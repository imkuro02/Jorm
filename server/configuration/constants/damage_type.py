
class DamageType:
    PHYSICAL = "dmg_physical"
    MAGICAL = "dmg_magical"
    HEALING = "dmg_healing"
    PURE = "dmg_pure"
    CANCELLED = "dmg_cancelled"  # Cancels all damage
    name = {
        PHYSICAL: "physical damage",
        MAGICAL: "magical damage",
        HEALING: "healing",
        PURE: "pure damage",
        CANCELLED: "cancelled????",
    }