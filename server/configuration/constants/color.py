from configuration.constants.stat_type import StatType
class Color:
    NORMAL = "@normal"
    BACK = "@back"
    ERROR = "@bgred"

    GOOD = "@bgreen"
    BAD = "@bpurple"

    IMPORTANT = "@yellow"

    TOOLTIP = "@tip"
    DESCRIPTION = "@cyan"

    NAME_ADMIN = "@bgreen"
    NAME_PLAYER = "@bcyan"
    NAME_ENEMY = "@yellow"
    NAME_NPC = "@byellow"

    NAME_ROOM_NORMAL = "@bwhite"
    NAME_ROOM_SAFE = "@bgreen"
    NAME_ROOM_INSTANCE = "@bred"
    DESC_ROOM = "@cyan"

    NAME_QUEST = "@bgreen"
    DESC_QUEST = "@cyan"

    MAP_PLAYER = NAME_PLAYER
    MAP_IMPORTANT = NORMAL
    MAP_NORMAL = NORMAL
    MAP_WALL = "@wall"
    MAP_WALL_INSTANCED = "@bgpurple"
    MAP_ROOM = "@yellow"
    MAP_PATH = "@yellow"

    ITEM_KEEP = "@red"
    ITEM_EQUIPPED = "@green"
    ITEM_TRADING = "@yellow"
    ITEM_NEW = "@yellow"
    ITEM_MATERIAL = "@byellow"

    DAMAGE_PURE = "@byellow"
    DAMAGE_PHY = "@bred"
    DAMAGE_MAG = "@bcyan"
    DAMAGE_HEAL = "@bgreen"

    COMBAT_TURN = "@bred"
    COMBAT_IMPORTANT = "@bgred"

    stat = {
        StatType.HP: "@bgreen",
        StatType.PHYARMOR: "@byellow",
        StatType.MAGARMOR: "@bcyan",
    }
    # STAT_HP =               '@bred'
    # STAT_MP =               '@bcyan'
    # STAT_PHY_ARM =          '@red'
    # STAT_MAG_ARM =          '@bblue'
    # STAT_GRIT =             NORMAL
    # STAT_FLOW =             NORMAL
    # STAT_MIND =             NORMAL
    # STAT_SOUL =             NORMAL
    # STAT_EXPERIENCE =       NORMAL
    # STAT_PRACTICE_POINTS =  NORMAL
    # STAT_BAG_SPACE =        NORMAL