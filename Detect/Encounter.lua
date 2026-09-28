-- Get Out, Sugar: Detect/Encounter.lua
-- Boss fights: the pull, and how it ended.

local _, ns = ...

function ns.OnEncounterEnd(success)
    if not ns.Readable(success) then return end
    if success == 1 or success == true then
        ns.Voice.Play("kill")
    elseif success == 0 or success == false then
        ns.Voice.Play("wipe")
    end
end

local listener = ns.Listener(function(event, ...)
    if event == "ENCOUNTER_START" then
        ns.Voice.Play("pull")
    elseif event == "ENCOUNTER_END" then
        ns.OnEncounterEnd(select(5, ...))
    end
end)

ns.RegisterDetector("encounter", {
    cats = { "pull", "wipe", "kill" },
    Enable = function()
        listener:Listen("ENCOUNTER_START")
        listener:Listen("ENCOUNTER_END")
    end,
    Disable = function() listener:Quiet() end,
})
