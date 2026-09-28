-- Get Out, Sugar: Options.lua
-- The /trixie window: every warning with a switch and a Play button to hear
-- one of its lines, then mute and the sound channel.
--
-- Built from plain frames and textures, asking for a template only where a
-- missing one can be survived: which templates exist has changed across
-- these clients, and a missing one is a hard error at load.

local _, ns = ...

local window
local rows = {}
local controls = {}

local function Button(parent, width, text)
    local button
    local ok = pcall(function() button = CreateFrame("Button", nil, parent, "UIPanelButtonTemplate") end)
    if not (ok and button) then
        button = CreateFrame("Button", nil, parent)
        local bg = button:CreateTexture(nil, "BACKGROUND")
        bg:SetAllPoints()
        bg:SetColorTexture(0.30, 0.16, 0.26, 1)
        local hl = button:CreateTexture(nil, "HIGHLIGHT")
        hl:SetAllPoints()
        hl:SetColorTexture(1, 1, 1, 0.12)
    end
    button:SetSize(width, 22)
    local label = button:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    label:SetPoint("CENTER")
    label:SetText(text)
    button.labelText = label
    return button
end

local function Check(parent)
    local cb
    local ok = pcall(function() cb = CreateFrame("CheckButton", nil, parent, "UICheckButtonTemplate") end)
    if not (ok and cb) then
        cb = CreateFrame("CheckButton", nil, parent)
        cb:SetNormalTexture("Interface\\Buttons\\UI-CheckBox-Up")
        cb:SetPushedTexture("Interface\\Buttons\\UI-CheckBox-Down")
        cb:SetHighlightTexture("Interface\\Buttons\\UI-CheckBox-Highlight")
        cb:SetCheckedTexture("Interface\\Buttons\\UI-CheckBox-Check")
    end
    cb:SetSize(22, 22)
    return cb
end

local function Tip(frame, title, text)
    frame:HookScript("OnEnter", function(self)
        if not (GameTooltip and text) then return end
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:AddLine(title, 1, 0.82, 0)
        GameTooltip:AddLine(text, 1, 1, 1, true)
        GameTooltip:Show()
    end)
    frame:HookScript("OnLeave", function() if GameTooltip then GameTooltip:Hide() end end)
end

local CHANNELS = { "Dialog", "Master", "SFX", "Music", "Ambience" }

function ns.RefreshOptions()
    if not window then return end
    for _, row in ipairs(rows) do
        row.check:SetChecked(ns.IsOn(row.cat))
        local count = ns.COUNTS and ns.COUNTS[row.cat] or 0
        row.play:SetEnabled(count > 0)
    end
    controls.mute:SetChecked(ns.db.muted and true or false)
    controls.channel.labelText:SetText("Sound channel: " .. tostring(ns.db.channel))
end

