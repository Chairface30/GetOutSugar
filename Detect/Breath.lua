-- Get Out, Sugar: Detect/Breath.lua
-- Fatigue: the bar at the top of the screen when you swim too far out.

local _, ns = ...

local listener = ns.Listener(function(event, timer)
    if not ns.Readable(timer) then return end
    if timer == "EXHAUSTION" then ns.Voice.Play("fatigue") end
end)

ns.RegisterDetector("breath", {
    cats = { "fatigue" },
    Enable = function() listener:Listen("MIRROR_TIMER_START") end,
    Disable = function() listener:Quiet() end,
})
