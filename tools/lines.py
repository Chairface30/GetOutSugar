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
    "big_hit": [
        "Ooh, that one's gonna leave a mark.",
        "Ouch! Somebody get this girl a healer!",
        "That hurt, sugar! Watch yourself!",
        "Whew, that was a big one!",
        "Darlin', you just got flattened!",
        "Ow! Heal up, hon!",
        "That's gonna bruise, sugar!",
        "Big hit! Careful now!",
        "Lord, that one rattled my teeth!",
        "You felt that one, didn't you?",
        "Hon, you can't take many more of those!",
        "Yikes! Pop somethin', quick!",
        "That was a wallop, sugar!",
        "Oof! Right in the pride!",
        "Easy, darlin', that one nearly had you!",
        "Heal, heal, heal!",
        "Sugar, you're gettin' clobbered!",
        "That one came with interest!",
        "Whoa! Big one incoming, and it landed!",
        "Somebody's hittin' hard, hon!",
    ],
    "aggro": [
        "Honey, that thing's lookin' at YOU. Back off!",
        "You pulled it, sugar! Run to the tank!",
        "Uh oh, it's comin' for you!",
        "It's on you, hon! Get to the tank!",
        "You've got aggro, darlin'!",
        "Sugar, it likes you. That's bad!",
        "Run to the big guy with the shield!",
        "It's chasin' you, hon! Move!",
        "Well, you've made a new friend. Run!",
        "You grabbed aggro, sugar!",
        "Stop hittin' it, it's on you!",
        "Darlin', you're the tank now. Congratulations.",
        "It's lookin' right at you, hon!",
        "Bring it to the tank, sugar!",
        "You pulled threat! Back it up!",
        "Honey, why is it hittin' YOU?",
        "Aggro! Aggro on you!",
        "Oh sugar, it's mad at you now!",
        "Run it back to the tank, hon!",
        "That monster picked you, darlin'!",
    ],
    "aggro_close": [
        "Ease up, sugar, you're about to pull it!",
        "Easy, hon! You're right on the tank's heels!",
        "Slow down, darlin', your threat's too high!",
        "Careful, sugar, it's about to turn!",
        "Hold back a second, hon!",
        "You're this close to pullin' it!",
        "Easy on the buttons, sugar!",
        "Whoa there, let the tank catch up!",
        "Threat's gettin' high, darlin'!",
        "Pace yourself, hon!",
        "Sugar, you're flirtin' with aggro!",
        "Take a breath, you're nearly on top!",
        "Hold your fire a moment, hon!",
        "Careful now, you're gonna pull it!",
        "Back off a hair, darlin'!",
        "Your threat's creepin' up, sugar!",
        "Ease off, or it's comin' for you!",
        "Easy, tiger!",
        "Let the tank work, hon!",
        "Too hot, sugar! Cool it!",
    ],
    "tank_lost": [
        "You dropped one, darlin'. Go get it back!",
        "Tank! One's gettin' away!",
        "Sugar, it's off you! Taunt it!",
        "You lost one, hon! Grab it!",
        "Loose mob! Go get it, tank!",
        "It's runnin' off, darlin'!",
        "Hon, somethin' slipped away!",
        "Taunt, sugar, taunt!",
        "You lost aggro, hon!",
        "One's eatin' your healer, darlin'!",
        "Get it back on you, sugar!",
        "Tank, you've got a runaway!",
        "Grab it, grab it!",
        "It's not on you anymore, hon!",
        "Somebody's gettin' chewed, sugar! Pick it up!",
        "You let one go, darlin'!",
        "Snag that one back, hon!",
        "Loose one! Loose one!",
        "Sugar, your mob wandered off!",
        "Hey tank, you missed one!",
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
    "boss_you": [
        "It's after you, sugar. Move!",
        "The boss picked you, hon!",
        "Darlin', you're the target!",
        "Uh oh, it's lookin' your way!",
        "It's you, sugar! Get ready!",
        "Heads up, hon, it's comin' for you!",
        "You've been chosen, and not in a good way!",
        "Move, darlin', it's got your name!",
        "Sugar, it's whisperin' sweet nothin's to you. Run!",
        "It singled you out, hon!",
        "You're up, darlin'! Do the thing!",
        "It's on you! Watch out!",
        "Boss has eyes on you, sugar!",
        "Get clear, hon, you're marked!",
        "It said your name, darlin'!",
        "Spread out, sugar, it's you!",
        "Target's on your back, hon!",
        "Run it out, darlin'!",
        "It's got a special gift for you, sugar!",
        "You! Yes, you! Move!",
    ],
    "boss_emote": [
        "Somethin' big's comin'. Heads up!",
        "Watch it, sugar, the boss is up to somethin'!",
        "Heads up, hon!",
        "Uh oh, here it comes!",
        "Look sharp, darlin'!",
        "Big move comin', sugar!",
        "Get ready, hon!",
        "The boss is windin' up!",
        "Somethin's happenin', darlin'!",
        "Eyes up, sugar!",
        "Brace yourself, hon!",
        "That doesn't sound good!",
        "Here we go, darlin'!",
        "Pay attention, sugar!",
        "Oh, it's gettin' fancy now!",
        "Watch the boss, hon!",
        "Somethin' nasty's brewin'!",
        "Mechanic time, sugar!",
        "Stay sharp, darlin'!",
        "Listen up, hon!",
    ],
    "drowning": [
        "Air, sugar! Swim up!",
        "You're runnin' out of breath, hon!",
        "Surface, darlin', surface!",
        "Up, up, up!",
        "Get some air, sugar!",
        "Hon, you need to breathe!",
        "You're drownin', darlin'!",
        "Swim for the top!",
        "Lungs are burnin', sugar! Up!",
        "Air! Now!",
        "Honey, fish breathe water. You don't.",
        "Kick for the surface, hon!",
        "You're turnin' blue, sugar!",
        "Breathe, darlin'!",
        "Up you go, hon, quick!",
        "Out of air! Swim!",
        "Sugar, you're not a mermaid!",
        "Get your head above water!",
        "Hurry up, hon, you're drownin'!",
        "Air, darlin', air!",
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
    "range": [
        "You're too far away, sugar!",
        "Get closer, hon!",
        "Out of range, darlin'!",
        "Sugar, you can't hit it from there!",
        "Face it, hon! Face the thing!",
        "Can't see it, darlin'! Move!",
        "Line of sight, sugar!",
        "Turn around, hon!",
        "Too far, darlin'!",
        "Step in a little, sugar!",
        "You're facin' the wrong way, hon!",
        "Get around that pillar, darlin'!",
        "Closer, sugar, closer!",
        "It's behind somethin', hon!",
        "Out of range again, darlin'!",
        "Sugar, the target's over there!",
        "Hon, you're swingin' at air!",
        "Scoot in, darlin'!",
        "Can't reach, sugar!",
        "Look at it, hon! Look at it!",
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


def write_counts():
    """Counts.lua: the clip count per category, from what is on disk."""
    counts = counts_on_disk()
    lines = ["-- Generated by tools/lines.py from the clips in Sounds/. Do not edit:",
             "-- run a tool that writes clips, or python tools/lines.py, to refresh it.",
             "local _, ns = ...", "ns.COUNTS = {"]
    for cat in POOLS:
        lines.append(f"    {cat} = {counts[cat]},")
    lines.append("}")
    path = os.path.join(ROOT, "Counts.lua")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return counts


if __name__ == "__main__":
    for cat, n in write_counts().items():
        print(f"  {cat:<12} {n}")
