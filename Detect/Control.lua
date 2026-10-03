-- Get Out, Sugar: Detect/Control.lua
-- Crowd control, by kind: the events behind the game's own loss-of-control
-- alert.
--
-- LOSS_OF_CONTROL_ADDED carries the unit and which of its effects is new;
-- C_LossOfControl says what kind that effect is (its locType). Each kind has
-- its own warning. A kind not listed, or one the client keeps secret, is
-- "other crowd control". An interrupt of your own cast is reported the same
-- way and is not crowd control, so it is skipped.

local _, ns = ...

ns.CC_KINDS = {
    STUN = "cc_stun", STUN_MECHANIC = "cc_stun",
    FEAR = "cc_fear", FEAR_MECHANIC = "cc_fear",
    CONFUSE = "cc_incap",
    CHARM = "cc_charm", POSSESS = "cc_charm",
    SILENCE = "cc_silence", PACIFYSILENCE = "cc_silence",
    ROOT = "cc_root",
    DISARM = "cc_disarm",
}
local SKIP = { SCHOOL_INTERRUPT = true }
local CATS = { "cc_stun", "cc_fear", "cc_incap", "cc_charm", "cc_silence", "cc_root", "cc_disarm", "cc" }

-- The effect's locType, or nil when it cannot be read.
local function Kind(unit, index)
    local api = _G.C_LossOfControl
    if type(api) ~= "table" or not index then return nil end
    local ok, data
    if unit and type(api.GetActiveLossOfControlDataByUnit) == "function" then
        ok, data = ns.Ask(api.GetActiveLossOfControlDataByUnit, unit, index)
    end
    if not (ok and type(data) == "table") then
        ok, data = ns.Ask(api.GetActiveLossOfControlData, index)
    end
    if ok and type(data) == "table" then
        local okT, kind = ns.Ask(function() return data.locType end)
        if okT and type(kind) == "string" then return kind end
    end
    return nil
end

-- Kinds that keep you from walking out of anything.
local HOLDS = {
    ROOT = true, STUN = true, STUN_MECHANIC = true, FEAR = true, FEAR_MECHANIC = true,
    CONFUSE = true, CHARM = true, POSSESS = true,
}

-- True while one of those is on you: "get out" is no use then. A root such as
-- Entangling Roots also ticks magic damage, which looks just like fire. An
-- effect whose kind the client keeps secret counts as one, since the warning
-- is the one that can do harm by being wrong.
function ns.HeldInPlace()
    local api = _G.C_LossOfControl
    if type(api) ~= "table" then return false end
    local byUnit = type(api.GetActiveLossOfControlDataByUnit) == "function"
    local okN, count
    if byUnit and type(api.GetActiveLossOfControlDataCountByUnit) == "function" then
        okN, count = ns.Ask(api.GetActiveLossOfControlDataCountByUnit, "player")
    end
    if not (okN and type(count) == "number") then
        okN, count = ns.Ask(api.GetActiveLossOfControlDataCount)
    end
    if not (okN and type(count) == "number") then count = 8 end   -- read until one is missing
    for i = 1, math.min(count, 8) do
        local okD, data
        if byUnit then okD, data = pcall(api.GetActiveLossOfControlDataByUnit, "player", i) end
        if not (okD and data ~= nil) then okD, data = pcall(api.GetActiveLossOfControlData, i) end
        if not okD or data == nil then break end
        local kind = Kind("player", i)
        if not kind or HOLDS[kind] then return true end
    end
    return false
end

function ns.OnLossOfControl(unit, index)
    local kind = Kind(unit, index)
    if kind and SKIP[kind] then return end
    ns.Voice.Play(kind and ns.CC_KINDS[kind] or "cc")
end

local listener = ns.Listener(function(event, unit, index)
    if event ~= "LOSS_OF_CONTROL_ADDED" then return end
    if not ns.Readable(unit, index) then unit, index = nil, nil end
    -- Older clients sent only the index.
    if type(unit) == "number" then unit, index = "player", unit end
    if unit and unit ~= "player" then return end
    ns.OnLossOfControl(unit or "player", tonumber(index))
end)

ns.RegisterDetector("control", {
    cats = CATS,
    Enable = function()
        if not listener:Listen("LOSS_OF_CONTROL_ADDED", "player") then
            ns.Print("|cffff5555the client refused the loss-of-control event.|r")
        end
    end,
    Disable = function() listener:Quiet() end,
})
