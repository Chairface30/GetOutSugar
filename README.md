# Get Out, Sugar

Trixie, the host from **Chairface's Casino**, yells at you before you die. Standing in fire, pulling aggro, stunned, drowning, the boss picking you: she tells you, loudly, in about twenty different ways each.

Made for **WoW Forever** (interface 16001).

## Using it

- Type **`/trixie`** (or `/gos`). Every warning starts off: tick the ones you want and press **Play** to hear her.
- **Mute Trixie**, the **sound channel** she plays on, and **how often** she speaks are at the bottom of the window.
- `/trixie test <warning>` plays one; `/trixie status` shows what is on.

## The warnings

**Danger**: standing in something · a big hit (30% of your health) · you pulled aggro · about to pull aggro (90%) · tank: a monster got away · stunned, feared or silenced · the boss picked you · boss warnings · drowning · too far out to sea

**Moments**: you died · boss fight starts · boss fight lost · boss defeated · gear about to break · ready check · out of range or not facing

Aggro warnings only speak in a group, since alone every monster is on you anyway. Tick **Aggro warnings when solo** to hear them regardless.

## What it can and cannot see

WoW Forever hides a lot from addons in combat: there is no combat log, and your health and buffs are secret. So there is no low-health warning, and **"standing in something" is a best guess**: several magic-damage hits in three seconds. It can mistake a damage-over-time spell for fire.

`/trixie probe` records what the client lets her see; `/trixie probe report` shows it.

## For developers

- `tools/lines.py`: every line she says, by warning.
- `tools/make_test_tracks.py`: speaks every line with Windows' own voice, for free testing.
- `tools/gen_voices.py`: Trixie's real voice from ElevenLabs; a dry run unless given `--go`, and it reads the API key only from `ELEVENLABS_API_KEY`.
- `python tests/addon_test.py`: the logic, in a stand-in client (needs `pip install lupa`).
