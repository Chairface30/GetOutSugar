-- Get Out, Sugar: Detect/Damage.lua
-- Standing in something, from the damage you take.
--
-- There is no combat log on this client, so nothing says which spell hit you.
-- What UNIT_COMBAT may still carry, for the player, is each hit's amount and
-- school -- the same feed the floating combat text is drawn from. Standing in
-- fire looks like several magic-school hits in quick succession, so that is
-- what is counted. It cannot tell a puddle from a damage-over-time spell.
--
-- Whether UNIT_COMBAT is readable here is for the probe to say. If its
-- values come back secret, this detector says so once and stays quiet.

local _, ns = ...

local WINDOW = 3        -- seconds
local TICKS = 3         -- magic hits within WINDOW that count as "in something"

local recent = {}
local warnedSecret = false

local function Magic(school)
    school = tonumber(school)
    if not school or school == 0 then return false end
    return school % 2 == 0      -- the physical bit is clear
end

function ns.OnDamage(action, amount, school)
    if action ~= "WOUND" then return end
    amount = tonumber(amount)
    if not amount or amount <= 0 or not Magic(school) then return end
    local now = GetTime()
    recent[#recent + 1] = now
    local keep = {}
    for _, t in ipairs(recent) do
        if now - t <= WINDOW then keep[#keep + 1] = t end
    end
    recent = keep
    if #recent >= TICKS then
        recent = {}
        ns.Voice.Play("fire")
    end
end

local listener = ns.Listener(function(event, unit, action, descriptor, amount, school)
    if unit ~= "player" then return end
    if not ns.Readable(action, amount, school) then
        if not warnedSecret then
            warnedSecret = true
            ns.Print("this client keeps the damage you take secret, so the "
                .. "\"standing in something\" warning cannot work here.")
        end
        return
    end
    ns.OnDamage(action, amount, school)
end)

ns.RegisterDetector("damage", {
    cats = { "fire" },
    Enable = function()
        recent = {}
        if not listener:Listen("UNIT_COMBAT", "player") then
            ns.Print("|cffff5555the client refused the damage event|r (UNIT_COMBAT).")
        end
    end,
    Disable = function()
        listener:Quiet()
        recent = {}
    end,
})
