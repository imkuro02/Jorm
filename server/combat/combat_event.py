from configuration.config import ActorStatusType, StatType, DamageType, Audio, MsgType

class CombatEvent:
    def __init__(self):
        self.queue = []
        self.popped = []

    def add_to_queue(self, damage_event):
        self.queue.append(damage_event)

    def pop_from_queue(self):
        self.popped.append(self.queue[0])
        self.queue.pop(0)
        

    def print(self):
        
        output_other = ''
        output_self = ''
        sound = None
        
        

        for pop in self.popped:
            color = '@purple'
            match pop.damage_type:
                case DamageType.HEALING:
                    color = '@green'
                case DamageType.PHYSICAL:
                    color = '@red'
                case DamageType.MAGICAL:
                    color = '@cyan'
                case DamageType.PURE:
                    color = '@yellow'
            if not pop.silent:
                #print(pop)
                if pop.damage_taker_actor.stat_manager.stats[pop.damage_to_stat+'_max'] == 0:
                    percentage = 0
                else:
                    percentage = int((pop.damage_value / pop.damage_taker_actor.stat_manager.stats[pop.damage_to_stat+'_max'])*100)
                
                if pop.damage_value < 0:
                    damage_txt = f'{abs(pop.damage_value)}@back'
                else:
                    damage_txt = f'{abs(pop.damage_value)} @normal(@back {percentage}% @normal)@back'

                
                if pop.damage_type == DamageType.CANCELLED:
                    output_self =  f'You cancel {pop.damage_source_action.name}. '
                    output_other = f'{pop.damage_taker_actor.pretty_name()} cancels {pop.damage_source_action.name}. '
                    sound = Audio.ERROR
                elif pop.damage_type == DamageType.HEALING:
                    output_self = f'You heal {color}{damage_txt}@back {StatType.name[pop.damage_to_stat]} from {pop.damage_source_action.name}.'
                    output_other = f'{pop.damage_taker_actor.pretty_name()} heals {color}{damage_txt}@back {StatType.name[pop.damage_to_stat]} from {pop.damage_source_action.name}.'
                    sound = Audio.BUFF
                
                if pop.damage_type == DamageType.PHYSICAL or pop.damage_type == DamageType.MAGICAL or pop.damage_type == DamageType.PURE:
                    if pop.damage_value <= 0:
                        output_self = f'You block {color}{damage_txt} from {pop.damage_source_action.name}. '
                        output_other = f'{pop.damage_taker_actor.pretty_name()} blocks {color}{damage_txt} from {pop.damage_source_action.name}. '
                        sound = Audio.ERROR
                    else:
                        output_self = f'You lose {color}{damage_txt}@back {StatType.name[pop.damage_to_stat]} from {pop.damage_source_action.name}. '
                        output_other = f'{pop.damage_taker_actor.pretty_name()} loses {color}{damage_txt}@back {StatType.name[pop.damage_to_stat]} from {pop.damage_source_action.name}. '
                        sound = Audio.HURT

                pop.damage_taker_actor.simple_broadcast(output_self, output_other, sound = sound, msg_type = [MsgType.COMBAT])


        

        
        
        actors = []
        for actor in pop.damage_source_actor.room.actors.values():
            actors.append(actor)
        for actor in actors:
            if actor.status == ActorStatusType.DEAD:
                continue
            actor.stat_manager.hp_mp_clamp_update()
        

        #pop.damage_source_actor.stat_manager.hp_mp_clamp_update()
        #pop.damage_taker_actor.stat_manager.hp_mp_clamp_update()

    def run(self):
        if len(self.queue) == 0:
            self.print()
            return

        # get damage_obj first in queue
        damage_obj = self.queue[0]

        # before calc on damage_source_actor 
        damage_obj = damage_obj.damage_source_actor.affect_manager.deal_damage(damage_obj)
        damage_obj = damage_obj.damage_source_actor.inventory_manager.deal_damage(damage_obj)

        # before calc on damage_taker_actor
        damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_before_calc(damage_obj)
        damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_before_calc(damage_obj)
       
        # +/- armor calculation and hp removal
        damage_obj.calculate()

        # after calc on damage_taker_actor
        damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_after_calc(damage_obj)
        damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_after_calc(damage_obj)

        # after calc on damage_source_actor 
        damage_obj.damage_source_actor.affect_manager.dealt_damage(damage_obj)
        damage_obj.damage_source_actor.inventory_manager.dealt_damage(damage_obj)

        # add threat to the attacker
        if damage_obj.add_threat:
            damage_obj.damage_source_actor.stat_manager.stats[StatType.THREAT] += abs(damage_obj.damage_value)
        
        self.pop_from_queue()


        '''
        # break loop if someone is dead
        #if damage_obj.damage_source_actor.status == ActorStatusType.DEAD:
        #    return
        #if damage_obj.damage_taker_actor.status == ActorStatusType.DEAD:
        #    return

        # add attacker buffs
        print('base dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_source_actor.affect_manager.deal_damage(damage_obj)
        print('deal_damage dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_source_actor.inventory_manager.deal_damage(damage_obj)
        print('deal_damage dmg:',damage_obj.damage_value)

        # before taking damage, receiver buffs
        damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_before_calc(damage_obj)
        print('take_damage dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_before_calc(damage_obj)
        print('take_damage dmg:',damage_obj.damage_value)
       
        # +/- armor calculation and hp removal
        damage_obj.calculate()
        print('calculated',damage_obj.damage_value)

        # after taking damage, receiver buffs
        damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage_after_calc(damage_obj)
        print('take_damage dmg:',damage_obj.damage_value)
        damage_obj = damage_obj.damage_taker_actor.inventory_manager.take_damage_after_calc(damage_obj)
        print('take_damage dmg:',damage_obj.damage_value)


        # effects after successful attack
        damage_obj.damage_source_actor.affect_manager.dealt_damage(damage_obj)
        print('dealt_damage',damage_obj.damage_value)
        damage_obj.damage_source_actor.inventory_manager.dealt_damage(damage_obj)
        print('dealt_damage',damage_obj.damage_value)
        # add threat to the attacker
        damage_obj.damage_source_actor.stat_manager.stats[StatType.THREAT] += damage_obj.damage_value
        self.pop_from_queue()
        # rerun if any affect_manager functions triggered another attack to be added to queue
        '''

        # rerun if any affect_manager functions triggered another attack to be added to queue
        self.run()