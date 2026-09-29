#!/usr/bin/env python3
"""Every clip at the same loudness, and loud enough to hear over a fight.

The voice comes back from ElevenLabs at whatever level the delivery had: a
sighed line can sit 14 dB under a shouted one, and the peaks are already at
full scale, so turning a quiet clip up is not possible without squeezing it.
Each clip is therefore:

  1. brought to a common level, so the compressor treats them all alike
  2. high-passed (rumble below the voice only costs headroom)
  3. compressed, 4:1 over the loud parts, so the limiter has little left to do
  4. turned up until its loudness (EBU R128, integrated) is TARGET
  5. limited, so no peak passes CEILING

Step 4 is repeated, because the limiter takes back some of what the gain
gave, until the clip measures within TOLERANCE of TARGET.

  python tools/level.py                  # level the clips in Sounds/ that are off target
  python tools/level.py --check          # measure only; exit 1 if any clip is off
  python tools/level.py --src DIR        # level from untouched originals in DIR into Sounds/
  python tools/level.py --target -14     # another loudness

Levelling a clip decodes and re-encodes it, which costs a little quality each
time, so clips already on target are left alone, and --src is the better way
to change the target: keep the originals and level from those.
"""
import argparse, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines

TARGET = -12.0       # LUFS, integrated
CEILING = -1.5       # dBFS, what the limiter holds peaks to
TOLERANCE = 0.5      # LU either side of TARGET counts as on target
PEAK_SLACK = 1.0     # dB over CEILING allowed after encoding (Vorbis moves peaks a little)
NOMINAL = -20.0      # LUFS each clip is brought to before the compressor
QUALITY = "5"        # libvorbis -q:a


def run(ffmpeg, args):
    return subprocess.run([ffmpeg, "-hide_banner", "-nostats"] + args, capture_output=True,
                          text=True, errors="replace")


def read(report):
    """Loudness and peak from ffmpeg's ebur128 and astats reports."""
    def last(pattern):
        found = re.findall(pattern, report)
        return float(found[-1]) if found else None
    return {"lufs": last(r"I:\s+(-?[\d.]+) LUFS"),
            "peak": last(r"Peak level dB: (-?[\d.]+)"),
            "rms": last(r"RMS level dB: (-?[\d.]+)")}


def measure(ffmpeg, path, chain=None):
    """A file's loudness and peak, as it is or after a filter chain."""
    af = (chain + "," if chain else "") + "astats=measure_perchannel=none,ebur128"
    return read(run(ffmpeg, ["-i", path, "-af", af, "-f", "null", "-"]).stderr)


def chain_for(pre, gain, limit=CEILING):
    """The filters for one clip. limit is the limiter's ceiling in dB, or None for no limiter."""
    parts = [f"volume={pre:.2f}dB",
             "highpass=f=70",
             "acompressor=threshold=-24dB:ratio=4:knee=6dB:attack=3:release=150",
             f"volume={gain:.2f}dB"]
    if limit is not None:
        parts.append(f"alimiter=limit={limit:.2f}dB:attack=5:release=60:level=false")
    return ",".join(parts)


def level(ffmpeg, src, out, target=TARGET):
    """src, levelled, to out (Ogg Vorbis, mono). Returns what was done, or None."""
    before = measure(ffmpeg, src)
    if before["lufs"] is None:
        return None
    pre = NOMINAL - before["lufs"]
    gain = target - NOMINAL
    limit = CEILING
    part = out + ".tmp.ogg"
    after = None
    # Encoding moves the peaks, now and then by more than a dB: if the encoded
    # clip peaks too high, the limiter is set lower by that much and it is made again.
    for _ in range(5):
        for _ in range(12):
            got = measure(ffmpeg, src, chain_for(pre, gain, limit))
            if got["lufs"] is None:
                return None
            off = target - got["lufs"]
            if abs(off) <= 0.1:
                break
            gain += off
        r = run(ffmpeg, ["-loglevel", "error", "-y", "-i", src, "-af", chain_for(pre, gain, limit),
                         "-ac", "1", "-ar", "44100", "-c:a", "libvorbis", "-q:a", QUALITY, part])
        if r.returncode != 0 or not os.path.exists(part) or not os.path.getsize(part):
            return None
        after = measure(ffmpeg, part)
        over = (after["peak"] or CEILING) - (CEILING + PEAK_SLACK)
        if over <= 0:
            break
        limit -= over + 0.2
    # How hard the limiter is working: the peak it would have let through.
    unlimited = measure(ffmpeg, src, chain_for(pre, gain, None))
    os.replace(part, out)
    return {"before": before["lufs"], "after": after["lufs"], "peak": after["peak"],
            "limited": max(0.0, (unlimited["peak"] or limit) - limit)}


