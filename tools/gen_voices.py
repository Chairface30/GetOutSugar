#!/usr/bin/env python3
"""Trixie's real voice from ElevenLabs, replacing the test clips. SPENDS CREDITS.

Same voice and settings as the Casino's Trixie (Chairfaces Casino/tools/
gen_trixie_voices.py): model eleven_multilingual_v2, stability 0.45,
similarity 0.75, style 0.35, speaker boost on. Lines come from lines.py.

Nothing is sent without --go. Without it, this only lists what would be made
and how many characters that costs.

Each clip is fetched as mp3, then made louder (ElevenLabs output is quiet, about
-24 dB; +30% with a limiter, as the Casino's amplify_voices.py does) and saved
as Ogg over the test clip of the same name. A clip counts as done once a
marker says it is the real voice, so a run that hits the monthly quota can be
re-run next month and picks up where it stopped.

  set ELEVENLABS_API_KEY=...                      (never written to any file)
  python tools/gen_voices.py                      # dry run: what, and how many characters
  python tools/gen_voices.py --go                 # generate every clip still on a test voice
  python tools/gen_voices.py --go --only fire,cc
"""
import argparse, json, os, subprocess, sys, tempfile, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines
from make_test_tracks import find_ffmpeg

API = "https://api.elevenlabs.io/v1"
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "Z3R5wn05IrDiVCyEkUrK")
MODEL_ID = "eleven_multilingual_v2"
OUTPUT_FORMAT = "mp3_44100_128"
VOICE_SETTINGS = {"stability": 0.45, "similarity_boost": 0.75,
                  "style": 0.35, "use_speaker_boost": True}
GAIN = 1.3
DONE = os.path.join(HERE, "voiced.json")     # clip names already in the real voice


def load_done():
    try:
        with open(DONE, encoding="utf-8") as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


def save_done(done):
    with open(DONE, "w", encoding="utf-8") as f:
        json.dump(sorted(done), f, indent=0)


def tts(key, text):
    body = json.dumps({"text": text, "model_id": MODEL_ID,
                       "voice_settings": VOICE_SETTINGS}).encode("utf-8")
    req = urllib.request.Request(f"{API}/text-to-speech/{VOICE_ID}?output_format={OUTPUT_FORMAT}",
                                 data=body, method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json",
                                          "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true", help="actually generate (spends credits)")
    ap.add_argument("--only", help="comma-separated categories")
    ap.add_argument("--ffmpeg")
    args = ap.parse_args()
    cats = set(args.only.split(",")) if args.only else None

    done = load_done()
    todo = [(n, c, t) for n, c, t in lines.all_lines()
            if (not cats or c in cats) and n not in done]
    chars = sum(len(t) for _, _, t in todo)
    print(f"{len(todo)} clip(s) still on a test voice, {chars} characters.")
    if not args.go:
        print("Dry run: nothing sent. Add --go to generate.")
        return
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY first.")
    ffmpeg = find_ffmpeg(args.ffmpeg)

    made = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, _, text) in enumerate(todo, 1):
            try:
                audio = tts(key, text)
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace").lower()
                if "quota" in detail or e.code in (402, 429) or "credit" in detail:
                    print(f"[{i}/{len(todo)}] quota or rate limit reached ({e.code}). Stopping; re-run later.")
                    break
                if e.code == 401:
                    sys.exit("401: the API key is invalid or was rotated.")
                print(f"[{i}/{len(todo)}] {name}: HTTP {e.code}")
                continue
            mp3 = os.path.join(tmp, name + ".mp3")
            with open(mp3, "wb") as f:
                f.write(audio)
            out = os.path.join(lines.SOUNDS, name + ".ogg")
            part = out + ".tmp.ogg"
            r = subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", mp3,
                                "-af", f"volume={GAIN},alimiter=limit=0.98", "-ac", "1",
                                "-c:a", "libvorbis", "-q:a", "2", part])
            if r.returncode != 0 or not os.path.getsize(part):
                print(f"[{i}/{len(todo)}] {name}: conversion failed")
                continue
            os.replace(part, out)
            done.add(name)
            save_done(done)
            made += 1
            print(f"[{i}/{len(todo)}] {name}")
            time.sleep(0.3)
    lines.write_counts(ffmpeg)
    print(f"\n{made} clip(s) now in Trixie's voice. Restart the game client: "
          "a /reload does not pick up changed sound files.")


if __name__ == "__main__":
    main()
