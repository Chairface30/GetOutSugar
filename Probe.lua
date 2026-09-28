-- Get Out, Sugar: Probe.lua
-- /trixie probe: what this client lets the warnings see.
--
-- Listens to every event a warning could use and records, out of combat and
-- in combat separately, how often each fired and what one looked like, with
-- any secret value marked SECRET. It also asks the APIs the detectors lean
-- on. Everything lands in GetOutSugarDB.probe, which the client writes to the
-- saved file on logout or /reload -- that file is what gets read afterwards.
--
-- Nothing is registered until the probe is started: registering some events
-- is protected on this client, and a refused one is recorded as refused.

local _, ns = ...
local Probe = {}
ns.Probe = Probe

local EVENTS = {
    "UNIT_COMBAT", "COMBAT_TEXT_UPDATE", "LOSS_OF_CONTROL_ADDED", "LOSS_OF_CONTROL_UPDATE",
    "PLAYER_CONTROL_LOST", "MIRROR_TIMER_START", "MIRROR_TIMER_STOP", "PLAYER_DEAD",
    "ENCOUNTER_START", "ENCOUNTER_END", "UPDATE_INVENTORY_DURABILITY", "READY_CHECK",
    "PLAYER_REGEN_DISABLED", "PLAYER_REGEN_ENABLED",
}

local function Describe(value)
    if ns.Secret(value) then return "SECRET" end
    local kind = type(value)
    if kind == "table" then
        local parts = {}
        for k, v in pairs(value) do
            if #parts >= 8 then parts[#parts + 1] = "..." break end
            parts[#parts + 1] = tostring(k) .. "=" .. Describe(v)
        end
        return "{" .. table.concat(parts, " ") .. "}"
    elseif kind == "string" then
        return '"' .. value:sub(1, 60) .. '"'
    end
    return tostring(value)
end

local function DescribeAll(...)
    local parts = {}
    for i = 1, math.min(select("#", ...), 8) do
        parts[#parts + 1] = Describe((select(i, ...)))
    end
    return table.concat(parts, ", ")
end

local function State()
    local ok, fighting = ns.Ask(UnitAffectingCombat, "player")
    return (ok and fighting) and "combat" or "calm"
end

local function DB()
    local db = ns.db
    db.probe = db.probe or {}
    local p = db.probe
    p.events = p.events or {}
    p.apis = p.apis or {}
    p.refused = p.refused or {}
    return p
end

local function Exists(path)
    local node = _G
    for part in path:gmatch("[^%.]+") do
        if type(node) ~= "table" then return false end
        node = node[part]
    end
    return node ~= nil
end

-- One answer for an API, as "missing", "error: ...", or its results.
local function Try(path, ...)
    if not Exists(path) then return "missing" end
    local node = _G
    for part in path:gmatch("[^%.]+") do node = node[part] end
    local results = { pcall(node, ...) }
    if not results[1] then return "error: " .. tostring(results[2]):sub(1, 120) end
    return "yes: " .. DescribeAll(select(2, unpack(results)))
end

function Probe.CheckAPIs()
    local p, state = DB(), State()
    local out = {}
    out["GetMirrorTimerProgress(BREATH)"] = Try("GetMirrorTimerProgress", "BREATH")
    out["GetMirrorTimerInfo(1)"] = Try("GetMirrorTimerInfo", 1)
    out["C_LossOfControl.GetActiveLossOfControlDataCount"] = Try("C_LossOfControl.GetActiveLossOfControlDataCount")
    out["C_LossOfControl.GetActiveLossOfControlData(1)"] = Try("C_LossOfControl.GetActiveLossOfControlData", 1)
    out["GetCurrentCombatTextEventInfo"] = Try("GetCurrentCombatTextEventInfo")
    out["GetInventoryItemDurability(5)"] = Try("GetInventoryItemDurability", 5)
    out["MuteSoundFile / UnmuteSoundFile"] = (Exists("MuteSoundFile") and "exists" or "missing")
        .. " / " .. (Exists("UnmuteSoundFile") and "exists" or "missing")
    out["C_Sound.IsPlaying"] = Exists("C_Sound.IsPlaying") and "exists" or "missing"
    out["CombatLogGetCurrentEventInfo"] = Exists("CombatLogGetCurrentEventInfo") and "exists" or "missing"
    out["issecretvalue"] = Exists("issecretvalue") and "exists" or "missing"
    p.apis[state] = out
    p.when = date and date("%Y-%m-%d %H:%M") or "?"
end

local listener = CreateFrame("Frame")
listener:SetScript("OnEvent", function(_, event, ...)
    local p = DB()
    local entry = p.events[event]
    if not entry then entry = { count = 0 }; p.events[event] = entry end
    entry.count = entry.count + 1
    local state = State()
    -- The first of each in each state, and the latest, which is often the
    -- more telling one (the tenth UNIT_COMBAT, not the first).
    local sample = DescribeAll(...)
    entry[state] = entry[state] or sample
    entry[state .. "Latest"] = sample
    if event == "COMBAT_TEXT_UPDATE" then
        entry.info = Try("GetCurrentCombatTextEventInfo")
    end
    -- Ask the APIs once in combat too: many answer differently there.
    if event == "PLAYER_REGEN_DISABLED" and C_Timer and C_Timer.After then
        C_Timer.After(2, function() pcall(Probe.CheckAPIs) end)
    end
end)

Probe.running = false

function Probe.Start()
    if Probe.running then return end
    Probe.running = true
    local p = DB()
    for _, event in ipairs(EVENTS) do
        local ok = pcall(listener.RegisterEvent, listener, event)
        local okR, registered = pcall(listener.IsEventRegistered, listener, event)
        if not ok or (okR and registered == false) then p.refused[event] = true end
    end
    pcall(Probe.CheckAPIs)
end

function Probe.Stop()
    Probe.running = false
    pcall(listener.UnregisterAllEvents, listener)
end

function Probe.Report()
    local p = DB()
    local names = {}
    for event in pairs(p.events) do names[#names + 1] = event end
    table.sort(names)
    ns.Print("probe: " .. #names .. " event(s) seen.")
    for _, event in ipairs(names) do
        local e = p.events[event]
        print(string.format("  %s x%d  calm: %s  combat: %s", event, e.count,
            e.calm or "-", e.combatLatest or e.combat or "-"))
    end
    local refused = {}
    for event in pairs(p.refused) do refused[#refused + 1] = event end
    if #refused > 0 then
        table.sort(refused)
        print("  refused: " .. table.concat(refused, ", "))
    end
end

function Probe.Clear()
    ns.db.probe = nil
end
