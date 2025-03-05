from configuration.config import ActorStatusType, StatType

class CombatEvent:
    def __init__(self):
        self.queue = []

    def add_to_queue(self, damage_event):
        self.queue.append(damage_event)

    def pop_from_queue(self):
        self.queue.pop(0)

    def run(self):
        if len(self.queue) == 0:
            return

        # get damage_obj first in queue
        damage_obj = self.queue[0]

        # break loop if someone is dead
        if damage_obj.damage_source_actor.status == ActorStatusType.DEAD:
            return
        if damage_obj.damage_taker_actor.status == ActorStatusType.DEAD:
            return

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