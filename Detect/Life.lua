-- Get Out, Sugar: Detect/Life.lua
-- Dying, worn-out gear, and ready checks.

local _, ns = ...

-------------------------------------------------------------------------------
-- Death and durability
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

local lifeListener = ns.Listener(function(event)
    if event == "PLAYER_DEAD" then
        ns.Voice.Play("death")
    elseif event == "UPDATE_INVENTORY_DURABILITY" then
        ns.OnDurability()
    end
end)

ns.RegisterDetector("life", {
    cats = { "death", "durability" },
    Enable = function()
        lifeListener:Listen("PLAYER_DEAD")
        lifeListener:Listen("UPDATE_INVENTORY_DURABILITY")
        gearLow = (ns.LowestDurability() or 1) <= LOW_DURABILITY
    end,
    Disable = function() lifeListener:Quiet() end,
})

-------------------------------------------------------------------------------
-- Ready checks
-------------------------------------------------------------------------------
-- Trixie takes the place of the game's own ready check sound: while this
-- warning is on, that sound's file is muted, and she speaks instead. The game
-- plays it when the ready check window opens, which it does for everyone but
-- the player who started the check -- so she stays quiet for your own too.

ns.READY_CHECK_SOUND = 567409     -- sound/interface/readycheck.ogg

local muted = false

local function MuteGameSound(on)
    local fn = on and _G.MuteSoundFile or _G.UnmuteSoundFile
    if type(fn) ~= "function" then return false end
    local ok = pcall(fn, ns.READY_CHECK_SOUND)
    if ok then muted = on end
    return ok
end

local function MyName(name)
    if not ns.Readable(name) or type(name) ~= "string" then return false end
    local ok, first, second = ns.Ask(UnitName, "player")
    if not ok or not first then return false end
    local full = (second and second ~= "") and (first .. " " .. second) or first
    return name == first or name == full or name:find(full, 1, true) == 1
end

local readyListener = ns.Listener(function(event, initiator)
    if not MyName(initiator) then ns.Voice.Play("ready_check") end
end)

ns.RegisterDetector("readycheck", {
    cats = { "ready_check" },
    Enable = function()
        readyListener:Listen("READY_CHECK")
        MuteGameSound(true)
    end,
    Disable = function()
        readyListener:Quiet()
        if muted then MuteGameSound(false) end
    end,
})
