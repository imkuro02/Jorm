from combat.combat_event import CombatEvent
#from configuration.constants.actor_status_type import ActorStatusType
#from configuration.constants.audio import Audio
from configuration.constants.damage_type import DamageType
#from configuration.constants.message_type import MessageType
from configuration.constants.stat_type import StatType

class Damage:
    def __init__(
        self,
        damage_taker_actor,
        damage_source_action,
        damage_source_actor,
        damage_value,
        damage_type,
        damage_to_stat=StatType.HP,
        silent=False,
        add_threat=True,
        combat_event=None,
        dont_proc=False,  # do not proc afflictions or item bonuses
    ):
        self.damage_source_action = damage_source_action
        self.damage_taker_actor = damage_taker_actor
        self.damage_source_actor = damage_source_actor

        # a negative value means the damage has been blocked by armor
        # a positive value means the damage went through armor
        self.damage_value = damage_value

        self.damage_type = damage_type
        self.damage_to_stat = damage_to_stat
        self.silent = silent
        self.add_threat = add_threat
        self.dont_proc = dont_proc

        self.combat_event = combat_event
        if self.combat_event == None:
            self.combat_event = CombatEvent()
            self.combat_event.add_to_queue(self)
        else:
            self.combat_event.add_to_queue(self)

        self.damage_snapshot = self.get_damage_snapshot()
        
    def get_damage_snapshot(self):
        return {
            StatType.HP: self.damage_taker_actor.stat_manager.stats[StatType.HP],
            StatType.PHYARMOR: self.damage_taker_actor.stat_manager.stats[
                StatType.PHYARMOR
            ],
            StatType.MAGARMOR: self.damage_taker_actor.stat_manager.stats[
                StatType.MAGARMOR
            ],
        }
           

       

    def run(self):
        self.combat_event.run()
        return self

    # if the damage is negative, this means that the damage has been blocked by armor or marmor
    # if its positive, assume that the armor is broken and damage is dealt directly to hp / whatever stat
    def calculate(self):
        
        # lvl_taker = self.damage_taker_actor.stat_manager.stats[StatType.LVL]
        # lvl_source = self.damage_taker_actor.stat_manager.stats[StatType.LVL]
        # lvl_diff = lvl_source - lvl_taker
        # if lvl_diff <= 0:
        #    lvl_diff = 0

        # add 20% of max hp of the taker to damage
        # if self.damage_taker_actor.room.combat != None:
        #    combat_round = self.damage_taker_actor.room.combat.round
        #    taker_max_hp = self.damage_taker_actor.stat_manager.stats[StatType.HPMAX]
        #    self.damage_value += int(self.damage_value * (0.05 * (combat_round-1)))

        self.damage_snapshot = self.get_damage_snapshot()

        #if self.damage_taker_actor.status == ActorStatusType.DEAD:
        #    self.damage_value = 0

        if self.damage_value <= 0:
            return self

        # if self.damage_type != DamageType.HEALING:
        #    _flow = int(self.damage_taker_actor.stat_manager.stats[StatType.FLOW])
        #    _roll = random.randint(0,100)
        #    if _roll <= _flow:
        #        self.damage_type = DamageType.CANCELLED
        #        self.damage_value = 0
        #        sound = Audio.WALK
        #        self.damage_taker_actor.simple_broadcast('You dodge', f'{self.damage_taker_actor.pretty_name()} dodges', sound = sound, msg_type = [MsgType.COMBAT])
        #        return self
        
        '''
        if self.damage_taker_actor != None and self.damage_source_actor != None and self.dont_proc == False:
            source = self.damage_source_actor
            taker = self.damage_taker_actor
            stats_source =    self.damage_source_actor.stat_manager.stats
            stats_taker =     self.damage_taker_actor.stat_manager.stats
            
            s_ego = 0
            t_ego = 0
            if type(source).__name__ == 'Player':
                s_ego = bool(source.settings_manager.get_value('ego'))
            if type(taker).__name__ == 'Player':
                t_ego = bool(taker.settings_manager.get_value('ego'))
            
            ego = False
            if s_ego == 1:
                ego = True
            if t_ego == 1:
                ego = True

            if type(source).__name__ == 'Player' and type(taker).__name__ == 'Player':
                ego = False
            
            if ego:
                #source_all = stats_source[StatType.HPMAX] + stats_source[StatType.PHYARMORMAX] + stats_source[StatType.MAGARMORMAX]
                #source_all -= (stats_source[StatType.GRIT] + stats_source[StatType.FLOW] + stats_source[StatType.MIND] + stats_source[StatType.SOUL])/4
                #taker_all =  stats_taker[StatType.HPMAX] + stats_taker[StatType.PHYARMORMAX] + stats_taker[StatType.MAGARMORMAX]
                #taker_all -= (stats_taker[StatType.GRIT] + stats_taker[StatType.FLOW] + stats_taker[StatType.MIND] + stats_taker[StatType.SOUL])/4
                source_lvl = stats_source[StatType.LVL]
                taker_lvl = stats_taker[StatType.LVL]

                if source_lvl > taker_lvl:
                    self.damage_value = self.damage_value - int(self.damage_value * (0.05 * (source_lvl - taker_lvl)))
                if source_lvl < taker_lvl:
                    self.damage_value = self.damage_value + int(self.damage_value * (0.05 * (taker_lvl - source_lvl)))
        '''

        '''
        if self.damage_taker_actor != None and self.damage_source_actor != None and self.dont_proc == False:
            source = self.damage_source_actor
            taker = self.damage_taker_actor
            stats_source =    self.damage_source_actor.stat_manager.stats
            stats_taker =     self.damage_taker_actor.stat_manager.stats
            
            s_ego = 1
            t_ego = 1
            if type(source).__name__ == 'Player':
                s_ego = float(source.settings_manager.get_value('ego'))
            if type(taker).__name__ == 'Player':
                t_ego = float(taker.settings_manager.get_value('ego'))
            
            ego = False
            if s_ego == 0:
                ego = True
            if t_ego == 0:
                ego = True

            if type(source).__name__ == 'Player' and type(taker).__name__ == 'Player':
                ego = False
            
            if ego:
                #source_all = stats_source[StatType.HPMAX] + stats_source[StatType.PHYARMORMAX] + stats_source[StatType.MAGARMORMAX]
                #source_all -= (stats_source[StatType.GRIT] + stats_source[StatType.FLOW] + stats_source[StatType.MIND] + stats_source[StatType.SOUL])/4
                #taker_all =  stats_taker[StatType.HPMAX] + stats_taker[StatType.PHYARMORMAX] + stats_taker[StatType.MAGARMORMAX]
                #taker_all -= (stats_taker[StatType.GRIT] + stats_taker[StatType.FLOW] + stats_taker[StatType.MIND] + stats_taker[StatType.SOUL])/4
                source_all = (stats_source[StatType.LVL]*10) + 30
                taker_all = (stats_taker[StatType.LVL]*10) + 30

                damage_percentage = self.damage_value / ((taker_all+source_all)/2)
                if damage_percentage <= 0.15:
                    damage_percentage = 0.15
                if damage_percentage >= 0.9:
                    damage_percentage = 0.9
                self.damage_value = int(taker_all*damage_percentage)

        '''
        if self.damage_taker_actor != None and self.damage_source_actor != None and self.dont_proc == False:
            source = self.damage_source_actor
            taker = self.damage_taker_actor


            if type(source).__name__ == 'Player':
                ego = float(source.settings_manager.get_value('ego'))
                ego_damage = (self.damage_value / ego)
                ego_damage = int(ego_damage)
                new_damage = ego_damage
                self.damage_value = new_damage

            if type(taker).__name__ == 'Player':
                ego = float(taker.settings_manager.get_value('ego'))
                
                ego_damage = int(self.damage_value * (ego)) #- self.damage_value
                self.damage_value = ego_damage
                '''
                ego_damage = int(ego_damage)
                new_damage = ego_damage
                damage = Damage(
                    add_threat = False,
                    dont_proc = True,
                    damage_taker_actor = self.damage_taker_actor,
                    damage_source_actor = self.damage_source_actor,
                    damage_source_action = self.damage_source_action,
                    damage_value = new_damage,
                    damage_type = self.damage_type,
                    damage_to_stat = self.damage_to_stat,
                    combat_event = self.combat_event,
                    silent = True,
                    )
                '''

        '''
        if self.damage_taker_actor != None and self.damage_source_actor != None and self.dont_proc == False:
            lvl_source =    self.damage_source_actor.stat_manager.stats[StatType.LVL]
            lvl_taker =     self.damage_taker_actor.stat_manager.stats[StatType.LVL]
            diff = (lvl_taker - lvl_source) / 10
            msg = f'diff is {diff}'
            self.damage_source_actor.simple_broadcast(msg,msg)
            if diff < 0:
                if diff < 0.9:
                    new_damage = int(self.damage_value - (self.damage_value*0.9))
                else:
                    new_damage = int(self.damage_value - (self.damage_value*abs(diff)))
                #new_damage = int(self.damage_value - abs(diff*1.5))
                #new_damage = int(diff*(self.damage_value+diff))-self.damage_value
                #if self.damage_value * 0.1 > new_damage:
                #    new_damage = int(self.damage_value * 0.05)

                self.damage_value = new_damage
                pass

            if diff > 0:
                diff = diff * 3
                bonus_dmg = int(diff*(self.damage_value+diff))-self.damage_value
                msg = f'rolled {self.damage_value}, adding {diff} which is {bonus_dmg}'
                self.damage_source_actor.simple_broadcast(msg,msg)
                #self.damage_value = int(diff*self.damage_value)
                damage = Damage(
                    add_threat = False,
                    dont_proc = True,
                    damage_taker_actor = self.damage_taker_actor,
                    damage_source_actor = self.damage_source_actor,
                    damage_source_action = self.damage_source_action,
                    damage_value = bonus_dmg,
                    damage_type = self.damage_type,
                    damage_to_stat = self.damage_to_stat,
                    combat_event = self.combat_event,
                    silent = True,
                )
                #damage.run()

        '''

        #if self.damage_taker_actor.room.combat != None:
        #    self.damage_value += 1*self.damage_taker_actor.room.combat.round

        match self.damage_type:
            # meaning the damage was completely cancelled by something
            # the affect should send_line what exactly happened
            # example: physical damage while ethereal should send "You are ethereal"
            case DamageType.CANCELLED:
                self.damage_value = 0
                return self

            case DamageType.PHYSICAL:
                self.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR] -= (
                    self.damage_value
                )
                if self.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR] < 0:
                    self.damage_value = (
                        -1
                        * self.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR]
                    )
                    self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] -= (
                        self.damage_value
                    )
                    self.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR] = 0
                else:
                    self.damage_value = -1 * self.damage_value
                    # self.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR] = 0

            case DamageType.MAGICAL:
                self.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR] -= (
                    self.damage_value
                )
                if self.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR] < 0:
                    self.damage_value = (
                        -1
                        * self.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR]
                    )
                    self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] -= (
                        self.damage_value
                    )
                    self.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR] = 0
                else:
                    self.damage_value = -1 * self.damage_value
                    # self.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR] = 0

            case DamageType.PURE:
                self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] -= (
                    self.damage_value
                )
                pass

            case DamageType.HEALING:
                self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] += (
                    self.damage_value
                )
                return self.damage_value

        """
        if self.damage_value <= 0:
            if not self.silent:
                self.damage_taker_actor.simple_broadcast(
                indent(f'You block', IndentType.MINOR),
                indent(f'{self.damage_taker_actor.pretty_name()} blocks', IndentType.MINOR)
                )
            return self
        """

        # if self.damage_value <= 0:
        #    self.damage_value = 0

        # self.damage_taker_actor.stat_manager.stats[self.damage_to_stat] -= self.damage_value

        """
        if self.damage_to_stat == StatType.HP:
            if not self.silent:
                self.damage_taker_actor.simple_broadcast(
                    indent(f'You take {self.damage_value} damage', IndentType.MINOR),
                    indent(f'{self.damage_taker_actor.pretty_name()} takes {self.damage_value} damage', IndentType.MINOR)
                    )

        if self.damage_to_stat == StatType.MP:
            if not self.silent:
                self.damage_taker_actor.simple_broadcast(
                    indent(f'You lose {self.damage_value} Magicka', IndentType.MINOR),
                    indent(f'{self.damage_taker_actor.pretty_name()} loses {self.damage_value} Magicka', IndentType.MINOR)
                    )
        """

        # self.damage_taker_actor.stat_manager.hp_mp_clamp_update()

        return self
