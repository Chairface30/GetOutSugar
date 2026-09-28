-- Get Out, Sugar: Detect/Breath.lua
-- Drowning and fatigue: the bars at the top of the screen.
--
-- Drowning warns twice: when the breath bar appears, and again once it is
-- under LOW of its length. Fatigue warns when its bar appears.

local _, ns = ...

local LOW = 0.30
local TICK = 0.5

local breath            -- { max, warnedLow } while the breath bar is up
local ticker

local function StopWatching()
    if ticker then ticker:Cancel() end
    ticker = nil
    breath = nil
end

function ns.BreathTick()
    if not breath then return end
    local ok, left = ns.Ask(GetMirrorTimerProgress, "BREATH")
    left = ok and tonumber(left) or nil
    if left and breath.max > 0 and not breath.warnedLow and left < breath.max * LOW then
        breath.warnedLow = true
        ns.Voice.Play("drowning", { again = true })
    end
end

function ns.OnMirrorStart(timer, value, maxValue)
    if timer == "BREATH" then
        ns.Voice.Play("drowning")
        breath = { max = tonumber(maxValue) or 0, warnedLow = false }
        if not ticker and C_Timer and C_Timer.NewTicker then
            ticker = C_Timer.NewTicker(TICK, function() pcall(ns.BreathTick) end)
        end
    elseif timer == "EXHAUSTION" then
        ns.Voice.Play("fatigue")
    end
end

local listener = ns.Listener(function(event, timer, value, maxValue)
    if not ns.Readable(timer, value, maxValue) then return end
    if event == "MIRROR_TIMER_START" then
        ns.OnMirrorStart(timer, value, maxValue)
    elseif event == "MIRROR_TIMER_STOP" and timer == "BREATH" then
        StopWatching()
    end
end)

ns.RegisterDetector("breath", {
    cats = { "drowning", "fatigue" },
    Enable = function()
        listener:Listen("MIRROR_TIMER_START")
        listener:Listen("MIRROR_TIMER_STOP")
    end,
    Disable = function()
        listener:Quiet()
        StopWatching()
    end,
})
