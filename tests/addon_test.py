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
function PlaySoundFile(path, channel)
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

-- Timers: a one-shot runs when the clock, moved on by WAIT(seconds), gets to it.
AFTER = {}
C_Timer = {
    After = function(d, fn) table.insert(AFTER, { due = NOW + d, fn = fn }) end,
}
function WAIT(seconds)
    local target = NOW + seconds
    while true do
        local soonest
        for i, t in ipairs(AFTER) do
            if t.due <= target and (not soonest or t.due < AFTER[soonest].due) then soonest = i end
        end
        if not soonest then break end
        local t = table.remove(AFTER, soonest)
        NOW = t.due
        t.fn()
    end
    NOW = target
end

function UnitName() return "Chairface", "Chippendale" end
DURABILITY = {}
function GetInventoryItemDurability(slot) local d = DURABILITY[slot] if d then return d[1], d[2] end end
LOC = { locType = "STUN" }
C_LossOfControl = { GetActiveLossOfControlData = function() return LOC end }
MUTED_FILES = {}
function MuteSoundFile(id) MUTED_FILES[id] = true end
function UnmuteSoundFile(id) MUTED_FILES[id] = nil end

-- The minimap libraries, as far as the addon uses them.
DBICON = { registered = {}, shown = {} }
local LDB = { objects = {} }
function LDB:NewDataObject(name, obj) self.objects[name] = obj return obj end
function DBICON:Register(name, obj, db) self.registered[name] = { obj = obj, db = db } self.shown[name] = not db.hide end
function DBICON:IsRegistered(name) return self.registered[name] ~= nil end
function DBICON:Show(name) self.shown[name] = true end
function DBICON:Hide(name) self.shown[name] = false end
function LibStub(name) return name == "LibDataBroker-1.1" and LDB or name == "LibDBIcon-1.0" and DBICON or nil end
TIP = { lines = {} }
function TIP:AddLine(t) table.insert(self.lines, t) end

