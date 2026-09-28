-- Get Out, Sugar: Minimap.lua
-- The minimap button: the standard LibDBIcon one, wearing Trixie's face.
-- Left-click opens the options, right-click mutes or unmutes her. It also
-- works as a launcher in any bar addon that shows LibDataBroker launchers.

local _, ns = ...

ns.ICON = "Interface\\AddOns\\" .. ns.addonName .. "\\Textures\\trixie"
local NAME = "GetOutSugar"

local function Libs()
    local stub = _G.LibStub
    if not stub then return nil end
    return stub("LibDataBroker-1.1", true), stub("LibDBIcon-1.0", true)
end

local function Tooltip(tip)
    tip:AddLine(ns.title, 1, 0.48, 0.78)
    local on = 0
    for _, entry in ipairs(ns.CATALOG) do
        if ns.IsOn(entry.cat) then on = on + 1 end
    end
    if on == 0 then
        tip:AddLine("Every warning is off.", 1, 1, 1)
    else
        tip:AddLine(on .. " of " .. #ns.CATALOG .. " warnings on.", 1, 1, 1)
    end
    if ns.db.muted then tip:AddLine("Muted.", 1, 0.3, 0.3) end
    tip:AddLine(" ")
    tip:AddLine("Click: options", 0.7, 0.7, 0.7)
    tip:AddLine("Right-click: " .. (ns.db.muted and "unmute" or "mute"), 0.7, 0.7, 0.7)
end

function ns.ToggleMute()
    ns.db.muted = not ns.db.muted
    if ns.db.muted then ns.Voice.Stop() end
    ns.Print(ns.db.muted and "muted." or "unmuted.")
    if ns.RefreshOptions then ns.RefreshOptions() end
end

function ns.SetupMinimap()
    local ldb, icon = Libs()
    if not (ldb and icon) or ns.launcher then return end
    ns.launcher = ldb:NewDataObject(NAME, {
        type = "launcher",
        text = ns.title,
        icon = ns.ICON,
        OnClick = function(_, button)
            if button == "RightButton" then ns.ToggleMute() else ns.ToggleOptions() end
        end,
        OnTooltipShow = Tooltip,
    })
    icon:Register(NAME, ns.launcher, ns.db.minimap)
end

function ns.SetMinimapShown(shown)
    ns.db.minimap.hide = not shown
    local _, icon = Libs()
    if icon and icon:IsRegistered(NAME) then
        if shown then icon:Show(NAME) else icon:Hide(NAME) end
    end
end
