
CREATE TABLE IF NOT EXISTS new_stats (
    actor_id TEXT PRIMARY KEY,
    hp_max INT NOT NULL,
    hp INT NOT NULL,
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
    actor_id, hp_max, hp,
    grit, flow, mind, soul,
    phy_armor, mag_armor, phy_armor_max, mag_armor_max,
    exp, lvl, pp
)
SELECT
actor_id, hp_max, hp,
grit, flow, mind, soul,
phy_armor, mag_armor, phy_armor_max, mag_armor_max,
exp, lvl, pp
FROM stats;

DROP TABLE stats;
ALTER TABLE new_stats RENAME TO stats;
