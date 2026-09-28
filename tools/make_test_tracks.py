#!/usr/bin/env python3
"""Placeholder clips for testing, spoken by Windows' own voice. Costs nothing.

Every line in lines.py is said by Microsoft Zira (System.Speech, built into
Windows), prefixed with its warning's name so you can tell in game which one
fired: "fire. Get out of the fire, sugar!". Each is converted to Ogg under
the final file name, Sounds/gos_<category><n>.ogg, so putting the real voice
in later is only a matter of replacing files. Counts.lua is rewritten from
what landed on disk.

Needs ffmpeg with libvorbis: the FFMPEG environment variable, --ffmpeg, or the
copy that ships with Lian-Li's L-Connect on this machine.

  python tools/make_test_tracks.py              # make every missing clip
  python tools/make_test_tracks.py --force      # remake them all
  python tools/make_test_tracks.py --only fire,cc
"""
import argparse, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines

# One PowerShell run speaks every line: starting PowerShell per clip would take
# minutes. The list arrives as a JSON file of [wav path, text] pairs.
SPEAK = r"""
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { $s.SelectVoice('Microsoft Zira Desktop') } catch {}
$s.Rate = 1
$items = Get-Content -Raw -Encoding UTF8 $args[0] | ConvertFrom-Json
foreach ($it in $items) {
    $s.SetOutputToWaveFile($it[0])
    $s.Speak($it[1])
}
$s.SetOutputToNull()
"""


def find_ffmpeg(arg=None):
    found = lines.find_ffmpeg(arg)
    if not found:
        sys.exit("ffmpeg not found: set FFMPEG or pass --ffmpeg")
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", help="comma-separated categories")
    ap.add_argument("--ffmpeg")
    args = ap.parse_args()
    ffmpeg = find_ffmpeg(args.ffmpeg)
    cats = set(args.only.split(",")) if args.only else None

    os.makedirs(lines.SOUNDS, exist_ok=True)
    todo = [(name, cat, text) for name, cat, text in lines.all_lines()
            if (not cats or cat in cats)
            and (args.force or not os.path.exists(os.path.join(lines.SOUNDS, name + ".ogg")))]
    print(f"{len(todo)} test clip(s) to make")
    if todo:
        with tempfile.TemporaryDirectory() as tmp:
            items = [[os.path.join(tmp, name + ".wav"), f"{cat.replace('_', ' ')}. {text}"]
                     for name, cat, text in todo]
            listing = os.path.join(tmp, "items.json")
            with open(listing, "w", encoding="utf-8") as f:
                json.dump(items, f)
            script = os.path.join(tmp, "speak.ps1")
            with open(script, "w", encoding="utf-8-sig") as f:
                f.write(SPEAK)
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                            "-File", script, listing], check=True)
            made = 0
            for (name, _, _), (wav, _) in zip(todo, items):
                out = os.path.join(lines.SOUNDS, name + ".ogg")
                r = subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                                    "-i", wav, "-ac", "1", "-c:a", "libvorbis", "-q:a", "2", out])
                if r.returncode == 0 and os.path.getsize(out) > 0:
                    made += 1
                else:
                    print(f"  failed: {name}")
            print(f"made {made}/{len(todo)}")
    counts = lines.write_counts(ffmpeg)
    print("Counts.lua:", ", ".join(f"{c} {n}" for c, n in counts.items()))


if __name__ == "__main__":
    main()
