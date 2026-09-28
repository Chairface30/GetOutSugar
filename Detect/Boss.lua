-- Get Out, Sugar: Detect/Boss.lua
-- Boss warnings and boss fights.
--
-- A boss whispering you is how the game marks a player as a mechanic's
-- target. An emote is the big yellow text across the middle of the screen.
-- The message itself is never read, only that it came, so a secret message
-- still counts. Both arrive twice on some clients (the RAID_BOSS_ event and
-- its CHAT_MSG_ twin), and the warning's cooldown keeps that to one line.

local _, ns = ...

local EVENTS = {
    RAID_BOSS_WHISPER = "boss_you",
    CHAT_MSG_RAID_BOSS_WHISPER = "boss_you",
    RAID_BOSS_EMOTE = "boss_emote",
    CHAT_MSG_RAID_BOSS_EMOTE = "boss_emote",
    ENCOUNTER_START = "pull",
}

function ns.OnEncounterEnd(success)
    if not ns.Readable(success) then return end
    if success == 1 or success == true then
        ns.Voice.Play("kill")
    elseif success == 0 or success == false then
        ns.Voice.Play("wipe")
    end
end

local listener = ns.Listener(function(event, ...)
    if event == "ENCOUNTER_END" then
        ns.OnEncounterEnd(select(5, ...))
    elseif EVENTS[event] then
        ns.Voice.Play(EVENTS[event])
    end
end)

ns.RegisterDetector("boss", {
    cats = { "boss_you", "boss_emote", "pull", "wipe", "kill" },
    Enable = function()
        for event in pairs(EVENTS) do listener:Listen(event) end
        listener:Listen("ENCOUNTER_END")
    end,
    Disable = function() listener:Quiet() end,
})
