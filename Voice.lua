-- Get Out, Sugar: Voice.lua
-- Plays one of Trixie's lines for a warning, one line at a time.
--
-- Every warning that is on gets its line: there are no cooldowns. What there
-- is instead is a queue. While she is speaking, the next warning waits for
-- her to finish, so two lines never play over each other. Danger waits at the
-- front of the queue, ahead of the moments. A warning she is already saying,
-- or already has waiting, is not queued twice, and one that has waited too
-- long is dropped: the moment it was about has passed.
--
-- A pull countdown is the one thing that does not wait its turn: each number
-- has to land on its second, so it cuts off whatever she was saying, and the
-- queue holds until she has said "Go".
--
-- The client cannot say how long a sound is, so each clip's length comes from
-- Counts.lua, measured by the tools when the clips were made.

local _, ns = ...
local Voice = {}
ns.Voice = Voice

local GAP = 0.15          -- a breath between one line and the next
local MAX_WAIT = 8        -- seconds a queued line stays worth saying
local MAX_QUEUE = 3
local FALLBACK = 4.5      -- a clip whose length is unknown
local PRIORITY = { danger = 2, situation = 1 }
local FOLDER = "Interface\\AddOns\\" .. ns.addonName .. "\\Sounds\\gos_"

local playing             -- { handle, cat, ends }
local queue = {}          -- { cat, prio, at }, in the order they will play
local lastClip = {}       -- cat -> the clip number last played
local generation = 0      -- bumped on every start, so a stale finish timer does nothing
local counting = nil      -- the count running, while she counts a pull down
Voice.queue = queue

function Voice.Speaking()
    return playing ~= nil and GetTime() < playing.ends
end

local Next

local function Start(cat, clip)
    local count = ns.COUNTS and ns.COUNTS[cat] or 0
    if count < 1 then return false end
    if not clip then
        clip = math.random(1, count)
        if count > 1 and clip == lastClip[cat] then clip = clip % count + 1 end
    elseif clip > count then
        return false
    end

    local ok, willPlay, handle = pcall(PlaySoundFile, FOLDER .. cat .. clip .. ".ogg", ns.db.channel or "Dialog")
    if not (ok and willPlay) then return false end
    local length = ns.SECONDS and ns.SECONDS[cat] and ns.SECONDS[cat][clip] or FALLBACK
    local now = GetTime()
    playing = { handle = handle, cat = cat, ends = now + length + GAP }
    lastClip[cat] = clip
    generation = generation + 1
    local mine = generation
    C_Timer.After(length + GAP, function()
        if generation == mine then Next() end
    end)
    return true, clip
end

-- The line has run its length: on to the next one waiting, if any still is.
function Next()
    playing = nil
    if counting then return end
    local now = GetTime()
    while #queue > 0 do
        local item = table.remove(queue, 1)
        if now - item.at <= MAX_WAIT and not (ns.db.muted) and ns.IsOn(item.cat) then
            if Start(item.cat) then return end
        end
    end
end

-- opts.preview: the options' Play button and /trixie test. Plays even when
-- the warning is off or muted, and straight away: whatever she was saying
-- stops and the queue is cleared, so presses never stack up.
function Voice.Play(cat, opts)
    opts = opts or {}
    local db = ns.db
    if not (db and ns.CATEGORY[cat]) then return false end

    if opts.preview then
        Voice.Stop()
        if cat == "count" then return Voice.Count(3, true) end
        return Start(cat)
    end
    if db.muted or not ns.IsOn(cat) then return false end

    if not Voice.Speaking() and #queue == 0 and not counting then
        return Start(cat)
    end
    if playing and playing.cat == cat then return false end
    for _, item in ipairs(queue) do
        if item.cat == cat then return false end
    end
    local prio = PRIORITY[ns.CATEGORY[cat].prio] or 1
    local at = #queue + 1
    for i, item in ipairs(queue) do
        if prio > item.prio then at = i break end
    end
    table.insert(queue, at, { cat = cat, prio = prio, at = GetTime() })
    while #queue > MAX_QUEUE do table.remove(queue) end
    return true, "queued"
end

function Voice.Stop()
    if playing and playing.handle then pcall(StopSound, playing.handle) end
    playing = nil
    generation = generation + 1
    counting = nil
    wipe(queue)
end

-- One exact clip, now: whatever she was saying is cut off.
local function Say(cat, clip)
    if playing and playing.handle then pcall(StopSound, playing.handle) end
    playing = nil
    return Start(cat, clip)
end

-- Clips of the "count" warning: clip n says n, and the one after ten says go.
Voice.GO = 11

-- Counts a pull down out loud: from ten, or from however many whole seconds
-- are left if fewer, then "Go" when `remaining` runs out. A new count
-- replaces the one running. preview: the Play button, which counts even
-- while muted or switched off.
function Voice.Count(remaining, preview)
    remaining = tonumber(remaining)
    if not remaining or remaining < 1 then return false end
    local mine = {}
    counting = mine
    local function Tick(clip, last)
        if counting ~= mine then return end
        if preview or (not ns.db.muted and ns.IsOn("count")) then Say("count", clip) end
        if last then
            counting = nil
            if not Voice.Speaking() then Next() end
        end
    end
    for n = math.min(10, math.floor(remaining)), 1, -1 do
        C_Timer.After(remaining - n, function() Tick(n) end)
    end
    C_Timer.After(remaining, function() Tick(Voice.GO, true) end)
    return true
end

-- The pull was called off: she stops counting, mid-number too.
function Voice.CancelCount()
    if not counting then return end
    counting = nil
    if playing and playing.cat == "count" then
        if playing.handle then pcall(StopSound, playing.handle) end
        playing = nil
        generation = generation + 1
    end
    if not Voice.Speaking() then Next() end
end

function Voice.Counting()
    return counting ~= nil
end
