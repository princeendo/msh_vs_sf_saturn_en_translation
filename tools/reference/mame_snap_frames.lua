-- MAME autoboot script: save snapshots at the frames in SNAP_FRAMES, then exit.
-- Example: SNAP_FRAMES="1200 3000" mame mshvsfu -autoboot_script this.lua ...
local targets = {}
for f in string.gmatch(os.getenv("SNAP_FRAMES") or "1800", "%d+") do targets[tonumber(f)] = true end
local last = 0
for f in pairs(targets) do if f > last then last = f end end
local screen = manager.machine.screens[":screen"]
emu.register_frame_done(function()
  local n = screen:frame_number()
  if targets[n] then
    screen:snapshot(string.format("%s_f%05d.png", emu.romname(), n))
  end
  if n >= last then manager.machine:exit() end
end)