math.randomseed(1)
'''

# The real libraries need the whole minimap; the harness stands in for them.
TOC = [l.strip() for l in io.open("GetOutSugar.toc", encoding="utf-8")
       if l.strip() and not l.startswith("#") and not l.startswith("Libs")]


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


def printed(rt):
    return [rt.eval(f"PRINTED[{i}]") for i in range(1, rt.eval("#PRINTED") + 1)]


ALL_ON = "GetOutSugarDB = { warnings = { %s }, seenWelcome = true }" % ", ".join(
    f"{c} = true" for c in lines.POOLS)

# --------------------------------------------------------------------------
print("The lines, the catalog and the clips agree")
catalog = boot().eval("(function() local t = {} for _, e in ipairs(NS.CATALOG) do t[#t+1] = e.cat end return table.concat(t, ',') end)()").split(",")
check("every warning in the catalog has lines, and no others", set(catalog) == set(lines.POOLS), set(catalog) ^ set(lines.POOLS))
check("about twenty lines each", all(len(v) >= 18 for v in lines.POOLS.values()))
disk = lines.counts_on_disk()
counts_lua = io.open("Counts.lua", encoding="utf-8").read()
counts = dict(re.findall(r"(\w+) = (\d+),", counts_lua))
check("Counts.lua matches the clips on disk", all(int(counts.get(c, -1)) == n for c, n in disk.items()), counts)
check("every line has its clip", all(disk[c] == len(v) for c, v in lines.POOLS.items()), disk)
secs = boot().eval("(function() for cat, n in pairs(NS.COUNTS) do if #NS.SECONDS[cat] ~= n then return cat end end return 'ok' end)()")
check("every clip has its length recorded", secs == "ok", secs)
stray = [f for f in os.listdir("Sounds") if re.sub(r"\d+\.ogg$", "", f)[len(lines.PREFIX):] not in lines.POOLS]
check("no clips left for warnings that are gone", not stray, stray[:5])
# Loudness: one clip that is quieter than the rest is the one nobody hears.
# Measured with ffmpeg, so it is skipped where there is none.
import level
from concurrent.futures import ThreadPoolExecutor
ffmpeg = lines.find_ffmpeg()
if ffmpeg:
    names = level.clips("Sounds")
    with ThreadPoolExecutor(8) as pool:
        measured = list(zip(names, pool.map(lambda n: level.measure(ffmpeg, os.path.join("Sounds", n)), names)))
    off = [(n, m["lufs"], m["peak"]) for n, m in measured if not level.on_target(m)]
    check(f"every clip is within {level.TOLERANCE} LU of {level.TARGET} LUFS, with no peak at full scale", not off, off[:5])
else:
    print("  skip the clips' loudness (no ffmpeg)")

# --------------------------------------------------------------------------
print("A new install")
rt = boot()
check("every warning starts off", rt.eval("next(NS.db.warnings) == nil") is True)
check("nothing is listening", rt.eval("(function() for _, d in ipairs(NS.detectors) do if d.active then return false end end return true end)()") is True)
rt.execute("FIRE('PLAYER_DEAD') FIRE('LOSS_OF_CONTROL_ADDED', 'player', 1)")
check("so nothing plays", rt.eval("#PLAYED") == 0)
check("and the game's ready check sound is untouched", rt.eval("next(MUTED_FILES) == nil") is True)
check("the options open by themselves, once", rt.eval("NS.db.seenWelcome") is True)

# --------------------------------------------------------------------------
print("The voice")
rt = boot(ALL_ON)
rt.execute("NS.Voice.Play('death')")
check("a line plays from the warning's clips", cats_played(rt) == ["death"], played(rt))
check("on the chosen channel", rt.eval("PLAYED[1].channel") == "Dialog")
rt.execute("WAIT(1) NS.Voice.Play('kill')")
check("while she speaks, the next line waits: never two at once", cats_played(rt) == ["death"])
rt.execute("NS.Voice.Play('fire')")
check("nothing is cut off", rt.eval("#STOPPED") == 0)
rt.execute("NS.Voice.Play('kill')")
check("a warning already waiting is not queued twice", rt.eval("#NS.Voice.queue") == 2)
check("danger waits ahead of a moment", rt.eval("NS.Voice.queue[1].cat") == "fire")
first_len = rt.eval("NS.SECONDS.death[tonumber(PLAYED[1].path:match('death(%d+)'))]")
rt.execute(f"WAIT({first_len} - 1 - 0.05)")
check("the next waits out the clip's measured length", cats_played(rt) == ["death"])
rt.execute("WAIT(0.3)")
check("then plays", cats_played(rt) == ["death", "fire"])
rt.execute("WAIT(8)")
check("and each waiting line in turn", cats_played(rt) == ["death", "fire", "kill"], cats_played(rt))
rt.execute("WAIT(10) NS.Voice.Play('fire') WAIT(10) NS.Voice.Play('fire') WAIT(10) NS.Voice.Play('fire')")
check("no cooldowns: the same warning speaks every time it happens", cats_played(rt).count("fire") == 4)
check("never the same clip twice running", played(rt)[-1] != played(rt)[-2])
rt.execute("WAIT(10) NS.Voice.Play('fire') NS.Voice.Play('fire')")
check("a warning she is saying right now is not queued behind itself", rt.eval("#NS.Voice.queue") == 0)
rt.execute("WAIT(10) NS.Voice.Play('death') NS.Voice.Play('pull') NS.Voice.Play('wipe') NS.Voice.Play('kill') NS.Voice.Play('cc')")
check("the queue holds three at most", rt.eval("#NS.Voice.queue") == 3)
rt.execute("WAIT(60) FIRE('PLAYER_DEAD')")
check("the queue empties in turn", rt.eval("#NS.Voice.queue") == 0)
n = len(played(rt))
rt.execute("WAIT(20) NS.Voice.Play('pull') WAIT(0.1) NS.Voice.Play('cc') NS.Voice.Stop() WAIT(20)")
check("stopping her clears what was waiting", len(played(rt)) == n + 1)
rt.execute("WAIT(20) NS.db.warnings.durability = nil NS.Voice.Play('durability')")
check("a warning that is off stays quiet", cats_played(rt)[-1] != "durability")
rt.execute("NS.Voice.Play('durability', { preview = true })")
check("but its Play button still plays it", cats_played(rt)[-1] == "durability")
stops = rt.eval("#STOPPED")
rt.execute("WAIT(0.5) NS.Voice.Play('wipe', { preview = true })")
check("a second Play stops the first rather than talking over it",
      cats_played(rt)[-1] == "wipe" and rt.eval("#STOPPED") == stops + 1)
rt.execute("WAIT(20) NS.db.muted = true NS.Voice.Play('death')")
check("muted, nothing plays", cats_played(rt)[-1] == "wipe")

# --------------------------------------------------------------------------
print("Standing in something")
rt = boot("GetOutSugarDB = { warnings = { fire = true }, seenWelcome = true }")
rt.execute("FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4) NOW = NOW + 1 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4)")
check("two magic hits are not yet standing in it", rt.eval("#PLAYED") == 0)
rt.execute("NOW = NOW + 1 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4)")
check("three in three seconds are", cats_played(rt) == ["fire"])
rt.execute("WAIT(20) for i = 1, 5 do FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 1) NOW = NOW + 0.5 end")
check("physical hits are not fire", cats_played(rt) == ["fire"])
rt.execute("WAIT(20) FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4) NOW = NOW + 4 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4) NOW = NOW + 4 FIRE('UNIT_COMBAT', 'player', 'WOUND', '', 50, 4)")
check("hits spread past three seconds are not", cats_played(rt) == ["fire"])
rt.execute("WAIT(20) for i = 1, 3 do FIRE('UNIT_COMBAT', 'target', 'WOUND', '', 50, 4) end")
check("damage to someone else is ignored", len(played(rt)) == 1)
rt.execute("WAIT(20) for i = 1, 4 do FIRE('UNIT_COMBAT', 'player', 'WOUND', '', SECRET, 4) end")
check("secret damage plays nothing", len(played(rt)) == 1)
check("and says once why", sum("secret" in p for p in printed(rt)) == 1)

# --------------------------------------------------------------------------
print("Stuns, fatigue, fights, life")
rt = boot(ALL_ON)
for kind, cat in [("STUN", "cc_stun"), ("STUN_MECHANIC", "cc_stun"), ("FEAR", "cc_fear"), ("CONFUSE", "cc_incap"),
                  ("CHARM", "cc_charm"), ("POSSESS", "cc_charm"), ("SILENCE", "cc_silence"), ("ROOT", "cc_root"),
                  ("DISARM", "cc_disarm"), ("PACIFY", "cc")]:
    rt.execute(f"WAIT(20) LOC = {{ locType = '{kind}' }} FIRE('LOSS_OF_CONTROL_ADDED', 'player', 1)")
    check(f"{kind.lower()}: her {cat} lines", cats_played(rt)[-1] == cat, cats_played(rt)[-1:])
n = len(played(rt))
rt.execute("WAIT(20) LOC = { locType = 'SCHOOL_INTERRUPT' } FIRE('LOSS_OF_CONTROL_ADDED', 'player', 1)")
check("an interrupt of your cast is not crowd control", len(played(rt)) == n)
rt.execute("WAIT(20) LOC = SECRET FIRE('LOSS_OF_CONTROL_ADDED', 'player', 1)")
check("a kind the client keeps secret is other crowd control", cats_played(rt)[-1] == "cc")
rt.execute("WAIT(20) LOC = { locType = 'STUN' } FIRE('LOSS_OF_CONTROL_ADDED', 'player', 1) FIRE('LOSS_OF_CONTROL_ADDED', 'player', 2)")
check("a stun reported twice is said once", cats_played(rt).count("cc_stun") == 3, cats_played(rt))
rt.execute("WAIT(20) NS.SetOn('cc_root', false) LOC = { locType = 'ROOT' } FIRE('LOSS_OF_CONTROL_ADDED', 'player', 1)")
check("a kind switched off stays quiet, even with other crowd control on", cats_played(rt)[-1] != "cc_root" and cats_played(rt)[-1] != "cc")
rt.execute("WAIT(20) LOC = { locType = 'ROOT' } FIRE('LOSS_OF_CONTROL_ADDED', 'player', 1) WAIT(20)")
rt.execute("WAIT(20) FIRE('ENCOUNTER_START', 1, 'Boss', 1, 5) WAIT(20) FIRE('ENCOUNTER_END', 1, 'Boss', 1, 5, 0) WAIT(20) FIRE('ENCOUNTER_END', 1, 'Boss', 1, 5, 1)")
check("pull, wipe, kill", cats_played(rt)[-3:] == ["pull", "wipe", "kill"])
rt.execute("WAIT(20) FIRE('START_PLAYER_COUNTDOWN', 'player', 10, 10, true, 'Somebody Else')")
check("a pull countdown starting: countdown", cats_played(rt)[-1] == "countdown")
n = len(played(rt))
rt.execute("FIRE('START_TIMER', 2, 10, 10)")
check("the same countdown announced twice is said once", len(played(rt)) == n)
rt.execute("WAIT(20) FIRE('START_TIMER', 2, 10, 10)")
check("the older START_TIMER for a player countdown counts too", cats_played(rt)[-1] == "countdown" and len(played(rt)) == n + 1)
rt.execute("WAIT(20) FIRE('START_TIMER', 0, 60, 60)")
check("a battleground's start timer does not", len(played(rt)) == n + 1)
n = len(played(rt))
rt.execute("WAIT(20) FIRE('MIRROR_TIMER_START', 'BREATH', 60000, 60000, -1, false, 'Breath')")
check("the breath bar says nothing", len(played(rt)) == n)
rt.execute("WAIT(20) FIRE('MIRROR_TIMER_START', 'EXHAUSTION', 60000, 60000, -1, false, 'Fatigue')")
check("the fatigue bar: fatigue", cats_played(rt)[-1] == "fatigue")
rt.execute("WAIT(20) FIRE('PLAYER_DEAD')")
check("death", cats_played(rt)[-1] == "death")
rt.execute("WAIT(20) DURABILITY[5] = { 30, 100 } FIRE('UPDATE_INVENTORY_DURABILITY')")
check("gear at 30% says nothing", cats_played(rt)[-1] == "death")
rt.execute("WAIT(20) DURABILITY[5] = { 15, 100 } FIRE('UPDATE_INVENTORY_DURABILITY') WAIT(20) FIRE('UPDATE_INVENTORY_DURABILITY')")
check("at 20% or less it warns, once while it stays low", cats_played(rt).count("durability") == 1)
rt.execute("WAIT(20) DURABILITY[5] = { 100, 100 } FIRE('UPDATE_INVENTORY_DURABILITY') WAIT(20) DURABILITY[5] = { 10, 100 } FIRE('UPDATE_INVENTORY_DURABILITY')")
check("and again once repaired and worn down", cats_played(rt).count("durability") == 2)
check("with ready checks on, the game's own ready check sound is muted", rt.eval("MUTED_FILES[567409]") is True)
rt.execute("WAIT(20) FIRE('READY_CHECK', 'Chairface Chippendale', 30)")
check("your own ready check is not announced", cats_played(rt)[-1] == "durability")
rt.execute("WAIT(20) FIRE('READY_CHECK', 'Somebody Else', 30)")
check("someone else's is, in its place", cats_played(rt)[-1] == "ready_check")
rt.execute("NS.SetOn('ready_check', false)")
check("switched off, the game's sound comes back", rt.eval("MUTED_FILES[567409]") is None)

# --------------------------------------------------------------------------
print("Switching and refusals")
rt = boot("GetOutSugarDB = { warnings = { cc = true }, seenWelcome = true }")
check("someone who had crowd control on gets every kind of it on",
      rt.eval("NS.IsOn('cc_stun') and NS.IsOn('cc_fear') and NS.IsOn('cc_disarm') and NS.IsOn('cc')") is True)
rt.execute("NS.SetOn('cc_fear', false)")
rt = boot("GetOutSugarDB = { warnings = { cc = true }, ccSplit = true, seenWelcome = true }")
check("but only once: a kind switched off since stays off", rt.eval("NS.IsOn('cc_fear')") is False)
rt = boot("GetOutSugarDB = { warnings = { death = true }, seenWelcome = true }")
check("the game's ready check sound is left alone while ready checks are off", rt.eval("MUTED_FILES[567409]") is None)
rt.execute("NS.SetOn('death', false) FIRE('PLAYER_DEAD')")
check("switched off, its detector stops listening", rt.eval("#PLAYED") == 0)
rt = boot("REFUSED = { UNIT_COMBAT = true } GetOutSugarDB = { warnings = { fire = true }, seenWelcome = true }")
check("an event the client refuses is reported, not an error", any("refused" in p for p in printed(rt)))
rt = boot("GetOutSugarDB = { warnings = { aggro = true, drowning = true }, chatty = 2, aggroSolo = true, seenWelcome = true }")
rt.execute("FIRE('MIRROR_TIMER_START', 'BREATH', 60000, 60000, -1, false, 'Breath') NS.Refresh()")
check("settings for warnings that are gone do no harm",
      rt.eval("#PLAYED") == 0 and rt.eval("NS.CATEGORY.aggro") is None and not any("error" in p for p in printed(rt)))

# --------------------------------------------------------------------------
print("The minimap button")
rt = boot("GetOutSugarDB = { warnings = { fire = true }, seenWelcome = true }")
check("it is registered with LibDBIcon", rt.eval("DBICON:IsRegistered('GetOutSugar')") is True)
check("shown by default", rt.eval("DBICON.shown.GetOutSugar") is True)
check("wearing Trixie's face", rt.eval("DBICON.registered.GetOutSugar.obj.icon") == r"Interface\AddOns\GetOutSugar\Textures\trixie")
check("and the face is on disk", os.path.exists("Textures/trixie.tga"))
check("its position is kept in the saved settings", rt.eval("DBICON.registered.GetOutSugar.db == NS.db.minimap") is True)
rt.execute("DBICON.registered.GetOutSugar.obj.OnClick(nil, 'LeftButton')")
check("click opens the options", rt.eval("GetOutSugarOptions:IsShown()") is True)
rt.execute("DBICON.registered.GetOutSugar.obj.OnClick(nil, 'RightButton')")
check("right-click mutes her", rt.eval("NS.db.muted") is True)
rt.execute("DBICON.registered.GetOutSugar.obj.OnTooltipShow(TIP)")
tip = [rt.eval(f"TIP.lines[{i}]") for i in range(1, rt.eval("#TIP.lines") + 1)]
check("the tooltip says how many warnings are on, and that she is muted",
      f"1 of {len(lines.POOLS)} warnings on." in tip and "Muted." in tip, tip)
rt.execute("DBICON.registered.GetOutSugar.obj.OnClick(nil, 'RightButton')")
check("right-click again unmutes", rt.eval("NS.db.muted") is False)
rt.execute("SlashCmdList.GETOUTSUGAR('minimap')")
check("/trixie minimap hides it, and it stays hidden", rt.eval("DBICON.shown.GetOutSugar") is False and rt.eval("NS.db.minimap.hide") is True)
rt = boot("GetOutSugarDB = { minimap = { hide = true }, seenWelcome = true }")
check("hidden across a reload", rt.eval("DBICON.shown.GetOutSugar") is False)

# --------------------------------------------------------------------------
print("Probe and commands")
rt = boot("REFUSED = { COMBAT_TEXT_UPDATE = true } GetOutSugarDB = { seenWelcome = true }")
rt.execute("SlashCmdList.GETOUTSUGAR('probe')")
rt.execute("FIRE('UNIT_COMBAT', 'player', 'WOUND', '', SECRET, 4)")
check("the probe records events, marking secrets",
      "SECRET" in rt.eval("NS.db.probe.events.UNIT_COMBAT.calm"), rt.eval("NS.db.probe.events.UNIT_COMBAT.calm"))
check("and which the client refused", rt.eval("NS.db.probe.refused.COMBAT_TEXT_UPDATE") is True)
check("and the APIs", rt.eval("NS.db.probe.apis.calm['MuteSoundFile / UnmuteSoundFile']") == "exists / exists")
rt.execute("SlashCmdList.GETOUTSUGAR('probe report')")
check("report prints", any("UNIT_COMBAT" in p for p in printed(rt)))
rt.execute("SlashCmdList.GETOUTSUGAR('test fire')")
check("/trixie test plays a warning that is off", cats_played(rt) == ["fire"])
rt.execute("SlashCmdList.GETOUTSUGAR('')")
check("/trixie opens the options", rt.eval("GetOutSugarOptions:IsShown()") is True)

print("\nALL OK" if not failures else f"\n{len(failures)} FAILED")
sys.exit(1 if failures else 0)
