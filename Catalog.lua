-- Get Out, Sugar: Catalog.lua
-- Every warning: its name in the options, what sets it off, how urgent it is,
-- and how long before the same warning may play again.
--
-- `prio` decides what happens when two want to play at once: a danger line
-- cuts off a situational one, never the other way round. The clips for each
-- are counted in Counts.lua, which the tools write from what is on disk.

local _, ns = ...

ns.CATALOG = {
    -- Danger: short lines, played the moment it happens.
    { cat = "fire",        prio = "danger", cd = 6,  label = "Standing in something",
      desc = "Several magic-damage hits in a few seconds, which is what standing in fire, poison or void feels like. Best effort: this client has no combat log to say what hit you, so a damage-over-time spell can set it off too." },
    { cat = "big_hit",     prio = "danger", cd = 8,  label = "A big hit",
      desc = "One hit of 30% or more of your maximum health." },
    { cat = "aggro",       prio = "danger", cd = 5,  label = "You pulled aggro",
      desc = "A monster turns on you and you are not the tank. Only in a group, unless you tick Aggro warnings when solo." },
    { cat = "aggro_close", prio = "danger", cd = 8,  label = "About to pull aggro",
      desc = "Your threat reaches 90% of what it takes to pull a monster off the tank." },
    { cat = "tank_lost",   prio = "danger", cd = 5,  label = "Tank: a monster got away",
      desc = "Your group role is Tank and a monster you were holding turns to someone else." },
    { cat = "cc",          prio = "danger", cd = 6,  label = "Stunned, feared or silenced",
      desc = "You lose control of your character: stuns, fears, silences, roots and the like." },
    { cat = "boss_you",    prio = "danger", cd = 4,  label = "The boss picked you",
      desc = "A boss whispers a warning to you, which is how bosses tell a player they are the target." },
    { cat = "boss_emote",  prio = "danger", cd = 6,  label = "Boss warning",
      desc = "A boss announces a big move in the middle of the screen." },
    { cat = "drowning",    prio = "danger", cd = 12, label = "Drowning",
      desc = "Your breath bar appears, and again when it is nearly empty." },
    { cat = "fatigue",     prio = "danger", cd = 15, label = "Too far out to sea",
      desc = "The fatigue bar appears: you have swum too far from land." },

    -- Situational: moments rather than emergencies.
    { cat = "death",       prio = "situation", cd = 10,  label = "You died" },
    { cat = "pull",        prio = "situation", cd = 10,  label = "Boss fight starts" },
    { cat = "wipe",        prio = "situation", cd = 10,  label = "Boss fight lost" },
    { cat = "kill",        prio = "situation", cd = 10,  label = "Boss defeated" },
    { cat = "durability",  prio = "situation", cd = 600, label = "Gear about to break",
      desc = "A piece of your gear is down to 20% durability or less." },
    { cat = "ready_check", prio = "situation", cd = 5,   label = "Ready check",
      desc = "Someone else starts a ready check." },
    { cat = "range",       prio = "situation", cd = 8,   label = "Out of range or not facing",
      desc = "The game tells you your target is out of range, out of sight, or behind you." },
}

ns.CATEGORY = {}
for _, entry in ipairs(ns.CATALOG) do ns.CATEGORY[entry.cat] = entry end
