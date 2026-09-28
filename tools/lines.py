"""Every line Trixie says, by warning. The one source for all three uses:

  make_test_tracks.py  speaks each line with Windows' own voice (free), so the
                       addon can be tested in game before any credits are spent
  gen_voices.py        sends the same lines to ElevenLabs, later
  write_counts()       writes Counts.lua from the clips actually on disk

Files are Sounds/gos_<category><n>.ogg, n counting from 1 in list order.

Persona: Trixie, the casino's host -- a sassy Southern belle, warm and
teasing -- except here she is yelling because you are about to die. Danger
lines are short on purpose: they have to land before the next tick does.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOUNDS = os.path.join(ROOT, "Sounds")
PREFIX = "gos_"

POOLS = {
    # ---- danger ---------------------------------------------------------
    "fire": [
        "Get out of the fire, sugar!",
        "Move your feet, hon, you're cookin'!",
        "Out of the bad stuff, now!",
        "Sugar, you're standin' in it!",
        "Hot, hot, hot! Move!",
        "Darlin', that glowin' floor is not a rug!",
        "Step left, step right, just STEP!",
        "You're sizzlin', hon! Get out!",
        "Feet, sugar! Use 'em!",
        "Out of it! Out out out!",
        "Honey, the ground is tryin' to kill you!",
        "Quit dancin' in the flames and move!",
        "That's not a spa, sugar, get out!",
        "Move, move, move!",
        "You're on fire, and not the good kind!",
        "Scoot, darlin'! Now!",
        "Sugar, the floor! The FLOOR!",
        "Get out before you're well done!",
        "Out of the puddle, hon!",
        "Don't just stand there, MOVE!",
    ],
    "cc": [
        "Shake it off, hon!",
        "You're stuck, sugar!",
        "Break free, darlin'!",
        "Can't move! Hang in there!",
        "Uh oh, you're locked down!",
        "Sugar, you're stunned!",
        "Hold on, hon, it'll pass!",
        "They've got you pinned!",
        "Trinket out if you can, sugar!",
        "You're frozen, darlin'!",
        "Wiggle, hon, wiggle!",
        "Oh no, you're caught!",
        "Somebody help this poor thing!",
        "You're not goin' anywhere, sugar!",
        "Snap out of it, hon!",
        "They've got you, darlin'!",
        "Break it, sugar!",
        "Stuck like a fly in molasses!",
        "Hang tight, it won't last!",
        "Control's gone, hon!",
    ],
    "fatigue": [
        "Turn back, that water's got teeth.",
        "Too far out, sugar! Swim back!",
        "Hon, you're gettin' tired. Turn around!",
        "Deep water, darlin'! Head back!",
        "You're wanderin' too far, sugar!",
        "Fatigue, hon! Back to shore!",
        "That's the edge of the world, darlin'. Turn around!",
        "Nothin' out there but trouble, sugar!",
        "Swim back, hon!",
        "You're wearin' out, darlin'!",
        "Wrong way, sugar!",
        "Turn around before you sink!",
        "Head for land, hon!",
        "You'll never make it, darlin'. Go back!",
        "Too deep, sugar!",
        "Back the way you came, hon!",
        "You're gettin' exhausted, darlin'!",
        "Sugar, there's nothin' out there!",
        "Paddle back, hon, quick!",
        "Not that way, darlin'!",
    ],
    # ---- situational -----------------------------------------------------
    "death": [
        "Well, sugar, that went about as well as expected.",
        "Oh, darlin'. I told you to move.",
        "Down you go, hon. Walk it off.",
        "Rest in pieces, sugar.",
        "That's a shame, hon. You had such potential.",
        "Oops. Somebody call the spirit healer.",
        "Darlin', dyin' is not a strategy.",
        "Well, that's one way to take a break.",
        "Sugar, the floor was not that comfortable.",
        "Pick yourself up, hon. We've all been there.",
        "And that, darlin', is why I yell.",
        "You died, sugar. Happens to the best of us. And you.",
        "Lord have mercy. Run back, hon.",
        "I'd send flowers, but you'll be back in a minute.",
        "Sugar, that was not the plan.",
        "Well, you made it look dramatic, at least.",
        "Oh honey. Oh no.",
        "Another one for the repair bill, darlin'.",
        "Go on, hon, release. I'll wait.",
        "That's what we call a learnin' experience, sugar.",
    ],
    "pull": [
        "Here we go, sugar! Look alive!",
        "Boss is up, hon! Showtime!",
        "Game faces on, darlin'!",
        "Let's dance, sugar!",
        "Here it comes, hon! Stay sharp!",
        "Fight's on, darlin'!",
        "Buckle up, sugar!",
        "Big one, hon! Don't stand in anything!",
        "Alright, darlin', let's see what you've got!",
        "Pull! Everybody on your toes!",
        "It's on, sugar!",
        "Places, everybody!",
        "Keep your eyes open, hon!",
        "Let's make this quick, darlin'!",
        "Here we go! Remember what I told you!",
        "Boss fight, sugar! Don't embarrass me!",
        "Time to earn that loot, hon!",
        "Chin up, darlin', it's go time!",
        "Rollin' the dice, sugar!",
        "Deal 'em, hon! Let's go!",
    ],
    "wipe": [
        "Well, that didn't work, did it, sugar?",
        "Everybody's down. Let's try that again.",
        "Wipe it up, hon. Round two.",
        "Oh darlin', that was a mess.",
        "Run back, sugar. The house always gets another hand.",
        "That's a wipe, hon. Shake it off.",
        "Well, the boss had a good day.",
        "Regroup, darlin'. You'll get it.",
        "Sugar, I've seen better pulls at a taffy stand.",
        "That's alright, hon. Learn and go again.",
        "Back to the start, darlin'.",
        "Somebody stood in somethin', I just know it.",
        "Wiped, sugar. Repair bills all around.",
        "Dust yourselves off, hon.",
        "Not today, darlin'. Maybe next time.",
        "The house wins that one, sugar.",
        "Let's pretend that never happened, hon.",
        "Deep breath, darlin'. Again.",
        "That's a bust, sugar. Deal again.",
        "Oh honey, everybody's dead.",
    ],
    "kill": [
        "Woohoo! You got it, sugar!",
        "Down it goes! Nice work, hon!",
        "That's how it's done, darlin'!",
        "Jackpot! Boss is dead!",
        "Winner winner, sugar!",
        "Now that's a payout, hon!",
        "Look at you, darlin'! Victory!",
        "Boss down! Go get your loot!",
        "Ha! Knew you had it in you, sugar!",
        "Beautiful, hon! Just beautiful!",
        "The house pays out, darlin'!",
        "You beat it, sugar! Whoo!",
        "That's a kill, hon! Drinks are on me!",
        "Well I'll be! You did it!",
        "Big win, darlin'!",
        "Cash it in, sugar!",
        "Now go roll on that loot, hon!",
        "You made that look easy, darlin'!",
        "Boss is done, sugar! Take a bow!",
        "Hot streak, hon! Keep it goin'!",
    ],
    "durability": [
        "Sugar, your gear's fallin' apart. Go see a smith.",
        "Hon, your armor's held together with hope.",
        "Darlin', get those repairs done.",
        "Your gear's about to break, sugar!",
        "Time for a repair bill, hon.",
        "That armor's seen better days, darlin'.",
        "Sugar, you're one hit from naked.",
        "Go find a vendor, hon. Your gear's cryin'.",
        "Repairs, darlin'! Before it all breaks!",
        "Your stuff's in tatters, sugar.",
        "Hon, even the rats have better armor right now.",
        "Get that fixed before the next fight, darlin'.",
        "Your gear's red, sugar. Red is bad.",
        "Somebody needs an anvil, hon.",
        "Darlin', that armor won't last another pull.",
        "Sugar, broken gear won't save you.",
        "Repair up, hon. I mean it.",
        "Your durability's in the gutter, darlin'.",
        "Find a smith, sugar. Now.",
        "Hon, you look like you lost a fight with a blender.",
    ],
    "ready_check": [
        "Ready check, sugar! Click it!",
        "Are you ready, hon? Say yes!",
        "Ready check, darlin'!",
        "Hit that ready button, sugar!",
        "They're askin' if you're ready, hon!",
        "Ready check! Don't keep 'em waitin'!",
        "Wake up, darlin', ready check!",
        "Sugar, click ready!",
        "Ready or not, hon!",
        "Ready check! Put down the snacks!",
        "Everybody's waitin' on you, darlin'!",
        "Yes or no, sugar? Ready check!",
        "Ready up, hon!",
        "Ready check, darlin'! Tick tock!",
        "Are we doin' this, sugar?",
        "Ready check! Look alive, hon!",
        "Answer the ready check, darlin'!",
        "Hon, the raid wants an answer!",
        "Sugar, ready check! Go go go!",
        "Ready check! Don't be that person, hon!",
    ],
}


def clip_name(cat, n):
    return f"{PREFIX}{cat}{n}"


def all_lines():
    """[(name, category, text)] in generation order."""
    out = []
    for cat, lines in POOLS.items():
        for i, text in enumerate(lines, 1):
            out.append((clip_name(cat, i), cat, text))
    return out


def counts_on_disk():
    """How many clips each category has on disk, counted from 1 with no gaps,
    so the addon's random pick never lands on a missing file."""
    have = set()
    if os.path.isdir(SOUNDS):
        for f in os.listdir(SOUNDS):
            base, ext = os.path.splitext(f)
            if ext.lower() in (".ogg", ".mp3"):
                have.add(base)
    counts = {}
    for cat in POOLS:
        n = 0
        while clip_name(cat, n + 1) in have:
            n += 1
        counts[cat] = n
    return counts


