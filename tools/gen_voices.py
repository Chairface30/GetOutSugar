#!/usr/bin/env python3
"""Trixie's real voice from ElevenLabs, replacing the test clips. SPENDS CREDITS.

Eleven v4 (model eleven_v4), voice Z3R5wn05IrDiVCyEkUrK. Each line is sent
with its audio tag from lines.prompt(): v4 takes the tag as direction for the
delivery and does not say it.

Nothing is sent without --go or --sample. Without them this lists what would
be made, with the exact text sent, and how many characters that costs.

Each clip is fetched as mp3, made louder (ElevenLabs output is quiet, about
-24 dB; +30% with a limiter, as the Casino's amplify_voices.py does) and saved
as Ogg over the test clip of the same name. voiced.json remembers which clips
are done, so a run that hits the monthly quota picks up where it stopped.

  set ELEVENLABS_API_KEY=sk_...                   (never written to any file)
  python tools/gen_voices.py                      # dry run: every prompt, and the cost
  python tools/gen_voices.py --sample 8           # 8 clips across the warnings, into tools/samples/
  python tools/gen_voices.py --go                 # generate every clip not yet in her voice
  python tools/gen_voices.py --go --only fire,cc_stun
"""
import argparse, json, os, subprocess, sys, tempfile, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines
from make_test_tracks import find_ffmpeg

API = "https://api.elevenlabs.io/v1"
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "Z3R5wn05IrDiVCyEkUrK")
MODEL_ID = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_v4")
OUTPUT_FORMAT = "mp3_44100_128"
# The Casino's settings. If the model refuses them, the fallbacks are tried in
# turn (newer models accept fewer settings), and the one that worked is said.
SETTINGS = [
    {"stability": 0.45, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True},
    {"stability": 0.5, "similarity_boost": 0.75},
    {"stability": 0.5},
    None,
]
GAIN = 1.3
DONE = os.path.join(HERE, "voiced.json")      # clip names already in her voice
SAMPLES = os.path.join(HERE, "samples")


def load_done():
    try:
        with open(DONE, encoding="utf-8") as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


def save_done(done):
    with open(DONE, "w", encoding="utf-8") as f:
        json.dump(sorted(done), f, indent=0)


class Speaker:
    def __init__(self, key):
        self.key = key
        self.settings_at = 0

    def _post(self, text, settings):
        body = {"text": text, "model_id": MODEL_ID}
        if settings is not None:
            body["voice_settings"] = settings
        req = urllib.request.Request(f"{API}/text-to-speech/{VOICE_ID}?output_format={OUTPUT_FORMAT}",
                                     data=json.dumps(body).encode("utf-8"), method="POST",
                                     headers={"xi-api-key": self.key, "Content-Type": "application/json",
                                              "Accept": "audio/mpeg"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()

    def say(self, text):
        while True:
            try:
                return self._post(text, SETTINGS[self.settings_at])
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace")
                # A refusal of the settings, not of the key or the quota: try the next set.
                if e.code in (400, 422) and "setting" in detail.lower() and self.settings_at + 1 < len(SETTINGS):
                    self.settings_at += 1
                    print(f"  {MODEL_ID} refused those voice settings; now using {SETTINGS[self.settings_at]}")
                    continue
                raise urllib.error.HTTPError(e.url, e.code, detail, e.headers, None)


def to_ogg(ffmpeg, mp3, out):
    part = out + ".tmp.ogg"
    r = subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", mp3,
                        "-af", f"volume={GAIN},alimiter=limit=0.98", "-ac", "1",
                        "-c:a", "libvorbis", "-q:a", "2", part])
    if r.returncode != 0 or not os.path.getsize(part):
        return False
    os.replace(part, out)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true", help="generate (spends credits)")
    ap.add_argument("--sample", type=int, help="make N clips into tools/samples/ to listen to first")
    ap.add_argument("--only", help="comma-separated categories")
    ap.add_argument("--ffmpeg")
    args = ap.parse_args()
    cats = set(args.only.split(",")) if args.only else None

    done = load_done()
    todo = [(name, cat, lines.prompt(cat, int(name[len(lines.PREFIX) + len(cat):]), text))
            for name, cat, text in lines.all_lines()
            if (not cats or cat in cats) and name not in done]
    if args.sample:
        # Spread across the warnings: the first clip of each, then the second...
        by_cat = {}
        for item in todo:
            by_cat.setdefault(item[1], []).append(item)
        picked, rank = [], 0
        while len(picked) < args.sample and any(rank < len(v) for v in by_cat.values()):
            for v in by_cat.values():
                if rank < len(v) and len(picked) < args.sample:
                    picked.append(v[rank])
            rank += 1
        todo = picked

    chars = sum(len(t) for _, _, t in todo)
    print(f"{len(todo)} clip(s), {chars} characters, model {MODEL_ID}, voice {VOICE_ID}.")
    if not (args.go or args.sample):
        for name, _, text in todo:
            print(f"  {name}: {text}")
        print("Dry run: nothing sent. --sample N to hear a few first, --go to generate.")
        return
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY first (it starts with sk_).")
    ffmpeg = find_ffmpeg(args.ffmpeg)
    speaker = Speaker(key)
    if args.sample:
        os.makedirs(SAMPLES, exist_ok=True)

    made = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, _, text) in enumerate(todo, 1):
            try:
                audio = speaker.say(text)
            except urllib.error.HTTPError as e:
                detail = str(e.msg).lower()
                if "quota" in detail or e.code in (402, 429) or "credit" in detail:
                    print(f"[{i}/{len(todo)}] quota or rate limit reached ({e.code}). Stopping; re-run later.")
                    break
                if e.code == 401 or "api_key" in detail:
                    sys.exit(f"The API key was refused ({e.code}): {e.msg[:200]}")
                print(f"[{i}/{len(todo)}] {name}: HTTP {e.code} {e.msg[:200]}")
                continue
            mp3 = os.path.join(tmp, name + ".mp3")
            with open(mp3, "wb") as f:
                f.write(audio)
            out = os.path.join(SAMPLES if args.sample else lines.SOUNDS, name + ".ogg")
            if not to_ogg(ffmpeg, mp3, out):
                print(f"[{i}/{len(todo)}] {name}: conversion failed")
                continue
            if not args.sample:
                done.add(name)
                save_done(done)
            made += 1
            print(f"[{i}/{len(todo)}] {name}  {text}")
            time.sleep(0.3)
    if args.sample:
        print(f"\n{made} sample(s) in {SAMPLES}. Listen, then run --go.")
        return
    lines.write_counts(ffmpeg)
    print(f"\n{made} clip(s) now in Trixie's voice. Restart the game client: "
          "a /reload does not pick up changed sound files.")


if __name__ == "__main__":
    main()
