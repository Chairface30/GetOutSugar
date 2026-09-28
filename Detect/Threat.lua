-- Get Out, Sugar: Detect/Threat.lua
-- Aggro: you pulled it, you are about to, or (as the tank) one got away.
--
-- UnitDetailedThreatSituation("player", mob) is readable in combat on this
-- client (ChairAuras' probe, 2026-09-26): whether you are the mob's target,
-- and your threat as a percentage of what it takes to pull it. Every hostile
-- unit in reach is asked -- the target and each nameplate -- twice a second
-- while in combat, and a warning plays when a mob's answer changes.

local _, ns = ...
local Play = function(cat) return ns.Voice.Play(cat) end

local CLOSE_AT = 90     -- percent of the pull threshold: "about to pull"
local CLOSE_RESET = 80  -- below this a mob can warn "about to pull" again
local TICK = 0.5

local state = {}        -- mob key -> { tanking, close }
local ticker

local function Hostile(unit)
    local exists = select(2, ns.Ask(UnitExists, unit))
    if not exists then return false end
    return select(2, ns.Ask(UnitCanAttack, "player", unit)) and true or false
end

-- A mob seen as the target and as a nameplate is one mob: keyed by its GUID
-- when that is readable, by the unit token otherwise.
local function Key(unit)
    local ok, guid = ns.Ask(UnitGUID, unit)
    if ok and type(guid) == "string" then return guid end
    return unit
end

local function IsTank()
    local ok, role = ns.Ask(UnitGroupRolesAssigned, "player")
    return ok and role == "TANK"
end

local function InGroup()
    local ok, grouped = ns.Ask(IsInGroup)
    return ok and grouped and true or false
end

local function Units()
    local list = { "target" }
    for i = 1, 40 do list[#list + 1] = "nameplate" .. i end
    return list
end
local UNITS = Units()

function ns.ThreatCheck()
    local tank, group = IsTank(), InGroup()
    local seen = {}
    for _, unit in ipairs(UNITS) do
        if Hostile(unit) then
            local key = Key(unit)
            if not seen[key] then
                seen[key] = true
                local ok, tanking, _, pct = ns.Ask(UnitDetailedThreatSituation, "player", unit)
                if ok then
                    tanking = tanking and true or false
                    pct = tonumber(pct)
                    local s = state[key]
                    if not s then s = {}; state[key] = s end
                    if tank then
                        -- The tank losing a mob only matters with a group
                        -- for it to go and eat.
                        if group and s.tanking and not tanking then
                            local okD, dead = ns.Ask(UnitIsDead, unit)
                            if not (okD and dead) then Play("tank_lost") end
                        end
                    elseif group or ns.db.aggroSolo then
                        -- Solo, every mob you fight is on you: that is not news.
                        -- A mob already on you when first seen counts too: a
                        -- patrol that runs straight at the healer.
                        if tanking and not s.tanking then
                            Play("aggro")
                        elseif not tanking and pct and pct >= CLOSE_AT and not s.close then
                            s.close = true
                            Play("aggro_close")
                        end
                    end
                    if pct and pct < CLOSE_RESET then s.close = false end
                    s.tanking = tanking
                end
            end
        end
    end
    for key in pairs(state) do
        if not seen[key] then state[key] = nil end
    end
end

local function Start()
    if ticker then return end
    wipe(state)
    ticker = C_Timer.NewTicker(TICK, function()
        local ok, err = pcall(ns.ThreatCheck)
        if not ok then ns.Print("|cffff5555threat check:|r", err) end
    end)
end

local function Stop()
    if ticker then ticker:Cancel() end
    ticker = nil
    wipe(state)
end

local listener = ns.Listener(function(event)
    if event == "PLAYER_REGEN_DISABLED" then Start() else Stop() end
end)

ns.RegisterDetector("threat", {
    cats = { "aggro", "aggro_close", "tank_lost" },
    Enable = function()
        listener:Listen("PLAYER_REGEN_DISABLED")
        listener:Listen("PLAYER_REGEN_ENABLED")
        if select(2, ns.Ask(UnitAffectingCombat, "player")) then Start() end
    end,
    Disable = function()
        listener:Quiet()
        Stop()
    end,
})
ns.threatState = state
