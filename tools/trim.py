#!/usr/bin/env python3
"""The silence cut from both ends of the count clips.

Voice.Count plays each number on its second, so a number has to start the
moment it is played (the voice comes back with a fifth of a second of quiet
in front) and be over before the next (and with as much behind). Only the
"count" clips are trimmed: the other lines are queued by their length, and a
breath either side does them no harm.

  python tools/trim.py          # trim the count clips in Sounds/
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lines
import level

THRESHOLD = "-40dB"
KEEP = 0.02          # seconds of quiet left at each end


def trim(ffmpeg, path):
    """Cuts the quiet off both ends of one clip, in place, and levels it
    again: without the quiet the same voice measures louder."""
    edge = f"silenceremove=start_periods=1:start_threshold={THRESHOLD}:start_silence={KEEP}"
    chain = f"{edge},areverse,{edge},areverse"
    fd, tmp = tempfile.mkstemp(suffix=".ogg", dir=os.path.dirname(path))
    os.close(fd)
    try:
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", path, "-af", chain,
                        "-c:a", "libvorbis", "-q:a", level.QUALITY, tmp], check=True)
        os.replace(tmp, path)
        level.level(ffmpeg, path, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def trim_counts(ffmpeg):
    names = [name for name, cat, _ in lines.all_lines() if cat == "count"]
    for name in names:
        path = os.path.join(lines.SOUNDS, name + ".ogg")
        if os.path.exists(path):
            trim(ffmpeg, path)
    return names


if __name__ == "__main__":
    ffmpeg = lines.find_ffmpeg()
    if not ffmpeg:
        sys.exit("ffmpeg not found (set FFMPEG)")
    print(f"trimmed {len(trim_counts(ffmpeg))} count clip(s)")
    lines.write_counts(ffmpeg)
