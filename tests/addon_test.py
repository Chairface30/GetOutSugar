# Get Out, Sugar in a stand-in client (needs: pip install lupa)
#   python tests/addon_test.py
#
# The harness is kinder than the client: it proves the logic, not that the
# client will hand these values over. That is what /trixie probe is for.
import io, os, re, sys
from lupa import lua51

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import lines

failures = []


def check(name, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        failures.append(name)


HARNESS = r'''
NOW = 100
function GetTime() return NOW end
SECRET = setmetatable({}, { __tostring = function() return "SECRET" end })
function issecretvalue(v) return v == SECRET end
PLAYED, STOPPED = {}, {}
local handle = 0
FILES_MISSING = {}
function PlaySoundFile(path, channel)
    if FILES_MISSING[path] then return false end
    handle = handle + 1
    table.insert(PLAYED, { path = path, channel = channel, handle = handle })
    return true, handle
end
function StopSound(h) table.insert(STOPPED, h) end
PRINTED = {}
function print(...) local t = {} for i = 1, select("#", ...) do t[#t+1] = tostring((select(i, ...))) end table.insert(PRINTED, table.concat(t, " ")) end
function wipe(t) for k in pairs(t) do t[k] = nil end return t end
tinsert = table.insert
unpack = unpack or table.unpack
function date() return "2026-09-28 12:00" end
UISpecialFrames = {}
SlashCmdList = {}

-- Frames: every method not listed does nothing and returns nothing.
FRAMES = {}
local function Widget(kind)
    local w = { _events = {}, _scripts = {}, _kind = kind }
    return setmetatable(w, { __index = function(self, key)
        if key == "RegisterEvent" then return function(s, e)
            if REFUSED and REFUSED[e] then error("forbidden") end
            s._events[e] = true end
        elseif key == "RegisterUnitEvent" then return function(s, e, u)
            if REFUSED and REFUSED[e] then error("forbidden") end
            s._events[e] = u or true end
        elseif key == "UnregisterAllEvents" then return function(s) s._events = {} end
        elseif key == "IsEventRegistered" then return function(s, e) return s._events[e] ~= nil end
        elseif key == "SetScript" then return function(s, n, f) s._scripts[n] = f end
        elseif key == "HookScript" then return function(s, n, f) s._scripts[n] = f end
        elseif key == "CreateTexture" or key == "CreateFontString" then return function() return Widget("region") end
        elseif key == "SetText" then return function(s, t) rawset(s, "_text", t) end
        elseif key == "SetChecked" then return function(s, v) rawset(s, "_checked", v) end
        elseif key == "GetChecked" then return function(s) return rawget(s, "_checked") end
        elseif key == "Show" then return function(s) rawset(s, "_shown", true) end
        elseif key == "Hide" then return function(s) rawset(s, "_shown", false) end
        elseif key == "IsShown" then return function(s) return rawget(s, "_shown") == true end
        end
        return function() end
    end })
end
function CreateFrame(kind, name, parent, template)
    local f = Widget(kind)
    rawset(f, "_shown", true)
    table.insert(FRAMES, f)
    if name then _G[name] = f end
    return f
end
UIParent = CreateFrame("Frame")

function FIRE(event, ...)
    for _, f in ipairs(FRAMES) do
        local reg = f._events[event]
        if reg and (reg == true or reg == (...)) and f._scripts.OnEvent then f._scripts.OnEvent(f, event, ...) end
    end
end

-- Timers run only when told to.
TIMERS = {}
C_Timer = {
    After = function(d, fn) table.insert(TIMERS, fn) end,
    NewTicker = function(d, fn)
        local t = { fn = fn, cancelled = false }
        function t:Cancel() self.cancelled = true end
        table.insert(TIMERS, t)
        return t
    end,
}
function TICK()
    for _, t in ipairs(TIMERS) do
        if type(t) == "table" and not t.cancelled then t.fn() end
    end
end

-- Units
UNITS = {}          -- token -> { exists, hostile, guid, dead, threat = { tanking, status, pct } }
ROLE, GROUPED, FIGHTING = "DAMAGER", true, false
MAXHP = 1000
function UnitExists(u) return UNITS[u] ~= nil end
function UnitCanAttack(a, u) return UNITS[u] and UNITS[u].hostile or false end
function UnitGUID(u) return UNITS[u] and UNITS[u].guid end
function UnitIsDead(u) return UNITS[u] and UNITS[u].dead or false end
function UnitDetailedThreatSituation(p, u)
    local t = UNITS[u] and UNITS[u].threat
    if not t then return nil end
    if t == SECRET then return SECRET, SECRET, SECRET, SECRET, SECRET end
    return t[1], t[2], t[3], t[3], 0
end
function UnitGroupRolesAssigned() return ROLE end
function IsInGroup() return GROUPED end
function UnitAffectingCombat() return FIGHTING end
function UnitHealthMax() return MAXHP end
function UnitName() return "Chairface", "Chippendale" end
BREATH_LEFT = 60000
function GetMirrorTimerProgress() return BREATH_LEFT end
DURABILITY = {}
function GetInventoryItemDurability(slot) local d = DURABILITY[slot] if d then return d[1], d[2] end end
LOC = { locType = "STUN" }
C_LossOfControl = { GetActiveLossOfControlData = function() return LOC end }
ERR_OUT_OF_RANGE = "Out of range."
SPELL_FAILED_LINE_OF_SIGHT = "Target not in line of sight"

math.randomseed(1)
'''

TOC = [l.strip() for l in io.open("GetOutSugar.toc", encoding="utf-8") if l.strip() and not l.startswith("#")]


def boot(setup=""):
    rt = lua51.LuaRuntime(unpack_returned_tuples=True)
    rt.execute(HARNESS)
    rt.execute(setup)
    rt.execute("NS = {}")
    load = rt.eval("function(src, name) local f, e = loadstring(src, name) if not f then error(e) end f('GetOutSugar', NS) end")
    for f in TOC:
        load(io.open(f.replace("\\", "/"), encoding="utf-8").read(), "@" + f)
    rt.execute('FIRE("ADDON_LOADED", "GetOutSugar") FIRE("PLAYER_LOGIN")')
    return rt


def played(rt):
    return [rt.eval(f"PLAYED[{i}].path") for i in range(1, rt.eval("#PLAYED") + 1)]


def cats_played(rt):
    return [re.sub(r"\d+\.ogg$", "", p.split("gos_")[-1]) for p in played(rt)]


# --------------------------------------------------------------------------
print("The lines, the catalog and the clips agree")
catalog = boot().eval("(function() local t = {} for _, e in ipairs(NS.CATALOG) do t[#t+1] = e.cat end return table.concat(t, ',') end)()").split(",")
check("every warning in the catalog has lines", set(catalog) == set(lines.POOLS), set(catalog) ^ set(lines.POOLS))
check("about twenty lines each", all(len(v) >= 18 for v in lines.POOLS.values()))
disk = lines.counts_on_disk()
counts_lua = dict(re.findall(r"(\w+) = (\d+),", io.open("Counts.lua", encoding="utf-8").read()))
check("Counts.lua matches the clips on disk", all(int(counts_lua.get(c, -1)) == n for c, n in disk.items()), counts_lua)
check("every line has its clip", all(disk[c] == len(v) for c, v in lines.POOLS.items()), disk)

# --------------------------------------------------------------------------
print("A new install")
rt = boot()
check("every warning starts off", rt.eval("next(NS.db.warnings) == nil") is True)
check("nothing is listening", rt.eval("(function() for _, d in ipairs(NS.detectors) do if d.active then return false end end return true end)()") is True)
rt.execute("UNITS.target = { hostile = true, guid = 'mob1', threat = { true, 3, 100 } } FIGHTING = true FIRE('PLAYER_REGEN_DISABLED') TICK()")
check("so nothing plays", rt.eval("#PLAYED") == 0)
check("the options open by themselves, once", rt.eval("NS.db.seenWelcome") is True)

# --------------------------------------------------------------------------
print("The voice")
rt = boot("GetOutSugarDB = { warnings = { fire = true, death = true, kill = true }, seenWelcome = true }")
rt.execute("NS.Voice.Play('death')")
check("a line plays from the warning's clips", cats_played(rt) == ["death"], played(rt))
check("on the chosen channel", rt.eval("PLAYED[1].channel") == "Dialog")
rt.execute("NOW = NOW + 1 NS.Voice.Play('fire')")
check("a danger line cuts off a situational one", cats_played(rt) == ["death", "fire"] and rt.eval("STOPPED[1]") == 1)
rt.execute("NOW = NOW + 1 NS.Voice.Play('kill')")
check("a situational one does not cut off danger", cats_played(rt) == ["death", "fire"])
rt.execute("NOW = NOW + 10 NS.Voice.Play('fire')")
check("once the line is over, the next plays", cats_played(rt)[-1] == "fire" and len(played(rt)) == 3)
rt.execute("NOW = NOW + 1 NS.Voice.Play('fire')")
check("the same warning waits out its cooldown", len(played(rt)) == 3)
rt.execute("NOW = NOW + 7 NS.Voice.Play('fire')")
check("then plays again", len(played(rt)) == 4)
check("never the same clip twice running", played(rt)[-1] != played(rt)[-2])
rt.execute("NOW = NOW + 20 NS.Voice.Play('pull')")
check("a warning that is off stays quiet", len(played(rt)) == 4)
rt.execute("NS.Voice.Play('pull', { preview = true })")
check("but its Play button still plays it", cats_played(rt)[-1] == "pull")
rt.execute("NOW = NOW + 20 NS.db.muted = true NS.Voice.Play('death')")
check("muted, nothing plays", cats_played(rt)[-1] == "pull")
rt.execute("NOW = NOW + 20 NS.db.muted = false NS.db.chatty = 3 NS.Voice.Play('death') NOW = NOW + 15 NS.Voice.Play('death')")
check("quieter setting stretches the cooldown", cats_played(rt).count("death") == 2, cats_played(rt))

# --------------------------------------------------------------------------
print("Aggro")
rt = boot("GetOutSugarDB = { warnings = { aggro = true, aggro_close = true, tank_lost = true }, seenWelcome = true }")
check("the threat detector is listening", rt.eval("NS.detectors[1].active") is True)
rt.execute("""
UNITS.target = { hostile = true, guid = 'mob1', threat = { false, 1, 40 } }
UNITS.nameplate1 = { hostile = true, guid = 'mob1', threat = { false, 1, 40 } }
FIGHTING = true FIRE('PLAYER_REGEN_DISABLED') TICK()
""")
check("a mob on the tank says nothing", rt.eval("#PLAYED") == 0)
rt.execute("NOW = NOW + 1 UNITS.target.threat = { false, 1, 92 } UNITS.nameplate1.threat = UNITS.target.threat TICK()")
check("at 90% of the pull: about to pull it", cats_played(rt) == ["aggro_close"])
rt.execute("NOW = NOW + 1 TICK()")
check("once, not every half second", cats_played(rt) == ["aggro_close"])
rt.execute("NOW = NOW + 5 UNITS.target.threat = { true, 3, 100 } UNITS.nameplate1.threat = UNITS.target.threat TICK()")
check("it turns on you: you pulled it", cats_played(rt) == ["aggro_close", "aggro"])
check("the target and its nameplate are one mob", len(played(rt)) == 2)
rt.execute("NOW = NOW + 10 UNITS.nameplate2 = { hostile = true, guid = 'mob2', threat = { true, 3, 100 } } TICK()")
check("a mob already on you when first seen counts", cats_played(rt)[-1] == "aggro")
rt.execute("NOW = NOW + 10 UNITS.nameplate3 = { hostile = true, guid = 'mob3', threat = SECRET } TICK()")
check("a mob whose threat is secret is passed over", len(played(rt)) == 3)
rt.execute("NOW = NOW + 10 GROUPED = false UNITS.nameplate4 = { hostile = true, guid = 'mob4', threat = { true, 3, 100 } } TICK()")
check("solo, a mob on you is not news", len(played(rt)) == 3)
rt.execute("NOW = NOW + 10 NS.db.aggroSolo = true UNITS.nameplate5 = { hostile = true, guid = 'mob5', threat = { true, 3, 100 } } TICK()")
check("unless aggro warnings when solo is ticked", len(played(rt)) == 4)

rt = boot("GetOutSugarDB = { warnings = { tank_lost = true }, seenWelcome = true } ROLE = 'TANK'")
rt.execute("UNITS.target = { hostile = true, guid = 'mob1', threat = { true, 3, 100 } } FIGHTING = true FIRE('PLAYER_REGEN_DISABLED') TICK()")
rt.execute("NOW = NOW + 1 UNITS.target.threat = { false, 1, 60 } TICK()")
check("tank: a mob turning away warns", cats_played(rt) == ["tank_lost"])
rt.execute("NOW = NOW + 10 UNITS.target.threat = { true, 3, 100 } TICK() NOW = NOW + 10 UNITS.target.dead = true UNITS.target.threat = { false, 0, 0 } TICK()")
check("but not one that died", cats_played(rt) == ["tank_lost"])
rt.execute("FIGHTING = false FIRE('PLAYER_REGEN_ENABLED')")
check("out of combat the checks stop", rt.eval("(function() for _, t in ipairs(TIMERS) do if type(t) == 'table' and not t.cancelled then return false end end return true end)()") is True)

# --------------------------------------------------------------------------
print("Damage")
rt = boot("GetOutSugarDB = { warnings = { fire = true, big_hit = true }, seenWelcome = true }")
rt.execute("FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4) NOW = NOW + 1 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4)")
check("two fire ticks are not yet standing in it", rt.eval("#PLAYED") == 0)
rt.execute("NOW = NOW + 1 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4)")
check("three in three seconds are", cats_played(rt) == ["fire"])
rt.execute("NOW = NOW + 20 for i = 1, 5 do FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 1) NOW = NOW + 0.5 end")
check("physical hits are not fire", cats_played(rt) == ["fire"])
rt.execute("NOW = NOW + 20 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4) NOW = NOW + 4 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4) NOW = NOW + 4 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4)")
check("ticks spread past the window are not", cats_played(rt) == ["fire"])
rt.execute("NOW = NOW + 20 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 350, 1)")
check("a hit of 30% of max health is a big hit", cats_played(rt)[-1] == "big_hit")
rt.execute("NOW = NOW + 20 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 250, 1)")
check("a smaller one is not", len(played(rt)) == 2)
rt.execute("NOW = NOW + 20 FIRE('UNIT_COMBAT', 'target', 'WOUND', '', 900, 1)")
check("damage to someone else is ignored", len(played(rt)) == 2)
rt.execute("NOW = NOW + 20 for i = 1, 4 do FIRE('UNIT_COMBAT', 'player', 'WOUND', '', SECRET, 4) end")
check("secret damage plays nothing", len(played(rt)) == 2)
check("and says once why", sum("secret" in rt.eval(f"PRINTED[{i}]") for i in range(1, rt.eval("#PRINTED") + 1)) == 1)

# --------------------------------------------------------------------------
print("Stuns, bosses, water, life")
rt = boot("""GetOutSugarDB = { warnings = { cc = true, boss_you = true, boss_emote = true, pull = true, wipe = true,
  kill = true, drowning = true, fatigue = true, death = true, durability = true, ready_check = true, range = true },
  seenWelcome = true }""")
rt.execute("FIRE('LOSS_OF_CONTROL_ADDED', 1)")
check("a stun", cats_played(rt) == ["cc"])
rt.execute("NOW = NOW + 20 LOC = { locType = 'SCHOOL_INTERRUPT' } FIRE('LOSS_OF_CONTROL_ADDED', 1)")
check("an interrupt of your cast is not crowd control", len(played(rt)) == 1)
rt.execute("NOW = NOW + 20 LOC = SECRET FIRE('LOSS_OF_CONTROL_ADDED', 1)")
check("unreadable details still count", cats_played(rt)[-1] == "cc")
rt.execute("NOW = NOW + 20 FIRE('RAID_BOSS_WHISPER', 'The boss looks at you') FIRE('CHAT_MSG_RAID_BOSS_WHISPER', 'The boss looks at you')")
check("a boss whisper plays once, not once per copy", cats_played(rt)[-1] == "boss_you" and cats_played(rt).count("boss_you") == 1)
rt.execute("NOW = NOW + 20 FIRE('RAID_BOSS_EMOTE', SECRET)")
check("a secret emote still counts", cats_played(rt)[-1] == "boss_emote")
rt.execute("NOW = NOW + 20 FIRE('ENCOUNTER_START', 1, 'Boss', 1, 5) NOW = NOW + 20 FIRE('ENCOUNTER_END', 1, 'Boss', 1, 5, 0) NOW = NOW + 20 FIRE('ENCOUNTER_END', 1, 'Boss', 1, 5, 1)")
check("pull, wipe, kill", cats_played(rt)[-3:] == ["pull", "wipe", "kill"])
rt.execute("NOW = NOW + 20 FIRE('MIRROR_TIMER_START', 'BREATH', 60000, 60000, -1, false, 'Breath')")
check("breath bar: drowning", cats_played(rt)[-1] == "drowning")
rt.execute("NOW = NOW + 4 BREATH_LEFT = 30000 TICK()")
check("not again at half", cats_played(rt).count("drowning") == 1)
rt.execute("NOW = NOW + 1 BREATH_LEFT = 15000 TICK() NOW = NOW + 1 BREATH_LEFT = 10000 TICK()")
check("again once under 30%, ignoring its cooldown, once", cats_played(rt).count("drowning") == 2)
rt.execute("FIRE('MIRROR_TIMER_STOP', 'BREATH') NOW = NOW + 20 FIRE('MIRROR_TIMER_START', 'EXHAUSTION', 60000, 60000, -1, false, 'Fatigue')")
check("fatigue", cats_played(rt)[-1] == "fatigue")
rt.execute("NOW = NOW + 20 FIRE('PLAYER_DEAD')")
check("death", cats_played(rt)[-1] == "death")
rt.execute("NOW = NOW + 20 DURABILITY[5] = { 30, 100 } FIRE('UPDATE_INVENTORY_DURABILITY')")
check("gear at 30% says nothing", cats_played(rt)[-1] == "death")
rt.execute("NOW = NOW + 20 DURABILITY[5] = { 15, 100 } FIRE('UPDATE_INVENTORY_DURABILITY') NOW = NOW + 700 FIRE('UPDATE_INVENTORY_DURABILITY')")
check("at 20% or less it warns, once while it stays low", cats_played(rt).count("durability") == 1)
rt.execute("NOW = NOW + 20 FIRE('READY_CHECK', 'Chairface Chippendale', 30)")
check("your own ready check is not announced", cats_played(rt)[-1] == "durability")
rt.execute("NOW = NOW + 20 FIRE('READY_CHECK', 'Somebody Else', 30)")
check("someone else's is", cats_played(rt)[-1] == "ready_check")
rt.execute("NOW = NOW + 20 FIRE('UI_ERROR_MESSAGE', 51, 'Target not in line of sight')")
check("line of sight", cats_played(rt)[-1] == "range")
rt.execute("NOW = NOW + 20 FIRE('UI_ERROR_MESSAGE', 51, 'Not enough rage')")
check("other errors are not", cats_played(rt).count("range") == 1)

# --------------------------------------------------------------------------
print("Switching and refusals")
rt = boot("GetOutSugarDB = { warnings = { death = true }, seenWelcome = true }")
rt.execute("NS.SetOn('death', false)")
rt.execute("FIRE('PLAYER_DEAD')")
check("switched off, its detector stops listening", rt.eval("#PLAYED") == 0)
rt = boot("REFUSED = { UNIT_COMBAT = true } GetOutSugarDB = { warnings = { fire = true }, seenWelcome = true }")
check("an event the client refuses is reported, not an error",
      any("refused" in rt.eval(f"PRINTED[{i}]") for i in range(1, rt.eval("#PRINTED") + 1)))

# --------------------------------------------------------------------------
print("Probe and commands")
rt = boot("REFUSED = { COMBAT_TEXT_UPDATE = true } GetOutSugarDB = { seenWelcome = true }")
rt.execute("SlashCmdList.GETOUTSUGAR('probe')")
rt.execute("FIRE('UNIT_COMBAT', 'player', 'WOUND', '', SECRET, 4)")
check("the probe records events, marking secrets",
      "SECRET" in rt.eval("NS.db.probe.events.UNIT_COMBAT.calm"), rt.eval("NS.db.probe.events.UNIT_COMBAT.calm"))
check("and which the client refused", rt.eval("NS.db.probe.refused.COMBAT_TEXT_UPDATE") is True)
check("and the APIs", rt.eval("NS.db.probe.apis.calm['CombatLogGetCurrentEventInfo']") == "missing")
rt.execute("SlashCmdList.GETOUTSUGAR('probe report')")
check("report prints", any("UNIT_COMBAT" in rt.eval(f"PRINTED[{i}]") for i in range(1, rt.eval("#PRINTED") + 1)))
rt.execute("SlashCmdList.GETOUTSUGAR('test fire')")
check("/trixie test plays a warning that is off", cats_played(rt) == ["fire"])
rt.execute("SlashCmdList.GETOUTSUGAR('')")
check("/trixie opens the options", rt.eval("GetOutSugarOptions:IsShown()") is True)

print("\nALL OK" if not failures else f"\n{len(failures)} FAILED")
sys.exit(1 if failures else 0)
