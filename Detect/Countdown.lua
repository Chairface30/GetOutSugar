-- Get Out, Sugar: Detect/Countdown.lua
-- A pull countdown starting: /pull, the countdown button on the raid frames,
-- or a boss mod's pull timer that runs through the game's own countdown.
--
-- Newer clients announce it as START_PLAYER_COUNTDOWN; older ones as
-- START_TIMER with the player-countdown type. Which one WoW Forever sends is
-- for the probe to say, so both are heard. When both arrive for one
-- countdown, the second finds her already saying it and is dropped.

local _, ns = ...

-- START_TIMER's type for a player countdown, from the client's enum when it
-- has one (2 on the clients that do).
local function PlayerCountdownType()
    local enum = _G.Enum and _G.Enum.StartTimerType
    local value = enum and enum.PlayerCountdown
    return type(value) == "number" and value or 2
end

function ns.OnCountdown(event, ...)
    if event == "START_PLAYER_COUNTDOWN" then
        ns.Voice.Play("countdown")
    elseif event == "START_TIMER" then
        local timerType = ...
        if ns.Readable(timerType) and timerType == PlayerCountdownType() then
            ns.Voice.Play("countdown")
        end
    end
end

local listener = ns.Listener(function(event, ...)
    ns.OnCountdown(event, ...)
end)

ns.RegisterDetector("countdown", {
    cats = { "countdown" },
    Enable = function()
        listener:Listen("START_PLAYER_COUNTDOWN")
        listener:Listen("START_TIMER")
    end,
    Disable = function() listener:Quiet() end,
})
