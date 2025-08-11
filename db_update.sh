-- Step 1: Create the new table with armor_max and marmor_max
CREATE TABLE new_stats (
    actor_id TEXT PRIMARY KEY,
    hp_max INT NOT NULL,
    mp_max INT NOT NULL,
    hp INT NOT NULL,
    mp INT NOT NULL,
    grit INT NOT NULL,
    flow INT NOT NULL,
    mind INT NOT NULL,
    soul INT NOT NULL,
    armor INT NOT NULL,
    marmor INT NOT NULL,
    armor_max INT NOT NULL,
    marmor_max INT NOT NULL,
    exp INT NOT NULL,
    lvl INT NOT NULL,
    pp INT NOT NULL
);

-- Step 2: Copy data from old table, remapping armor/marmor
INSERT INTO new_stats (
    actor_id, hp_max, mp_max, hp, mp,
    grit, flow, mind, soul,
    armor, marmor, armor_max, marmor_max,
    exp, lvl, pp
)
SELECT
    actor_id, hp_max, mp_max, hp, mp,
    grit, flow, mind, soul,
    0, 0, armor, marmor,  -- Set armor and marmor to 0, move old values to *_max
    exp, lvl, pp
FROM stats;

-- Optional: Replace old table
DROP TABLE stats;
ALTER TABLE new_stats RENAME TO stats;



CREATE TABLE IF NOT EXISTS new_stats (
    actor_id TEXT PRIMARY KEY,
    hp_max INT NOT NULL,
    mp_max INT NOT NULL,
    hp INT NOT NULL,
    mp INT NOT NULL,
    grit INT NOT NULL,
    flow INT NOT NULL,
    mind INT NOT NULL,
    soul INT NOT NULL,
    phy_armor INT NOT NULL,
    mag_armor INT NOT NULL,
    phy_armor_max INT NOT NULL,
    mag_armor_max INT NOT NULL,
    exp INT NOT NULL,
    lvl INT NOT NULL,
    pp INT NOT NULL,
    FOREIGN KEY(actor_id) REFERENCES actors(actor_id)
);

INSERT INTO new_stats (
    actor_id, hp_max, mp_max, hp, mp,
    grit, flow, mind, soul,
    phy_armor, mag_armor, phy_armor_max, mag_armor_max,
    exp, lvl, pp
)
SELECT
    actor_id, hp_max, mp_max, hp, mp,
    grit, flow, mind, soul,
    armor, marmor, armor_max, marmor_max,
    exp, lvl, pp
FROM stats;

DROP TABLE stats;
ALTER TABLE new_stats RENAME TO stats;