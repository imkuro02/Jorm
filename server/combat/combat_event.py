from configuration.config import ActorStatusType, StatType, DamageType

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
        
        output = ''
        
        

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
                if pop.damage_type == DamageType.CANCELLED:
                    output += f'{pop.damage_taker_actor.pretty_name()} cancels {pop.damage_source_action.name}. '
                elif pop.damage_type == DamageType.HEALING:
                    output += f'{pop.damage_taker_actor.pretty_name()} heals {color}{pop.damage_value} {StatType.name[pop.damage_to_stat]}@back from {pop.damage_source_action.name}'
                elif pop.damage_value <= 0:
                    output += f'{pop.damage_taker_actor.pretty_name()} blocks {color}{pop.damage_source_action.name}@back. '
                else:
                    output += f'{pop.damage_taker_actor.pretty_name()} takes {color}{pop.damage_value} damage@back from {pop.damage_source_action.name}. '

        if output == '': 
            return

        pop.damage_source_actor.simple_broadcast(output,output)
        
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

        # break loop if someone is dead
        #if damage_obj.damage_source_actor.status == ActorStatusType.DEAD:
        #    return
        #if damage_obj.damage_taker_actor.status == ActorStatusType.DEAD:
        #    return

        # add attacker buffs
        damage_obj = damage_obj.damage_source_actor.affect_manager.deal_damage(damage_obj)
        # add receiver buffs
        damage_obj = damage_obj.damage_taker_actor.affect_manager.take_damage(damage_obj)
        # +/- armor calculation and hp removal
        damage_obj.calculate()
        # effects after successful attack
        damage_obj.damage_source_actor.affect_manager.dealt_damage(damage_obj)
        # add threat to the attacker
        damage_obj.damage_source_actor.stat_manager.stats[StatType.THREAT] += damage_obj.damage_value
        self.pop_from_queue()
        # rerun if any affect_manager functions triggered another attack to be added to queue
        
        self.run()