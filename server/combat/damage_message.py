
class ReactionDeath:
    def __init__(self, actor):
        self.actor = actor

class ReactionLoot:
    def __init__(self, source, destination, loot):
        self.source = source
        self.destination = destination
        self.loot = loot

class ReactionDamage:
    def __init__(self, source, destination, damage_val, damage_type):
        self.source = source
        self.destination = destination
        self.damage_val = damage_val
        self.damage_type = damage_type
    
class ActionReaction:
    def __init__(self, action_actor, action):
        self.action_actor = action_actor
        self.action = action
        self.reactions = []

    def add_reaction(self, reaction):
        print(reaction)
        self.reactions.append(reaction)
        
    def print(self):
        output = ''
        #if type(self.action).__name__ == 'Skill':
        #    output += self.action.print()

        #self.action_actor.simple_broadcast(self.__dict__, self.__dict__)
        for reaction in self.reactions:
            output += type(reaction).__name__ 
            output += ' ' + str(reaction.__dict__)
        self.action_actor.simple_broadcast(output, output)