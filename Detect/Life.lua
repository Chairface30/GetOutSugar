-- Get Out, Sugar: Detect/Life.lua
-- The situational warnings: dying, worn-out gear, ready checks, and the
-- game's "out of range" family of errors.

local _, ns = ...

-------------------------------------------------------------------------------
-- Death, durability, ready checks
-------------------------------------------------------------------------------

local LOW_DURABILITY = 0.20
local gearLow = false

-- The lowest durability share across what you are wearing, or nil when
-- nothing reads.
function ns.LowestDurability()
    local lowest
    for slot = 1, 19 do
        local ok, current, maximum = ns.Ask(GetInventoryItemDurability, slot)
        current, maximum = tonumber(current), tonumber(maximum)
        if ok and current and maximum and maximum > 0 then
            local share = current / maximum
            if not lowest or share < lowest then lowest = share end
        end
    end
    return lowest
end

function ns.OnDurability()
    local lowest = ns.LowestDurability()
    if not lowest then return end
    local low = lowest <= LOW_DURABILITY
    -- Once as it crosses the line, not on every hit that follows.
    if low and not gearLow then ns.Voice.Play("durability") end
    gearLow = low
end

-- A ready check you started yourself needs no reminder.
local function MyName(name)
    if not ns.Readable(name) or type(name) ~= "string" then return false end
    local ok, first, second = ns.Ask(UnitName, "player")
    if not ok or not first then return false end
    local full = (second and second ~= "") and (first .. " " .. second) or first
    return name == first or name == full or name:find(full, 1, true) == 1
end

local lifeListener = ns.Listener(function(event, ...)
    if event == "PLAYER_DEAD" then
        ns.Voice.Play("death")
    elseif event == "UPDATE_INVENTORY_DURABILITY" then
        ns.OnDurability()
    elseif event == "READY_CHECK" then
        if not MyName((...)) then ns.Voice.Play("ready_check") end
    end
end)

ns.RegisterDetector("life", {
    cats = { "death", "durability", "ready_check" },
    Enable = function()
        lifeListener:Listen("PLAYER_DEAD")
        lifeListener:Listen("UPDATE_INVENTORY_DURABILITY")
        lifeListener:Listen("READY_CHECK")
        gearLow = (ns.LowestDurability() or 1) <= LOW_DURABILITY
    end,
    Disable = function() lifeListener:Quiet() end,
})

-------------------------------------------------------------------------------
-- Out of range, out of sight, facing the wrong way
-------------------------------------------------------------------------------
-- Matched against the game's own strings, so it works in any language.

local RANGE_ERRORS = {
    "ERR_OUT_OF_RANGE", "SPELL_FAILED_OUT_OF_RANGE", "SPELL_FAILED_LINE_OF_SIGHT",
    "SPELL_FAILED_UNIT_NOT_INFRONT", "ERR_BADATTACKFACING", "ERR_BADATTACKPOS",
    "SPELL_FAILED_TOO_CLOSE",
}

function ns.IsRangeError(message)
    if type(message) ~= "string" then return false end
    for _, key in ipairs(RANGE_ERRORS) do
        local text = _G[key]
        if type(text) == "string" and text ~= "" and message == text then return true end
    end
    return false
end

local errorListener = ns.Listener(function(_, _, message)
    if ns.Readable(message) and ns.IsRangeError(message) then ns.Voice.Play("range") end
end)

ns.RegisterDetector("errors", {
    cats = { "range" },
    Enable = function() errorListener:Listen("UI_ERROR_MESSAGE") end,
    Disable = function() errorListener:Quiet() end,
})
