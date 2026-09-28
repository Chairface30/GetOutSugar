-- Get Out, Sugar: Catalog.lua
-- Every warning: its name in the options, what sets it off, and how urgent it
-- is. Urgency only orders the queue: while Trixie is speaking, a danger line
-- waits ahead of a moment. The clips for each are counted in Counts.lua,
-- which the tools write from what is on disk.

local _, ns = ...

ns.CATALOG = {
    -- Danger: said the moment it happens.
    { cat = "fire",        prio = "danger", label = "Standing in something",
      desc = "Several magic-damage hits within three seconds, which is what standing in fire, poison or void feels like. Best effort: this client has no combat log to say what hit you, so a damage-over-time spell can set it off too." },
    { cat = "cc",          prio = "danger", label = "Stunned, feared or silenced",
      desc = "You lose control of your character: stuns, fears, silences, roots and the like." },
    { cat = "fatigue",     prio = "danger", label = "Too far out to sea",
      desc = "The fatigue bar appears: you have swum too far from land." },

    -- Moments.
    { cat = "death",       prio = "situation", label = "You died" },
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
