-- MAME autoboot script: replay a frame-timed input timeline, take snapshots, and
-- dump memory, then exit. The timeline path comes from MAME_TIMELINE.
--
-- Timeline lines (frame numbers are emulated screen frames; # starts a comment):
--   <frame> press <frames> <field name>   hold an input field, e.g. "P1 Button 1"
--   <frame> snap                          save <set>_f<frame>.png to the snap dir
--   <frame> dump <start> <end> <path>     write program-space bytes [start, end]
--   <frame> repeat <count> <every> <frames> <field name>
--                                         press <count> times, <every> frames apart
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
  local frame, verb, rest = line:match("^%s*(%d+)%s+(%a+)%s*(.-)%s*$")
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
    elseif verb == "exit" then
      add(frame, { kind = "exit" })
    else
      error("unknown timeline verb: " .. verb)
    end
  end
end

local screen = manager.machine.screens[":screen"]
local program = manager.machine.devices[":maincpu"].spaces["program"]

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
    elseif event.kind == "exit" then
      manager.machine:exit()
    end
  end
end)
