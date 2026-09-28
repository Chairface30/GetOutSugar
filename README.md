# Get Out, Sugar

Trixie, the host from **Chairface's Casino**, yells at you before you die. Standing in fire, stunned, swimming out too far, dying, a boss fight starting: she tells you, loudly, in twenty different ways each.

Made for **WoW Forever** (interface 16001).

## Using it

- Click **Trixie's face on the minimap**, or type **`/trixie`** (or `/gos`). Right-click her face to mute or unmute her.
- Every warning starts off: tick the ones you want and press **Play** to hear her.
- **Mute Trixie**, the **minimap button** and the **sound channel** she plays on are at the bottom of the window.
- She speaks every time a warning that is on happens, and never over herself: while she is talking, the next line waits its turn.
- `/trixie test <warning>` plays one; `/trixie status` shows what is on.

## The warnings

**Danger**: standing in something · too far out to sea

**Crowd control**, each kind with its own lines: stunned · feared · incapacitated (sheep, sap, gouge, sleep, disorient) · mind controlled · silenced · rooted · disarmed · other crowd control (any other kind, or one the game keeps hidden)

**Moments**: you died · pull countdown starts · boss fight starts · boss fight lost · boss defeated · gear about to break (20%) · ready check

With **Ready check** on, her line replaces the game's own ready check sound.

## What it can and cannot see

WoW Forever hides a lot from addons in combat: there is no combat log, and your health and buffs are secret. So there is no low-health warning, and **"standing in something" is a best guess**: several magic-damage hits in three seconds. It can mistake a damage-over-time spell for fire.

`/trixie probe` records what the client lets her see; `/trixie probe report` shows it.

## For developers

- `tools/lines.py`: every line she says, by warning.
- `tools/make_test_tracks.py`: speaks every line with Windows' own voice, for free testing.
- `tools/gen_voices.py`: Trixie's real voice from ElevenLabs; a dry run unless given `--go`, and it reads the API key only from `ELEVENLABS_API_KEY`.
- `python tests/addon_test.py`: the logic, in a stand-in client (needs `pip install lupa`).
