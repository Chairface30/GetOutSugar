-- Get Out, Sugar: Detect/Countdown.lua
-- A pull countdown starting: /pull, the countdown button on the raid frames,
-- or a boss mod's pull timer that runs through the game's own countdown.
--
-- Newer clients announce it as START_PLAYER_COUNTDOWN; older ones as
-- START_TIMER with the player-countdown type. Which one WoW Forever sends is
-- for the probe to say, so both are heard. When both arrive for one
-- countdown, the second finds her already saying it and is dropped.
--
-- With "Count the pull down" on she also counts it out loud, ten to one and
-- go, timed from the seconds left that the event carries. Her start line
-- runs two to four seconds, so on a timer too short for it to finish before
-- "ten" she skips it and only counts. Called off, the count stops.

local START_ROOM = 15     -- seconds left that leave room for the start line before "ten"

local _, ns = ...

-- START_TIMER's type for a player countdown, from the client's enum when it
-- has one (2 on the clients that do).
local function PlayerCountdownType()
    local enum = _G.Enum and _G.Enum.StartTimerType
    local value = enum and enum.PlayerCountdown
    return type(value) == "number" and value or 2
end

local function Started(remaining)
    remaining = ns.Readable(remaining) and tonumber(remaining) or nil
    if remaining and remaining <= 0 then
        ns.Voice.CancelCount()
        return
    end
    local counts = remaining and ns.IsOn("count")
    -- Announced twice (both events): the count is already running, and
    -- starting it again from the same seconds lands on the same beats.
    if not (counts and remaining < START_ROOM) then ns.Voice.Play("countdown") end
    if counts then ns.Voice.Count(remaining) end
end

function ns.OnCountdown(event, ...)
    if event == "START_PLAYER_COUNTDOWN" then
        local _, remaining = ...
        Started(remaining)
    elseif event == "START_TIMER" then
        local timerType, remaining = ...
        if ns.Readable(timerType) and timerType == PlayerCountdownType() then
            Started(remaining)
        end
    elseif event == "CANCEL_PLAYER_COUNTDOWN" then
        ns.Voice.CancelCount()
    elseif event == "STOP_TIMER_OF_TYPE" then
        local timerType = ...
        if ns.Readable(timerType) and timerType == PlayerCountdownType() then
            ns.Voice.CancelCount()
        end
    end
end

local listener = ns.Listener(function(event, ...)
    ns.OnCountdown(event, ...)
end)

ns.RegisterDetector("countdown", {
    cats = { "countdown", "count" },
    Enable = function()
        listener:Listen("START_PLAYER_COUNTDOWN")
        listener:Listen("START_TIMER")
        listener:Listen("CANCEL_PLAYER_COUNTDOWN")
        listener:Listen("STOP_TIMER_OF_TYPE")
    end,
    Disable = function()
        listener:Quiet()
        ns.Voice.CancelCount()
    end,
})
