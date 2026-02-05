import systems.utils
from configuration.config import (
    ActorStatusType,
    Audio,
    Color,
    DamageType,
    MsgType,
    StatType,
)


class CombatEvent:
    def __init__(self):
        self.queue = []
        self.popped = []

    def add_to_queue(self, damage_event):
        self.queue.append(damage_event)

    def pop_from_queue(self):
        self.popped.append(self.queue[0])
        # systems.utils.debug_print(self.queue[0].damage_source_action)
        self.queue.pop(0)

    def print(self):
        output_other = ""
        output_self = ""
        sound = None

        for pop in self.popped:
            

            color = Color.ERROR
            match pop.damage_type:
                case DamageType.HEALING:
                    color = Color.DAMAGE_HEAL
                case DamageType.PHYSICAL:
                    color = Color.DAMAGE_PHY
                case DamageType.MAGICAL:
                    color = Color.DAMAGE_MAG
                case DamageType.PURE:
                    color = Color.DAMAGE_PURE

            """
            if not pop.silent:
                #systems.utils.debug_print(pop)
                if pop.damage_taker_actor.stat_manager.stats[pop.damage_to_stat+'_max'] == 0:
                    percentage = 0
                else:
                    percentage = int((pop.damage_value / pop.damage_taker_actor.stat_manager.stats[pop.damage_to_stat+'_max'])*100)

                if pop.damage_value < 0:
                    damage_txt = f'{abs(pop.damage_value)}@back'
                else:
                    damage_txt = f'{abs(pop.damage_value)}@back'
                    #damage_txt = f'{abs(pop.damage_value)} @normal(@back {percentage}% @normal)@back'


                action_text = f'{color}{damage_txt}@normal {color}{DamageType.name[pop.damage_type]}@normal from {pop.damage_source_action.name}'
                if pop.damage_to_stat != StatType.HP:
                    action_text = f'{color}{damage_txt}@normal {color}{DamageType.name[pop.damage_type]}@normal to {color}{StatType.name[pop.damage_to_stat]}@normal from {pop.damage_source_action.name}'
                if pop.damage_type == DamageType.CANCELLED:
                    output_self =  f'You cancel {pop.damage_source_action.name}. '
                    output_other = f'{pop.damage_taker_actor.pretty_name()} cancels {pop.damage_source_action.name}'
                    sound = Audio.ERROR
                elif pop.damage_type == DamageType.HEALING:
                    output_self = f'You receive {action_text}.'
                    output_other = f'{pop.damage_taker_actor.pretty_name()} receives {action_text}'
                    sound = Audio.BUFF
                elif pop.damage_type == DamageType.PHYSICAL or pop.damage_type == DamageType.MAGICAL or pop.damage_type == DamageType.PURE:
                    output_self = f'You receive {action_text}. '
                    output_other = f'{pop.damage_taker_actor.pretty_name()} receives {action_text}'
                    sound = Audio.HURT
                    #if pop.damage_value <= 0:
                    #    output_self = f'You block {action_text}. '
                    #    output_other = f'{pop.damage_taker_actor.pretty_name()} blocks {action_text}'
                    #    sound = Audio.ERROR
                    #else:
                    #    output_self = f'You lose {action_text}. '
                    #    output_other = f'{pop.damage_taker_actor.pretty_name()} loses {action_text}'
                    #    sound = Audio.HURT

                pop.damage_taker_actor.simple_broadcast(output_self, output_other, sound = sound, msg_type = [MsgType.COMBAT])
            """

            if not pop.silent and pop.damage_type != DamageType.CANCELLED:
                damage_snapshot2 = {
                    StatType.HP: pop.damage_taker_actor.stat_manager.stats[StatType.HP],
                    StatType.PHYARMOR: pop.damage_taker_actor.stat_manager.stats[
                        StatType.PHYARMOR
                    ],
                    StatType.MAGARMOR: pop.damage_taker_actor.stat_manager.stats[
                        StatType.MAGARMOR
                    ],
                }

                """
                summary = {
                    StatType.HP: pop.damage_snapshot[StatType.HP] - damage_snapshot2[StatType.HP],
                    StatType.PHYARMOR: pop.damage_snapshot[StatType.PHYARMOR] - damage_snapshot2[StatType.PHYARMOR],
                    StatType.MAGARMOR: pop.damage_snapshot[StatType.MAGARMOR]- damage_snapshot2[StatType.MAGARMOR]
                }"""

                summary = {
                    StatType.HP: damage_snapshot2[StatType.HP]
                    - pop.damage_snapshot[StatType.HP],
                    StatType.PHYARMOR: damage_snapshot2[StatType.PHYARMOR]
                    - pop.damage_snapshot[StatType.PHYARMOR],
                    StatType.MAGARMOR: damage_snapshot2[StatType.MAGARMOR]
                    - pop.damage_snapshot[StatType.MAGARMOR],
                }

                if summary == pop.damage_snapshot:
                    return

                def lose_or_gain(val):
                    if val <= -1:
                        return "#L# " + Color.BAD + ""
                    elif val >= 1:
                        return "#G# " + Color.GOOD + "+"
                    else:
                        return None

                # output_self = str(summary)
                output = f"#A# "

                for i in summary:
                    _hp = lose_or_gain(summary[i])
                    if _hp != None:
                        output += f"{_hp}{abs(summary[i])}{Color.BACK} {Color.stat[i]}{StatType.name[i]}{Color.BACK},"

                if "#L#" not in output and "#G#" not in output:
                    return

                phy_arm_broke = (
                    pop.damage_snapshot[StatType.PHYARMOR] != 0
                    and damage_snapshot2[StatType.PHYARMOR] == 0
                )
                mag_arm_broke = (
                    pop.damage_snapshot[StatType.MAGARMOR] != 0
                    and damage_snapshot2[StatType.MAGARMOR] == 0
                )

                # if phy_arm_broke:
                #    output += f'{Color.stat[StatType.PHYARMOR]}{StatType.name[StatType.PHYARMOR]}{Color.BACK} {Color.COMBAT_TURN}BROKE{Color.BACK},'
                # if mag_arm_broke:
                #    output += f'{Color.stat[StatType.MAGARMOR]}{StatType.name[StatType.MAGARMOR]}{Color.BACK} {Color.COMBAT_TURN}BROKE{Color.BACK},'
                output = f"{output}{Color.NORMAL}"
                output = f" from {pop.damage_source_action.pretty_name()}".join(
                    output.rsplit(",", 1)
                )
                output = " and ".join(output.rsplit(",", 1))

                output_self = output
                output_other = output

                output_self = output_self.replace("#A#", f"You have")
                output_self = output_self.replace("#G#", "healed")
                output_self = output_self.replace("#L#", "lost")

                output_other = output_other.replace(
                    "#A#", f"{pop.damage_taker_actor.pretty_name()} has"
                )
                output_other = output_other.replace("#G#", "healed")
                output_other = output_other.replace("#L#", "lost")

                # output_raw = output_other = output_other.replace('#A#',f'')
                # output_raw = output_other.replace('#G#','healed')
                # output_raw = output_other.replace('#L#','lost')

                """
                _hp = lose_or_gain(summary[StatType.HP])
                if _hp != None:
                    output += f'{_hp}{summary[StatType.HP]}{Color.BACK} {StatType.name[StatType.HP]},'

                _pa = lose_or_gain(summary[StatType.PHYARMOR])
                if _pa != None:
                    output += f'{_pa}{summary[StatType.PHYARMOR]}{Color.BACK}PA '

                _ma = lose_or_gain(summary[StatType.MAGARMOR])
                if _ma != None:
                    output += f'{_ma}{summary[StatType.MAGARMOR]}{Color.BACK}{Color.MAGARM}MA '
                """

                sound = Audio.HURT
                # output = f'{pop.damage_taker_actor.name}  {pop.damage_hp}hp  {pop.damage_pa}pa {pop.damage_ma}ma'
                pop.damage_taker_actor.simple_broadcast(
                    output_self, output_other, sound=sound, msg_type=[MsgType.COMBAT]
                )

                if phy_arm_broke:
                    output = f"{Color.COMBAT_IMPORTANT}Your {StatType.name[StatType.PHYARMOR]} has broken{Color.NORMAL}"
                    pop.damage_taker_actor.sendLine(
                        f"{output}", sound=sound, msg_type=[MsgType.COMBAT]
                    )
                if mag_arm_broke:
                    output = f"{Color.COMBAT_IMPORTANT}Your {StatType.name[StatType.MAGARMOR]} has broken{Color.NORMAL}"
                    pop.damage_taker_actor.sendLine(
                        f"{output}", sound=sound, msg_type=[MsgType.COMBAT]
                    )
                # if phy_arm_broke:
                #    output = f'{Color.stat[StatType.PHYARMOR]}{StatType.name[StatType.PHYARMOR]}{Color.BACK} has broken'
                #    pop.damage_taker_actor.simple_broadcast(f'Your {output}', f'{pop.damage_taker_actor.pretty_name()}\'s {output}', sound = sound, msg_type = [MsgType.COMBAT])
                # if mag_arm_broke:
                #    output = f'{Color.stat[StatType.PHYARMOR]}{StatType.name[StatType.MAGARMOR]}{Color.BACK} has broken'
                #    pop.damage_taker_actor.simple_broadcast(f'Your {output}', f'{pop.damage_taker_actor.pretty_name()}\'s {output}', sound = sound, msg_type = [MsgType.COMBAT])

        actors = []
        actors = [pop.damage_taker_actor]
        # if pop.damage_taker_actor.room != None:
        # for actor in pop.damage_taker_actor.room.actors.values():
        #    actors.append(actor)
        for actor in actors:
            if actor.status == ActorStatusType.DEAD:
                continue

            # do not clamp if actor is unloaded
            # if actor.stat_manager == None:
            #    systems.utils.debug_print(f'{actor} was unloaded but somehow took damage (probably a heal tick)')
            #    systems.utils.debug_print(f'{actor.name} was unloaded but somehow took damage (probably a heal tick)')
            #    continue

            actor.stat_manager.hp_mp_clamp_update()

        # pop.damage_source_actor.stat_manager.hp_mp_clamp_update()
        # pop.damage_taker_actor.stat_manager.hp_mp_clamp_update()

    def run(self):

        
        
        if len(self.queue) == 0:
            self.print()
            return

        # get damage_obj first in queue
        damage_obj = self.queue[0]

     
        

        if not damage_obj.dont_proc:
            # before calc on damage_source_actor
            if damage_obj.damage_source_actor.affect_manager != None:
                damage_obj = damage_obj.damage_source_actor.affect_manager.deal_damage(
                    damage_obj
                )
            if damage_obj.damage_source_actor.inventory_manager != None:
                damage_obj = (
                    damage_obj.damage_source_actor.inventory_manager.deal_damage(
                        damage_obj
                    )
                )

            # before calc on damage_taker_actor
            if damage_obj.damage_taker_actor.affect_manager != None:
                damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_before_calc(
                    damage_obj
                )
            if damage_obj.damage_taker_actor.inventory_manager != None:
                damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_before_calc(
                    damage_obj
                )

        # +/- armor calculation and hp removal
        damage_obj.calculate()

        if not damage_obj.dont_proc:
            # after calc on damage_taker_actor
            if damage_obj.damage_taker_actor.affect_manager != None:
                damage_obj = (
                    damage_obj.damage_taker_actor.affect_manager.take_damage_after_calc(
                        damage_obj
                    )
                )
            if damage_obj.damage_taker_actor.inventory_manager != None:
                damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_after_calc(
                    damage_obj
                )

            # after calc on damage_source_actor
            if damage_obj.damage_source_actor.affect_manager != None:
                damage_obj.damage_source_actor.affect_manager.dealt_damage(damage_obj)
            if damage_obj.damage_source_actor.inventory_manager != None:
                damage_obj.damage_source_actor.inventory_manager.dealt_damage(
                    damage_obj
                )

        # add threat to the attacker
        if damage_obj.add_threat:
            if damage_obj.damage_source_actor.stat_manager != None:
                damage_obj.damage_source_actor.stat_manager.stats[StatType.THREAT] += (
                    abs(damage_obj.damage_value)
                )

        

        self.pop_from_queue()

        """
        # break loop if someone is dead
        #if damage_obj.damage_source_actor.status == ActorStatusType.DEAD:
        #    return
        #if damage_obj.damage_taker_actor.status == ActorStatusType.DEAD:
        #    return

        # add attacker buffs
        systems.utils.debug_print('base dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_source_actor.affect_manager.deal_damage(damage_obj)
        systems.utils.debug_print('deal_damage dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_source_actor.inventory_manager.deal_damage(damage_obj)
        systems.utils.debug_print('deal_damage dmg:',damage_obj.damage_value)

        # before taking damage, receiver buffs
        damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_before_calc(damage_obj)
        systems.utils.debug_print('take_damage dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_before_calc(damage_obj)
        systems.utils.debug_print('take_damage dmg:',damage_obj.damage_value)

        # +/- armor calculation and hp removal
        damage_obj.calculate()
        systems.utils.debug_print('calculated',damage_obj.damage_value)

        # after taking damage, receiver buffs
        damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_after_calc(damage_obj)
        systems.utils.debug_print('take_damage dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_after_calc(damage_obj)
        systems.utils.debug_print('take_damage dmg:',damage_obj.damage_value)


        # effects after successful attack
        damage_obj.damage_source_actor.affect_manager.dealt_damage(damage_obj)
        systems.utils.debug_print('dealt_damage',damage_obj.damage_value)
        damage_obj.damage_source_actor.inventory_manager.dealt_damage(damage_obj)
        systems.utils.debug_print('dealt_damage',damage_obj.damage_value)
        # add threat to the attacker
        damage_obj.damage_source_actor.stat_manager.stats[StatType.THREAT] += damage_obj.damage_value
        self.pop_from_queue()
        # rerun if any affect_manager functions triggered another attack to be added to queue
        """

        # rerun if any affect_manager functions triggered another attack to be added to queue
        self.run()
