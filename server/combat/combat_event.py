from configuration.config import ActorStatusType, StatType, DamageType, Audio, MsgType, Color
import utils

class CombatEvent:
    def __init__(self):
        self.queue = []
        self.popped = []

    def add_to_queue(self, damage_event):
        self.queue.append(damage_event)

    def pop_from_queue(self):
        self.popped.append(self.queue[0])
        #utils.debug_print(self.queue[0].damage_source_action)
        self.queue.pop(0)
        

    def print(self):
        
        output_other = ''
        output_self = ''
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
            if not pop.silent:
                #utils.debug_print(pop)
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
                    output_self =  f'You cancel {action_text}. '
                    output_other = f'{pop.damage_taker_actor.pretty_name()} cancels {action_text}'
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


        

        
        
        actors = []
        actors = [pop.damage_taker_actor]
        #if pop.damage_taker_actor.room != None:
        #for actor in pop.damage_taker_actor.room.actors.values():
        #    actors.append(actor)
        for actor in actors:
            if actor.status == ActorStatusType.DEAD:
                continue

            # do not clamp if actor is unloaded
            #if actor.stat_manager == None:
            #    utils.debug_print(f'{actor} was unloaded but somehow took damage (probably a heal tick)')
            #    utils.debug_print(f'{actor.name} was unloaded but somehow took damage (probably a heal tick)')
            #    continue
            
            actor.stat_manager.hp_mp_clamp_update()
        

        #pop.damage_source_actor.stat_manager.hp_mp_clamp_update()
        #pop.damage_taker_actor.stat_manager.hp_mp_clamp_update()

    def run(self):
        if len(self.queue) == 0:
            self.print()
            return

        # get damage_obj first in queue
        damage_obj = self.queue[0]

        
        if not damage_obj.dont_proc:
            # before calc on damage_source_actor 
            if damage_obj.damage_source_actor.affect_manager != None:
                damage_obj = damage_obj.damage_source_actor.affect_manager.deal_damage(damage_obj)
            if damage_obj.damage_source_actor.inventory_manager != None:
                damage_obj = damage_obj.damage_source_actor.inventory_manager.deal_damage(damage_obj)

            # before calc on damage_taker_actor
            if damage_obj.damage_taker_actor.affect_manager != None:
                damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_before_calc(damage_obj)
            if damage_obj.damage_taker_actor.inventory_manager != None:
                damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_before_calc(damage_obj)
       
        # +/- armor calculation and hp removal
        damage_obj.calculate()

        if not damage_obj.dont_proc:
            # after calc on damage_taker_actor
            if damage_obj.damage_taker_actor.affect_manager != None:
                damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_after_calc(damage_obj)
            if damage_obj.damage_taker_actor.inventory_manager != None:
                damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_after_calc(damage_obj)

            # after calc on damage_source_actor 
            if damage_obj.damage_source_actor.affect_manager != None:
                damage_obj.damage_source_actor.affect_manager.dealt_damage(damage_obj)
            if damage_obj.damage_source_actor.inventory_manager != None:
                damage_obj.damage_source_actor.inventory_manager.dealt_damage(damage_obj)

        # add threat to the attacker
        if damage_obj.add_threat:
            if damage_obj.damage_source_actor.stat_manager != None:
                damage_obj.damage_source_actor.stat_manager.stats[StatType.THREAT] += abs(damage_obj.damage_value)
        
        self.pop_from_queue()


        '''
        # break loop if someone is dead
        #if damage_obj.damage_source_actor.status == ActorStatusType.DEAD:
        #    return
        #if damage_obj.damage_taker_actor.status == ActorStatusType.DEAD:
        #    return

        # add attacker buffs
        utils.debug_print('base dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_source_actor.affect_manager.deal_damage(damage_obj)
        utils.debug_print('deal_damage dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_source_actor.inventory_manager.deal_damage(damage_obj)
        utils.debug_print('deal_damage dmg:',damage_obj.damage_value)

        # before taking damage, receiver buffs
        damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_before_calc(damage_obj)
        utils.debug_print('take_damage dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_before_calc(damage_obj)
        utils.debug_print('take_damage dmg:',damage_obj.damage_value)
       
        # +/- armor calculation and hp removal
        damage_obj.calculate()
        utils.debug_print('calculated',damage_obj.damage_value)

        # after taking damage, receiver buffs
        damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_after_calc(damage_obj)
        utils.debug_print('take_damage dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_after_calc(damage_obj)
        utils.debug_print('take_damage dmg:',damage_obj.damage_value)


        # effects after successful attack
        damage_obj.damage_source_actor.affect_manager.dealt_damage(damage_obj)
        utils.debug_print('dealt_damage',damage_obj.damage_value)
        damage_obj.damage_source_actor.inventory_manager.dealt_damage(damage_obj)
        utils.debug_print('dealt_damage',damage_obj.damage_value)
        # add threat to the attacker
        damage_obj.damage_source_actor.stat_manager.stats[StatType.THREAT] += damage_obj.damage_value
        self.pop_from_queue()
        # rerun if any affect_manager functions triggered another attack to be added to queue
        '''

        # rerun if any affect_manager functions triggered another attack to be added to queue
        self.run()