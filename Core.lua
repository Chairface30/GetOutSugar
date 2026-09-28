-- Get Out, Sugar: Core.lua
-- Settings, the detector registry, and the helpers every file shares.
--
-- Built for WoW Forever, where a lot of what an addon would read in combat is
-- secret or gone: there is no combat log, and health, power and auras are
-- secret. Every read of a client value goes through a pcall and an
-- issecretvalue check, and a detector that finds its signal unreadable stays
-- quiet rather than guessing.

local addonName, ns = ...
ns.addonName = addonName
ns.title = "Get Out, Sugar"

-- Every warning ships off: a new install says nothing until the player picks
-- what they want to hear.
local DEFAULTS = {
    warnings = {},        -- category -> true
    channel = "Dialog",   -- the sound channel her lines play on
    muted = false,
    seenWelcome = false,
}
ns.DEFAULTS = DEFAULTS

function ns.Print(...)
    local parts = { "|cffff7ac8Trixie|r:" }
    for i = 1, select("#", ...) do
        local value = (select(i, ...))
        local ok, text = pcall(function() return "" .. tostring(value) end)
        parts[#parts + 1] = ok and text or "<unreadable>"
    end
    print(table.concat(parts, " "))
end

-- A value the client keeps secret: only drawing widgets may take it, and
-- comparing or concatenating it throws.
function ns.Secret(value)
    local check = _G.issecretvalue
    if type(check) ~= "function" then return false end
    local ok, secret = pcall(check, value)
    return ok and secret and true or false
end

-- True when none of the values is secret.
function ns.Readable(...)
    for i = 1, select("#", ...) do
        if ns.Secret((select(i, ...))) then return false end
    end
    return true
end

-- A client call that may be missing, may throw, or may answer in secrets.
-- Gives back its results only when they are all readable.
function ns.Ask(fn, ...)
    if type(fn) ~= "function" then return false end
    local results = { pcall(fn, ...) }
    if not results[1] then return false end
    for i = 2, #results do
        if ns.Secret(results[i]) then return false end
    end
    return unpack(results)
end

-------------------------------------------------------------------------------
-- Settings
-------------------------------------------------------------------------------

function ns.LoadSettings()
    if type(GetOutSugarDB) ~= "table" then GetOutSugarDB = {} end
    local db = GetOutSugarDB
    for key, value in pairs(DEFAULTS) do
        if db[key] == nil then
            db[key] = type(value) == "table" and {} or value
        end
    end
    ns.db = db
    return db
end

function ns.IsOn(cat)
    return ns.db ~= nil and ns.db.warnings[cat] == true
end

function ns.SetOn(cat, on)
    ns.db.warnings[cat] = on and true or nil
    ns.Refresh()
end

-------------------------------------------------------------------------------
-- Detectors
-------------------------------------------------------------------------------
-- Each file in Detect/ registers one: the warnings it can raise, and Enable /
-- Disable. A detector is only switched on while one of its warnings is, so
-- nothing registers an event for a warning nobody wants.

ns.detectors = {}

function ns.RegisterDetector(key, def)
    def.key = key
    def.active = false
    ns.detectors[#ns.detectors + 1] = def
    return def
end

function ns.Refresh()
    if not ns.db then return end
    for _, detector in ipairs(ns.detectors) do
        local wanted = false
        for _, cat in ipairs(detector.cats) do
            if ns.IsOn(cat) then wanted = true end
        end
        if wanted ~= detector.active then
            local ok, err = pcall(wanted and detector.Enable or detector.Disable)
            if ok then
                detector.active = wanted
            else
                detector.broken = tostring(err)
                ns.Print("|cffff5555" .. detector.key .. " could not start:|r", err)
            end
        end
    end
end

-- A frame for a detector's events. Registering is done through a pcall, and
-- checked afterwards: some events are protected on this client, and one it
-- refuses is reported rather than silently never firing.
function ns.Listener(onEvent)
    local frame = CreateFrame("Frame")
    frame:SetScript("OnEvent", function(_, event, ...)
        local ok, err = pcall(onEvent, event, ...)
        if not ok then ns.Print("|cffff5555error in " .. event .. ":|r", err) end
    end)
    function frame:Listen(event, unit)
        local ok
        if unit and self.RegisterUnitEvent then
            ok = pcall(self.RegisterUnitEvent, self, event, unit)
        else
            ok = pcall(self.RegisterEvent, self, event)
        end
        local okR, registered = pcall(self.IsEventRegistered, self, event)
        return ok and not (okR and registered == false)
    end
    function frame:Quiet()
        pcall(self.UnregisterAllEvents, self)
    end
    return frame
end

-------------------------------------------------------------------------------
-- Boot
-------------------------------------------------------------------------------

local boot = CreateFrame("Frame")
boot:RegisterEvent("ADDON_LOADED")
boot:RegisterEvent("PLAYER_LOGIN")
boot:SetScript("OnEvent", function(_, event, arg1)
    if event == "ADDON_LOADED" and arg1 == addonName then
        ns.LoadSettings()
    elseif event == "PLAYER_LOGIN" then
        if not ns.db then ns.LoadSettings() end
        ns.Refresh()
        -- Once, on a new install: every warning is off, so show where they
        -- are switched on.
        if not ns.db.seenWelcome and ns.ShowOptions then
            ns.db.seenWelcome = true
            if C_Timer and C_Timer.After then
                C_Timer.After(3, function() ns.ShowOptions(true) end)
            end
        end
    end
end)
