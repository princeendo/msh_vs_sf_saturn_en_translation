-- MAME autoboot script: replay a frame-timed input timeline, take snapshots, and
-- dump memory, then exit. The timeline path comes from MAME_TIMELINE.
--
-- Timeline lines (frame numbers are emulated screen frames; # starts a comment):
--   <frame> press <frames> <field name>   hold an input field, e.g. "P1 Button 1"
--   <frame> snap                          save <set>_f<frame>.png to the snap dir
--   <frame> dump <start> <end> <path>     write program-space bytes [start, end]
--   <frame> share <tag> <path>            write a memory share, e.g. ":cps_a_regs"
--                                         (write-only registers read back as 0)
--   <frame> repeat <count> <every> <frames> <field name>
--                                         press <count> times, <every> frames apart
--   <frame> force16 <address> <value>     replace every CPU write to that word
--   <frame> unforce <address>             remove that replacement
--   <frame> logwrites <address> <path>    append "frame pc value" per CPU write
--   <frame> logreads <first> <last> <path>
--                                         append "frame pc offset" for CPU reads
--                                         of [first, last]: one line per change
--                                         of (frame, pc), at its first offset
--   <frame> debug <command>               run a MAME debugger command (needs -debug)
--   <frame> exit
-- Output paths are written as given; keep them under ignored local/ paths.

local path = os.getenv("MAME_TIMELINE")
if not path then error("MAME_TIMELINE is not set") end

local fields = {}
for _, port in pairs(manager.machine.ioport.ports) do
  for name, field in pairs(port.fields) do fields[name] = field end
end

local events = {}
local function add(frame, event)
  events[frame] = events[frame] or {}
  table.insert(events[frame], event)
end

for line in io.lines(path) do
  line = line:gsub("#.*$", "")
  local frame, verb, rest = line:match("^%s*(%d+)%s+(%w+)%s*(.-)%s*$")
  if frame then
    frame = tonumber(frame)
    if verb == "press" then
      local hold, name = rest:match("^(%d+)%s+(.+)$")
      if not fields[name] then error("unknown input field: " .. name) end
      add(frame, { kind = "down", name = name })
      add(frame + tonumber(hold), { kind = "up", name = name })
    elseif verb == "repeat" then
      local count, every, hold, name = rest:match("^(%d+)%s+(%d+)%s+(%d+)%s+(.+)$")
      if not fields[name] then error("unknown input field: " .. name) end
      for i = 0, tonumber(count) - 1 do
        local start = frame + i * tonumber(every)
        add(start, { kind = "down", name = name })
        add(start + tonumber(hold), { kind = "up", name = name })
      end
    elseif verb == "snap" then
      add(frame, { kind = "snap" })
    elseif verb == "dump" then
      local first, last, out = rest:match("^(%S+)%s+(%S+)%s+(%S+)$")
      add(frame, { kind = "dump", first = tonumber(first), last = tonumber(last), out = out })
    elseif verb == "share" then
      local tag, out = rest:match("^(%S+)%s+(%S+)$")
      add(frame, { kind = "share", tag = tag, out = out })
    elseif verb == "force16" then
      local address, value = rest:match("^(%S+)%s+(%S+)$")
      add(frame, { kind = "force", address = tonumber(address), value = tonumber(value) })
    elseif verb == "unforce" then
      add(frame, { kind = "unforce", address = tonumber(rest) })
    elseif verb == "logwrites" then
      local address, out = rest:match("^(%S+)%s+(%S+)$")
      add(frame, { kind = "log", address = tonumber(address), out = out })
    elseif verb == "logreads" then
      local first, last, out = rest:match("^(%S+)%s+(%S+)%s+(%S+)$")
      add(frame, { kind = "logreads", first = tonumber(first), last = tonumber(last), out = out })
    elseif verb == "debug" then
      add(frame, { kind = "debug", command = rest })
    elseif verb == "exit" then
      add(frame, { kind = "exit" })
    else
      error("unknown timeline verb: " .. verb)
    end
  end
end

local screen = manager.machine.screens[":screen"]
local program = manager.machine.devices[":maincpu"].spaces["program"]
local taps = {}

emu.register_frame_done(function()
  local frame = screen:frame_number()
  for _, event in ipairs(events[frame] or {}) do
    if event.kind == "down" then
      fields[event.name]:set_value(1)
    elseif event.kind == "up" then
      fields[event.name]:set_value(0)
    elseif event.kind == "snap" then
      screen:snapshot(string.format("%s_f%05d.png", emu.romname(), frame))
    elseif event.kind == "dump" then
      local out = assert(io.open(event.out, "wb"))
      out:write(program:read_range(event.first, event.last, 8))
      out:close()
    elseif event.kind == "share" then
      local share = assert(manager.machine.memory.shares[event.tag], "no share " .. event.tag)
      local bytes = {}
      for i = 0, share.size - 1 do bytes[#bytes + 1] = string.char(share:read_u8(i)) end
      local out = assert(io.open(event.out, "wb"))
      out:write(table.concat(bytes))
      out:close()
    elseif event.kind == "force" then
      local value = event.value
      taps[event.address] = program:install_write_tap(
        event.address, event.address + 1, "force" .. event.address,
        function(offset, data, mask) return value end)
    elseif event.kind == "log" then
      local out = assert(io.open(event.out, "a"))
      local cpu = manager.machine.devices[":maincpu"]
      taps["log" .. event.address] = program:install_write_tap(
        event.address, event.address + 1, "log" .. event.address,
        function(offset, data, mask)
          local pc = cpu.state["CURPC"] or cpu.state["PC"]
          out:write(string.format("%d %06x %04x %04x\n", screen:frame_number(), pc.value, data, mask))
          out:flush()
        end)
    elseif event.kind == "logreads" then
      local out = assert(io.open(event.out, "a"))
      local cpu = manager.machine.devices[":maincpu"]
      local last_key = nil
      taps["reads" .. event.first] = program:install_read_tap(
        event.first, event.last, "reads" .. event.first,
        function(offset, data, mask)
          local pc = (cpu.state["CURPC"] or cpu.state["PC"]).value
          local key = screen:frame_number() * 16777216 + pc
          if key ~= last_key then
            last_key = key
            out:write(string.format("%d %06x %06x\n", screen:frame_number(), pc, offset))
            out:flush()
          end
        end)
    elseif event.kind == "unforce" then
      if taps[event.address] then taps[event.address]:remove() end
      taps[event.address] = nil
    elseif event.kind == "debug" then
      manager.machine.debugger:command(event.command)
    elseif event.kind == "exit" then
      manager.machine:exit()
    end
  end
end)
