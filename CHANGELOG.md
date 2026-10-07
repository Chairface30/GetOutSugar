# Changelog

## Get Out, Sugar v0.10 (2026-10-06)

**New**
- **Count the pull down:** Trixie counts a pull timer out loud, "Ten!" to "One!", then "Go!", each number on its second. She joins a shorter timer at the right number, stops if the pull is called off, and holds her other lines until "Go". On a timer under 15 seconds she skips her start line and just counts. Her numbers replace the game's countdown tick and end sound, which stay muted while this is on (battleground start timers use the same sounds). Off until you tick it; Play counts three, two, one, go.
- **Twice the lines:** every warning has twenty more, short ones, in Trixie's voice: forty each, 640 in all. The new ones leave out "hon", "sugar" and "darlin'".

**Changed**
- **"Standing in something" is gone.** With no combat log, nothing the client gives an addon can tell fire on the floor from a damage-over-time spell or a spell cast at you, so she kept telling you to move out of things you can't move out of. She now speaks only when the game itself says what happened.
- **Every line is now the same loudness, and louder.** Trixie's lines used to vary a lot with the delivery: a sighed line could be less than a quarter as loud as a shouted one, and the quietest were lost in a fight. All 340 clips are now leveled to the same loudness, about that of DBM's voice packs. On average they are about 7 dB louder; the quietest crowd control lines gained about 13 dB.

## Get Out, Sugar v0.9 (2026-09-28)

**New**
- **Pull countdown starts:** Trixie calls it when someone starts a pull timer (`/pull`, the countdown button, or a boss mod's pull timer that uses the game's countdown). Twenty lines, off until you tick it.

## Get Out, Sugar v0.8 (2026-09-28)

**New**
- **Get Out, Sugar**: Trixie, the host from Chairface's Casino, yells at you before you die. Sixteen warnings, twenty lines each:
  - **Danger:** standing in something, too far out to sea, and crowd control by kind: stunned, feared, incapacitated (sheep, sap, disorient), mind controlled, silenced, rooted, disarmed, and any other.
  - **Moments:** you died, boss fight starts, boss fight lost, boss defeated, gear about to break, ready checks.
- **She always speaks** for a warning that is on, every time it happens, and **never over herself**: while she is talking, the next line waits for her to finish. Danger waits ahead of the moments.
- **Ready checks:** her line replaces the game's own ready check sound while that warning is on.
- **A minimap button with Trixie's face:** click for the options, right-click to mute or unmute her. Hide it in the options or with `/trixie minimap`.
- Every warning starts off. `/trixie` opens the options: tick what you want and press Play to hear it. Mute and the sound channel are there too.
- `/trixie probe` records what this client lets the warnings see.
- For WoW Forever. The client has no combat log, so "standing in something" is a best guess from the damage you take, and can mistake a damage-over-time spell for fire.
- **Trixie's own voice** for all 320 lines, recorded with ElevenLabs' Eleven v4, each line directed with an audio tag (alarmed, teasing, sighing and the rest).
