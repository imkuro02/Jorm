class StatType:
    HPMAX =     'hp_max'
    #MPMAX =     'mp_max'
    HP =        'hp'
    #MP =        'mp'
    GRIT =      'grit'
    FLOW =      'flow'
    MIND =      'mind'
    SOUL =      'soul'
    PHYARMOR =     'phy_armor'
    MAGARMOR =    'mag_armor'
    PHYARMORMAX =     'phy_armor_max'
    MAGARMORMAX =    'mag_armor_max'
    EXP =       'exp'
    LVL =       'lvl'
    PP =        'pp'
    INVSLOTS = 'inv_slots'


    # not saved in db
    THREAT =    'threat'
    INITIATIVE = 'initiative'

    name = {
        HP:     'Life',
        HPMAX:  'Max Life',

        PHYARMOR:  'Hold',
        MAGARMOR:  'Ward',

        PHYARMORMAX:  'Max Hold',
        MAGARMORMAX: 'Max Ward',

        GRIT:   'Grit',
        FLOW:   'Flow',
        MIND:   'Mind',
        SOUL:   'Soul',
        
        EXP:    'Experience',
        LVL:    'Level',
        PP:     'Practice Points',

        INVSLOTS: 'Bag Space',

        # not saved in db
        THREAT: 'Threat',
        INITIATIVE: 'Initiative'
    }

StatBonus = {
    StatType.GRIT: {
        StatType.HP: 4,
        StatType.PHYARMOR: 2,
        StatType.MAGARMOR: 0,
    },
    StatType.FLOW: {
        StatType.HP: 3,
        StatType.PHYARMOR: 2,
        StatType.MAGARMOR: 1,
    },
    StatType.MIND: {
        StatType.HP: 3,
        StatType.PHYARMOR: 0,
        StatType.MAGARMOR: 3,
    },
    StatType.SOUL: {
        StatType.HP: 3,
        StatType.PHYARMOR: 1,
        StatType.MAGARMOR: 2,
    },
}
