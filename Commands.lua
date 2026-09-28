-- Get Out, Sugar: Commands.lua
-- /trixie and /gos.

local _, ns = ...

local function Help()
    ns.Print("commands:")
    print("  /trixie  -  open the options")
    print("  /trixie test <warning>  -  play one of its lines (/trixie test lists them)")
    print("  /trixie mute  -  mute or unmute her")
    print("  /trixie minimap  -  show or hide the minimap button")
    print("  /trixie status  -  which warnings are on and what is listening")
    print("  /trixie probe  -  start or stop recording what this client lets her see")
    print("  /trixie probe report  -  show what the probe recorded")
end

local function Status()
    local on = {}
    for _, entry in ipairs(ns.CATALOG) do
        if ns.IsOn(entry.cat) then on[#on + 1] = entry.cat end
    end
    ns.Print(#on == 0 and "every warning is off." or ("on: " .. table.concat(on, ", ")))
    local active = {}
    for _, d in ipairs(ns.detectors) do
        if d.active then active[#active + 1] = d.key end
        if d.broken then ns.Print("|cffff5555" .. d.key .. " failed:|r", d.broken) end
    end
    print("  listening: " .. (#active > 0 and table.concat(active, ", ") or "nothing"))
    print("  muted: " .. tostring(ns.db.muted) .. ", channel: " .. tostring(ns.db.channel)
        .. ", probe: " .. (ns.Probe.running and "running" or "off"))
end

local function Handler(input)
    local command, rest = tostring(input or ""):match("^%s*(%S*)%s*(.-)%s*$")
    command = (command or ""):lower()
    if command == "" or command == "options" or command == "config" then
        ns.ToggleOptions()
    elseif command == "test" then
        local cat = rest:lower()
        if ns.CATEGORY[cat] then
            if not ns.Voice.Play(cat, { preview = true }) then
                ns.Print("no clip played for " .. cat .. ".")
            end
        else
            local names = {}
            for _, entry in ipairs(ns.CATALOG) do names[#names + 1] = entry.cat end
            ns.Print("test one of: " .. table.concat(names, ", "))
        end
    elseif command == "mute" then
        ns.ToggleMute()
    elseif command == "minimap" then
        ns.SetMinimapShown(ns.db.minimap.hide and true or false)
        ns.Print(ns.db.minimap.hide and "minimap button hidden." or "minimap button shown.")
        ns.RefreshOptions()
    elseif command == "status" then
        Status()
    elseif command == "probe" then
        if rest == "report" then
            ns.Probe.Report()
        elseif rest == "clear" then
            ns.Probe.Clear()
            ns.Print("probe results cleared.")
        elseif ns.Probe.running then
            ns.Probe.Stop()
            ns.Print("probe stopped. /reload to write the results to the saved file.")
        else
            ns.Probe.Start()
            ns.Print("probe started. Fight something, take damage, get stunned, swim until the "
                .. "breath bar shows, then /trixie probe again and /reload.")
        end
    else
        Help()
    end
end

SLASH_GETOUTSUGAR1 = "/trixie"
SLASH_GETOUTSUGAR2 = "/gos"
SlashCmdList.GETOUTSUGAR = Handler