LCONNECT = r"C:\Program Files\Lian-Li\L-Connect 3\x64\ffmpeg.exe"


def find_ffmpeg(arg=None):
    import shutil
    for c in (arg, os.environ.get("FFMPEG"), shutil.which("ffmpeg"), LCONNECT):
        if c and os.path.isfile(c):
            return c
    return None


def clip_seconds(path, ffmpeg):
    """A clip's length, read from ffmpeg's report on it."""
    import subprocess
    r = subprocess.run([ffmpeg, "-hide_banner", "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        return None
    h, mi, se = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(se)


def write_counts(ffmpeg=None):
    """Counts.lua: how many clips each warning has, and how long each one runs.

    The client cannot say how long a sound is, and the addon must know, to
    start the next line only once the last has finished."""
    counts = counts_on_disk()
    ffmpeg = find_ffmpeg(ffmpeg)
    if not ffmpeg:
        raise SystemExit("ffmpeg not found (set FFMPEG): clip lengths are needed for Counts.lua")
    out = ["-- Generated by tools/lines.py from the clips in Sounds/. Do not edit:",
           "-- run a tool that writes clips, or python tools/lines.py, to refresh it.",
           "local _, ns = ...", "ns.COUNTS = {"]
    for cat in POOLS:
        out.append(f"    {cat} = {counts[cat]},")
    out += ["}", "", "-- Seconds each clip runs, in clip order.", "ns.SECONDS = {"]
    for cat in POOLS:
        secs = []
        for n in range(1, counts[cat] + 1):
            path = os.path.join(SOUNDS, clip_name(cat, n) + ".ogg")
            if not os.path.exists(path):
                path = os.path.join(SOUNDS, clip_name(cat, n) + ".mp3")
            secs.append(f"{clip_seconds(path, ffmpeg) or 4:.2f}")
        out.append(f"    {cat} = {{ {', '.join(secs)} }},")
    out.append("}")
    with open(os.path.join(ROOT, "Counts.lua"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    return counts


if __name__ == "__main__":
    for cat, n in write_counts().items():
        print(f"  {cat:<12} {n}")
