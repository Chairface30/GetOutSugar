-- Get Out, Sugar: Voice.lua
-- Plays one of Trixie's lines for a warning.
--
-- Adapted from the Casino's Lobby:PlayTrixieVoice: one line at a time, a
-- cooldown per warning, a random clip that is not the one just played. Added
-- here is priority: while a line is playing, a more urgent warning stops it
-- and plays over it, and a less or equally urgent one is dropped.
--
-- The client has no way to ask how long a sound is, so a line is assumed to
-- take CLIP_TIME. The generated clips run two to four seconds.

local _, ns = ...
local Voice = {}
ns.Voice = Voice

local CLIP_TIME = 3.5
local PRIORITY = { danger = 2, situation = 1 }
local FOLDER = "Interface\\AddOns\\" .. ns.addonName .. "\\Sounds\\gos_"

local playing          -- { handle, prio, ends }
local lastAt = {}      -- cat -> when it last played
local lastClip = {}    -- cat -> the clip number last played
Voice.lastAt = lastAt

function Voice.Reset()
    playing = nil
    wipe(lastAt)
    wipe(lastClip)
end

-- opts.preview: the options' Play button and /trixie test. Plays even when
--   the warning is off or muted, and ignores its cooldown.
-- opts.again: ignores the warning's own cooldown (drowning's second call).
function Voice.Play(cat, opts)
    opts = opts or {}
    local db = ns.db
    local info = ns.CATEGORY[cat]
    local count = ns.COUNTS and ns.COUNTS[cat] or 0
    if not (db and info) or count < 1 then return false end
    if not opts.preview and (db.muted or not ns.IsOn(cat)) then return false end

    local now = GetTime()
    if not (opts.preview or opts.again) then
        local cd = (info.cd or 5) * (tonumber(db.chatty) or 1)
        if lastAt[cat] and now - lastAt[cat] < cd then return false end
    end

    local prio = PRIORITY[info.prio] or 1
    if playing and now < playing.ends then
        if not opts.preview and prio <= playing.prio then return false end
        if playing.handle then pcall(StopSound, playing.handle) end
        playing = nil
    end

    local clip = math.random(1, count)
    if count > 1 and clip == lastClip[cat] then clip = clip % count + 1 end

    local ok, willPlay, handle = pcall(PlaySoundFile, FOLDER .. cat .. clip .. ".ogg", db.channel or "Dialog")
    if not (ok and willPlay) then return false end
    playing = { handle = handle, prio = prio, ends = now + CLIP_TIME }
    lastAt[cat] = now
    lastClip[cat] = clip
    return true, clip
end

function Voice.Stop()
    if playing and playing.handle then pcall(StopSound, playing.handle) end
    playing = nil
end
