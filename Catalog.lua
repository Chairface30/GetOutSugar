-- Get Out, Sugar: Catalog.lua
-- Every warning: its name in the options, what sets it off, and how urgent it
-- is. Urgency only orders the queue: while Trixie is speaking, a danger line
-- waits ahead of a moment. The clips for each are counted in Counts.lua,
-- which the tools write from what is on disk.

local _, ns = ...

ns.CATALOG = {
    -- Danger: said the moment it happens.
    -- Crowd control, one warning per kind the game reports.
    { cat = "cc_stun",     prio = "danger", label = "Stunned" },
    { cat = "cc_fear",     prio = "danger", label = "Feared" },
    { cat = "cc_incap",    prio = "danger", label = "Incapacitated",
      desc = "Polymorphed, sapped, gouged, asleep or disoriented." },
    { cat = "cc_charm",    prio = "danger", label = "Mind controlled",
      desc = "Charmed or possessed: someone else is steering you." },
    { cat = "cc_silence",  prio = "danger", label = "Silenced" },
    { cat = "cc_root",     prio = "danger", label = "Rooted" },
    { cat = "cc_disarm",   prio = "danger", label = "Disarmed" },
    { cat = "cc",          prio = "danger", label = "Other crowd control",
      desc = "Any other loss of control, or one whose kind the game keeps hidden." },
    { cat = "fatigue",     prio = "danger", label = "Too far out to sea",
      desc = "The fatigue bar appears: you have swum too far from land." },

    -- Moments.
    { cat = "death",       prio = "situation", label = "You died" },
    { cat = "countdown",   prio = "situation", label = "Pull countdown starts",
      desc = "Someone starts a pull timer: /pull, the countdown button, or a boss mod's pull timer that uses the game's countdown." },
    { cat = "pull",        prio = "situation", label = "Boss fight starts" },
    { cat = "wipe",        prio = "situation", label = "Boss fight lost" },
    { cat = "kill",        prio = "situation", label = "Boss defeated" },
    { cat = "durability",  prio = "situation", label = "Gear about to break",
      desc = "A piece of your gear drops to 20% durability or less." },
    { cat = "ready_check", prio = "situation", label = "Ready check",
      desc = "Someone else starts a ready check. Trixie replaces the game's own ready check sound while this is on." },
}

ns.CATEGORY = {}
for _, entry in ipairs(ns.CATALOG) do ns.CATEGORY[entry.cat] = entry end