local function Build()
    if window then return window end
    window = CreateFrame("Frame", "GetOutSugarOptions", UIParent)
    window:SetSize(580, 340)
    window:SetPoint("CENTER")
    window:SetFrameStrata("DIALOG")
    window:SetClampedToScreen(true)
    window:EnableMouse(true)
    window:SetMovable(true)
    window:RegisterForDrag("LeftButton")
    window:SetScript("OnDragStart", window.StartMoving)
    window:SetScript("OnDragStop", window.StopMovingOrSizing)
    local bg = window:CreateTexture(nil, "BACKGROUND")
    bg:SetAllPoints()
    bg:SetColorTexture(0.06, 0.04, 0.07, 0.95)
    local edges = {
        { "TOPLEFT", "TOPRIGHT", nil, 2 }, { "BOTTOMLEFT", "BOTTOMRIGHT", nil, 2 },
        { "TOPLEFT", "BOTTOMLEFT", 2, nil }, { "TOPRIGHT", "BOTTOMRIGHT", 2, nil },
    }
    for _, e in ipairs(edges) do
        local t = window:CreateTexture(nil, "BORDER")
        t:SetColorTexture(0.85, 0.35, 0.65, 0.9)
        t:SetPoint(e[1])
        t:SetPoint(e[2])
        if e[3] then t:SetWidth(e[3]) end
        if e[4] then t:SetHeight(e[4]) end
    end
    if type(UISpecialFrames) == "table" then tinsert(UISpecialFrames, "GetOutSugarOptions") end

    local title = window:CreateFontString(nil, "ARTWORK", "GameFontNormalLarge")
    title:SetPoint("TOPLEFT", 16, -14)
    title:SetText(ns.title)
    local close = Button(window, 24, "x")
    close:SetPoint("TOPRIGHT", -8, -8)
    close:SetScript("OnClick", function() window:Hide() end)

    local intro = window:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
    intro:SetPoint("TOPLEFT", 16, -38)
    intro:SetWidth(548)
    intro:SetJustifyH("LEFT")
    intro:SetText("Trixie yells when you are about to get hurt. Every warning starts off: "
        .. "tick the ones you want, and press Play to hear her.")
    window.intro = intro

    local function Column(x, header, prio)
        local h = window:CreateFontString(nil, "ARTWORK", "GameFontNormal")
        h:SetPoint("TOPLEFT", x, -70)
        h:SetText("|cffff7ac8" .. header .. "|r")
        local y = -92
        for _, entry in ipairs(ns.CATALOG) do
            if entry.prio == prio then
                local check = Check(window)
                check:SetPoint("TOPLEFT", x, y)
                local label = window:CreateFontString(nil, "ARTWORK", "GameFontHighlight")
                label:SetPoint("LEFT", check, "RIGHT", 2, 0)
                label:SetWidth(170)
                label:SetJustifyH("LEFT")
                pcall(label.SetWordWrap, label, false)
                label:SetText(entry.label)
                local play = Button(window, 44, "Play")
                play:SetPoint("TOPLEFT", x + 214, y)
                local cat = entry.cat
                check:SetScript("OnClick", function(self)
                    ns.SetOn(cat, self:GetChecked() and true or false)
                    ns.RefreshOptions()
                end)
                play:SetScript("OnClick", function() ns.Voice.Play(cat, { preview = true }) end)
                if entry.desc then Tip(check, entry.label, entry.desc) end
                rows[#rows + 1] = { cat = cat, check = check, play = play }
                y = y - 26
            end
        end
    end
    Column(16, "Danger", "danger")
    Column(300, "Moments", "situation")

    -- The bottom block.
    local mute = Check(window)
    mute:SetPoint("BOTTOMLEFT", 16, 50)
    local muteLabel = window:CreateFontString(nil, "ARTWORK", "GameFontHighlight")
    muteLabel:SetPoint("LEFT", mute, "RIGHT", 2, 0)
    muteLabel:SetText("Mute Trixie")
    mute:SetScript("OnClick", function(self)
        ns.db.muted = self:GetChecked() and true or false
        if ns.db.muted then ns.Voice.Stop() end
    end)
    controls.mute = mute

    local channel = Button(window, 180, "Sound channel")
    channel:SetPoint("BOTTOMLEFT", 300, 50)
    channel:SetScript("OnClick", function()
        local at = 1
        for i, name in ipairs(CHANNELS) do if name == ns.db.channel then at = i end end
        ns.db.channel = CHANNELS[at % #CHANNELS + 1]
        ns.RefreshOptions()
    end)
    Tip(channel, "Sound channel", "Which of the game's volume sliders controls her. Click to change.")
    controls.channel = channel

    local allOn = Button(window, 90, "All on")
    allOn:SetPoint("BOTTOMLEFT", 16, 16)
    allOn:SetScript("OnClick", function()
        for _, entry in ipairs(ns.CATALOG) do ns.db.warnings[entry.cat] = true end
        ns.Refresh()
        ns.RefreshOptions()
    end)
    local allOff = Button(window, 90, "All off")
    allOff:SetPoint("LEFT", allOn, "RIGHT", 8, 0)
    allOff:SetScript("OnClick", function()
        wipe(ns.db.warnings)
        ns.Refresh()
        ns.RefreshOptions()
    end)

    window:Hide()
    return window
end

-- `welcome`: opened by itself on a new install.
function ns.ShowOptions(welcome)
    Build()
    if welcome then
        window.intro:SetText("|cffffd100Welcome!|r Trixie yells when you are about to get hurt. "
            .. "Every warning starts off: tick the ones you want, and press Play to hear her. "
            .. "/trixie opens this again.")
    end
    ns.RefreshOptions()
    window:Show()
end

function ns.ToggleOptions()
    if window and window:IsShown() then window:Hide() else ns.ShowOptions() end
end
