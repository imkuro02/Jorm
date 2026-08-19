import systems.utils
from configuration.constants.actor_status_type import ActorStatusType
from configuration.constants.audio import Audio
from configuration.constants.color import Color
from configuration.constants.damage_type import DamageType
from configuration.constants.message_type import MessageType
from configuration.constants.stat_type import StatType
import random

class CombatEvent:
    def __init__(self):
        self.queue = []
        self.popped = []
        self.to_print = {}

    def add_to_queue(self, damage_event):
        self.queue.append(damage_event)

    def pop_from_queue(self):
        self.popped.append(self.queue[0])
        # systems.utils.debug_print(self.queue[0].damage_source_action)
        self.queue.pop(0)

    def add_to_print(self, obj, diff):
        pop = {'id': obj.damage_source_action.id, 'diff': diff, 'obj': obj}
        if pop['id'] not in self.to_print:
            self.to_print[pop['id']] = pop
        else:
            for i in diff:
                self.to_print[pop['id']]['diff'][i] += diff[i]

    def print(self):
        output_other = ""
        output_self = ""
        sound = None

        for pop in self.to_print.values():


            obj = pop['obj']
            if obj.silent: 
                continue

            diff = pop['diff']

            color = Color.ERROR
            match obj.damage_type:
                case DamageType.HEALING:
                    color = Color.DAMAGE_HEAL
                case DamageType.PHYSICAL:
                    color = Color.DAMAGE_PHY
                case DamageType.MAGICAL:
                    color = Color.DAMAGE_MAG
                case DamageType.PURE:
                    color = Color.DAMAGE_PURE
            

            msg = ''
            #msg += f'{color} '
            msg += f'{obj.damage_taker_actor.id} '
            for i in diff:
                if diff[i]>0:
                    msg += f'lose#XD# ' + f'{abs(diff[i])} {StatType.name[i]} '

                if diff[i]<0:
                    msg += f'gain#XD# +' + f'{abs(diff[i])} {StatType.name[i]} '

            msg += f'from '
            msg += f'{obj.damage_source_action.id}'

            actors = []
            actors = [obj.damage_taker_actor]
            for actor in actors:
                if actor.status == ActorStatusType.DEAD:
                    continue
                if self.queue == []:
                    actor.pretty_broadcast(msg.replace('#XD#',''),msg.replace('#XD#','s'),list_pretty_name_objects = [obj.damage_taker_actor,obj.damage_source_actor,obj.damage_source_action])
                    actor.stat_manager.hp_mp_clamp_update()

        self.popped = []
        self.to_print = {}

    def run(self):

        if len(self.queue) == 0:
            #try:
            self.print()
            #except Exception as e:
            #    systems.utils.debug_print(f'Something went wrong while printing damage {e}')
            return

        

        # get damage_obj first in queue
        damage_obj = self.queue[0]
        self.pop_from_queue()
        
        snapshot_before = damage_obj.get_damage_snapshot()


        try:
            if damage_obj.dont_proc == False:
                rand_dmg = 0
                rand_dmg += damage_obj.damage_source_actor.calculate_damage_type_damage_bonus(damage_obj.damage_type)
                damage_obj.damage_value += rand_dmg #random.randint(0, rand_dmg)                    
        except Exception as e:
            systems.utils.debug_print('Something went wrong while applying stats to damage:')
            systems.utils.debug_print(f'"{e}"')

        try:            
            pa = damage_obj.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR]
            ma = damage_obj.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR]

            if not damage_obj.dont_proc:
                if damage_obj.damage_taker_actor.skill_manager != None:
                    damage_obj = damage_obj.damage_taker_actor.skill_manager.take_damage_before_calc(
                        damage_obj
                    )
                    
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

                if damage_obj.damage_source_actor.skill_manager != None:
                    damage_obj = damage_obj.damage_source_actor.skill_manager.deal_damage(
                        damage_obj
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
            
            '''for pop in self.popped:
                if not pop.silent and not damage_obj.silent:
                    if pop.damage_taker_actor == damage_obj.damage_taker_actor:
                        if pop == damage_obj:
                            continue
                        #print(pop.damage_taker_actor, damage_obj.damage_taker_actor)
                        #print(pop.damage_snapshot, damage_obj.damage_snapshot)
                        diff = {k: pop.damage_snapshot[k] - damage_obj.damage_snapshot[k] for k in pop.damage_snapshot} 
                        pop.damage_snapshot = {k: pop.damage_snapshot[k] - diff[k] for k in pop.damage_snapshot} 
                        print(diff, pop.damage_snapshot)'''
                        


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

                if damage_obj.damage_taker_actor.skill_manager != None:
                    damage_obj = damage_obj.damage_taker_actor.skill_manager.take_damage_after_calc(
                        damage_obj
                    )

                # after calc on damage_source_actor
                if damage_obj.damage_source_actor.affect_manager != None:
                    damage_obj.damage_source_actor.affect_manager.dealt_damage(damage_obj)
                if damage_obj.damage_source_actor.inventory_manager != None:
                    damage_obj.damage_source_actor.inventory_manager.dealt_damage(
                        damage_obj
                    )

                if damage_obj.damage_source_actor.skill_manager != None:
                    damage_obj = damage_obj.damage_source_actor.skill_manager.dealt_damage(
                        damage_obj
                    )

            # add threat to the attacker
            if damage_obj.add_threat:
                if damage_obj.damage_source_actor.stat_manager != None:
                    damage_obj.damage_source_actor.stat_manager.stats[StatType.THREAT] += (
                        abs(damage_obj.damage_value)
                    )


            snapshot_after = damage_obj.get_damage_snapshot()

            diff = {k: snapshot_before[k] - snapshot_after[k] for k in snapshot_after} 
            self.add_to_print(damage_obj, diff)

            pa1 = damage_obj.damage_taker_actor.stat_manager.stats[StatType.PHYARMOR]
            ma1 = damage_obj.damage_taker_actor.stat_manager.stats[StatType.MAGARMOR]
            sound = Audio.HURT
            actor = damage_obj.damage_taker_actor
            if pa > 0 and pa1 <1:
                _s = f"{actor.id} {Color.COMBAT_IMPORTANT}have no more {StatType.name[StatType.PHYARMOR]}{Color.NORMAL}"
                _o = f"{actor.id} {Color.COMBAT_IMPORTANT}has no more {StatType.name[StatType.PHYARMOR]}{Color.NORMAL}"
                damage_obj.damage_taker_actor.pretty_broadcast(_s,_o, sound=sound, msg_type=[MessageType.COMBAT], list_pretty_name_objects = [actor])
            if ma > 0 and ma1 <1:
                _s = f"{actor.id} {Color.COMBAT_IMPORTANT}have no more {StatType.name[StatType.MAGARMOR]}{Color.NORMAL}"
                _o = f"{actor.id} {Color.COMBAT_IMPORTANT}has no more {StatType.name[StatType.MAGARMOR]}{Color.NORMAL}"
                damage_obj.damage_taker_actor.pretty_broadcast(_s,_o, sound=sound, msg_type=[MessageType.COMBAT], list_pretty_name_objects = [actor])
        
            

        except Exception as e:
            systems.utils.debug_print(f'Something went wrong while running damage calculations for {damage_obj} {e}')


        # rerun if any affect_manager functions triggered another attack to be added to queue
        
        self.run()
