-- Get Out, Sugar: Detect/Control.lua
-- Stunned, feared, silenced, rooted: the events behind the game's own
-- loss-of-control alert.
--
-- The alert's details (C_LossOfControl) say what kind it is. An interrupt of
-- your own cast is reported the same way and is not being crowd-controlled,
-- so it is skipped. If the details are secret or missing, any loss of control
-- counts.

local _, ns = ...

local SKIP = { SCHOOL_INTERRUPT = true }

local function Kind(index)
    local api = _G.C_LossOfControl
    if type(api) ~= "table" then return nil end
    local ok, data = ns.Ask(api.GetActiveLossOfControlData, index or 1)
    if ok and type(data) == "table" then
        local okT, kind = ns.Ask(function() return data.locType end)
        if okT and type(kind) == "string" then return kind end
    end
    return nil
end

function ns.OnLossOfControl(index)
    local kind = Kind(index)
    if kind and SKIP[kind] then return end
    ns.Voice.Play("cc")
end

local listener = ns.Listener(function(event, ...)
    if event == "LOSS_OF_CONTROL_ADDED" then
        local index = ...
        if not ns.Readable(index) then index = nil end
        ns.OnLossOfControl(tonumber(index))
    end
end)

ns.RegisterDetector("control", {
    cats = { "cc" },
    Enable = function()
        if not listener:Listen("LOSS_OF_CONTROL_ADDED") then
            ns.Print("|cffff5555the client refused the loss-of-control event.|r")
        end
    end,
    Disable = function() listener:Quiet() end,
})