def on_target(m, target=TARGET):
    return (m["lufs"] is not None and abs(m["lufs"] - target) <= TOLERANCE
            and (m["peak"] is None or m["peak"] <= CEILING + PEAK_SLACK))


def clips(folder):
    return sorted(f for f in os.listdir(folder) if f.endswith(".ogg") and not f.endswith(".tmp.ogg"))


def category(name):
    return re.sub(r"\d+\.ogg$", "", name)[len(lines.PREFIX):]


def table(rows, key):
    cats = {}
    for name, value in rows:
        cats.setdefault(category(name), []).append(value[key])
    print(f"  {'warning':12} {'clips':>5} {'quietest':>9} {'loudest':>8}")
    for cat, values in cats.items():
        print(f"  {cat:12} {len(values):>5} {min(values):>9.1f} {max(values):>8.1f}")
    every = [v for values in cats.values() for v in values]
    print(f"  {'all':12} {len(every):>5} {min(every):>9.1f} {max(every):>8.1f}   (LUFS)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="measure only")
    ap.add_argument("--src", help="folder of untouched originals to level from")
    ap.add_argument("--target", type=float, default=TARGET)
    ap.add_argument("--force", action="store_true", help="level clips that are already on target too")
    ap.add_argument("--ffmpeg")
    args = ap.parse_args()
    ffmpeg = lines.find_ffmpeg(args.ffmpeg)
    if not ffmpeg:
        sys.exit("ffmpeg not found: set FFMPEG or pass --ffmpeg")
    src = args.src or lines.SOUNDS
    names = clips(src)

    with ThreadPoolExecutor(8) as pool:
        if args.check:
            found = list(zip(names, pool.map(lambda n: measure(ffmpeg, os.path.join(lines.SOUNDS, n)), names)))
            table(found, "lufs")
            off = [(n, m) for n, m in found if not on_target(m, args.target)]
            for n, m in off:
                print(f"  off target: {n} {m['lufs']} LUFS, peak {m['peak']} dB")
            print(f"{len(found) - len(off)} of {len(found)} clips within {TOLERANCE} LU of {args.target} LUFS.")
            sys.exit(1 if off else 0)

        if args.src or args.force:
            todo = names
        else:
            found = list(zip(names, pool.map(lambda n: measure(ffmpeg, os.path.join(src, n)), names)))
            todo = [n for n, m in found if not on_target(m, args.target)]
        print(f"{len(todo)} of {len(names)} clip(s) to level to {args.target} LUFS.")
        done = list(zip(todo, pool.map(lambda n: level(ffmpeg, os.path.join(src, n),
                                                       os.path.join(lines.SOUNDS, n), args.target), todo)))
    failed = [n for n, d in done if d is None]
    done = [(n, d) for n, d in done if d is not None]
    if done:
        table(done, "after")
        hard = sorted(done, key=lambda nd: -nd[1]["limited"])[:5]
        print("  limiter worked hardest on: " + ", ".join(f"{n[:-4]} ({d['limited']:.1f} dB)" for n, d in hard))
    for n in failed:
        print(f"  FAILED: {n}")
    if done:
        lines.write_counts(ffmpeg)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
