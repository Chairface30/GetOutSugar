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
    # Crowd control, by kind. "cc" is for any other kind, or when the client
    # will not say which.
    "cc_stun": [
        "Sugar, you're stunned!",
        "Seein' stars, hon?",
        "Stunned! Hang in there!",
        "Out cold on your feet, darlin'!",
        "Ding! You got your bell rung!",
        "Stun! Trinket if you've got it!",
        "You're dazed, sugar!",
        "Knocked silly, hon!",
        "Can't lift a finger, darlin'!",
        "Birdies circlin' your head, sugar!",
        "Stunned stiff!",
        "Shake the stars out, hon!",
        "Somebody bonked you good!",
        "You're a statue, darlin'!",
        "Stunlocked, sugar!",
        "Wake up, hon, you're stunned!",
        "Rattled right down to your boots!",
        "Frozen solid, darlin'!",
        "Oof! Stunned!",
        "Snap out of it, sugar!",
    ],
    "cc_fear": [
        "Run, sugar, run! Well, you're gonna anyway!",
        "Feared! Hold on to your hat!",
        "Don't run into anything else, hon!",
        "There she goes, screamin'!",
        "You're runnin' scared, darlin'!",
        "Feared! Watch where you're headed!",
        "Ain't no shame in runnin', sugar!",
        "Legs are goin' without you, hon!",
        "Somebody scared the daylights out of you!",
        "Feared! Try not to pull the whole room!",
        "Look at you go, darlin'!",
        "Panic time, sugar!",
        "Running like the devil's behind you!",
        "Feared, hon! Break it if you can!",
        "Don't run off the ledge, sugar!",
        "Whoa, where you goin', darlin'?",
        "Feared silly!",
        "Keep your wits, hon, it'll wear off!",
        "Scared stiff and runnin'!",
        "Fear! Tremor totem, anybody?",
    ],
    "cc_incap": [
        "Somebody turned you into a sheep, sugar!",
        "Baa! You're polymorphed, hon!",
        "Sapped! Sneaky little rogue!",
        "You're incapacitated, darlin'!",
        "Out like a light, sugar!",
        "Sleepin' on the job, hon?",
        "Disoriented! Don't hit it, it'll break!",
        "You're a critter now, darlin'!",
        "Knocked out cold, sugar!",
        "Sheep! Somebody sheeped you!",
        "Nap time, hon! Bad timing!",
        "You're all turned around, darlin'!",
        "Incapacitated! Hang tight!",
        "Somebody put you to sleep, sugar!",
        "Dizzy, hon? You look it!",
        "Hope you like wool, darlin'!",
        "Out of it! Wait it out!",
        "Gouged! Ouch!",
        "Sweet dreams, sugar! Wake up soon!",
        "Hon, you've been knocked loopy!",
    ],
    "cc_charm": [
        "Uh oh! You're mind controlled, sugar!",
        "Somebody's pullin' your strings, hon!",
        "Don't hurt your friends, darlin'!",
        "You're not yourself right now, sugar!",
        "Mind control! Somebody knock some sense into her!",
        "Hon, you're workin' for the other side!",
        "Charmed! And not in the good way!",
        "Your body's got a new boss, darlin'!",
        "Somebody's drivin' you, sugar!",
        "Break the control, quick!",
        "Mind controlled! Everybody watch out!",
        "Possessed! Lord have mercy!",
        "You've switched sides, hon!",
        "Fight it, darlin', fight it!",
        "Somebody snap her out of it!",
        "Puppet on a string, sugar!",
        "Your team's about to have a bad time!",
        "Charmed by the enemy, hon!",
        "Don't take it personal, it's the mind control!",
        "Controlled! Sorry, everybody!",
    ],
    "cc_silence": [
        "Silenced! Hush now, sugar!",
        "Cat got your tongue, hon?",
        "No spells for you, darlin'!",
        "Silenced! Swing a stick instead!",
        "Mouth's shut, sugar!",
        "Can't cast, hon! Wait it out!",
        "Shush, darlin'!",
        "Spell lock! Quiet time!",
        "Silenced! Well, that's rude!",
        "Hon, you've been muted!",
        "No castin' for a bit, sugar!",
        "Somebody zipped your lips!",
        "Silence! Use somethin' instant!",
        "Your words are gone, darlin'!",
        "Can't say a spell, hon!",
        "Tongue-tied, sugar!",
        "Silenced! Hang on!",
        "No magic right now, darlin'!",
        "Quiet as a church mouse, hon!",
        "Hush, sugar! Silenced!",
    ],
    "cc_root": [
        "Rooted! Your feet are stuck, sugar!",
        "Can't move, hon! Rooted!",
        "Stuck to the floor, darlin'!",
        "Rooted! You can still swing!",
        "Feet are glued, sugar!",
        "Frost nova! Stuck!",
        "You're planted, hon!",
        "Rooted in place, darlin'!",
        "Can't take a step, sugar!",
        "Stuck like a fly in molasses!",
        "Roots! Break 'em if you can!",
        "Your boots are frozen to the ground, hon!",
        "No runnin', darlin', you're rooted!",
        "Pinned down, sugar!",
        "You're not goin' anywhere, hon!",
        "Rooted! Fight from where you stand!",
        "Feet won't budge, darlin'!",
        "Caught in the vines, sugar!",
        "Stuck! Wiggle free!",
        "Rooted, hon! Hold your ground!",
    ],
    "cc_disarm": [
        "Disarmed! Where'd your weapon go, sugar?",
        "They took your weapon, hon!",
        "Empty hands, darlin'!",
        "Disarmed! Use your fists!",
        "Somebody snatched your blade, sugar!",
        "No weapon, hon! Improvise!",
        "Disarmed! Well, that's embarrassin'!",
        "Your weapon's gone, darlin'!",
        "Punch 'em, sugar!",
        "Disarmed! Wait for it back!",
        "Butterfingers, hon!",
        "They knocked it right out of your hand!",
        "Weapon's gone, darlin'!",
        "Disarmed! Use a spell!",
        "Hands are empty, sugar!",
        "Somebody's got sticky fingers!",
        "Disarmed, hon! Hang on!",
        "Your sword flew off, darlin'!",
        "Unarmed and dangerous, sugar!",
        "Disarmed! Kick 'em instead!",
    ],
    "cc": [
        "Shake it off, hon!",
        "You're stuck, sugar!",
        "Break free, darlin'!",
        "Hang in there!",
        "Uh oh, you're locked down!",
        "Hold on, hon, it'll pass!",
        "They've got you pinned!",
        "Trinket out if you can, sugar!",
        "You're caught, darlin'!",
        "Wiggle, hon, wiggle!",
        "Oh no, you're caught!",
        "Somebody help this poor thing!",
        "You're not in control, sugar!",
        "Snap out of it, hon!",
        "They've got you, darlin'!",
        "Break it, sugar!",
        "Crowd controlled!",
        "Hang tight, it won't last!",
        "Control's gone, hon!",
        "Somebody's got you tied up, sugar!",
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
