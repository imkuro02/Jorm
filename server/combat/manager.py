from configuration.config import ActorStatusType, StatType, DamageType
from combat.combat_event import CombatEvent
from combat.damage_event import Damage
class Combat:
    def __init__(self, room, participants):
        self.room = room
        self.participants = participants
        self.order = []
        self.current_actor = None
        self.time_since_turn_finished = 0
        self.round = 1

        # reset threat
        for p in self.participants.values():
            if type(p).__name__ == 'Player':
                p.stat_manager.stats[StatType.THREAT] = 20 
            else: 
                p.stat_manager.stats[StatType.THREAT] = 0  

        self.initiative()
        
    def add_participant(self, participant):
        participant.status = ActorStatusType.FIGHTING
        if participant.id in self.participants:
            return # already participating in combat
        self.participants[participant.id] = participant
        participant.simple_broadcast(
            f'You join the combat',
            f'{participant.pretty_name()} joins the combat',
        )
        # reset threat to 0 at start of combat
        participant.stat_manager.stats[StatType.THREAT] = 0 

    def tick(self):
        if self.current_actor == None:
            return

        self.time_since_turn_finished += 1

        if len(self.participants) == 0:
            self.combat_over()

        #print(self.time_since_turn_finished, len(self.participants))
        if self.time_since_turn_finished == 30*20:
            if type(self.current_actor).__name__ == "Player":
                self.current_actor.simple_broadcast(
                    '@yellowYour turn is over in 10 seconds.@normal',
                    f'{self.current_actor.name}\'s turn is over in 10 seconds.'
                )

        if self.time_since_turn_finished >= 30*30:
            if type(self.current_actor).__name__ == "Player":
                self.current_actor.simple_broadcast(
                    '@yellowYou missed your turn.@normal',
                    f'{self.current_actor.name} missed their turn.'
                )

            self.time_since_turn_finished = 0
            self.next_turn()


        '''
        team1_died = True
        team2_died = True
        for i in self.participants.values():
            if i.status != 'dead' and type(i).__name__ == "Player":
                team1_died = False
            if i.status != 'dead' and type(i).__name__ == "Enemy":
                team2_died = False
            i.tick()
        '''
        for i in self.participants.values():
            i.tick()

        #if team1_died or team2_died:
        #    self.combat_over()

        if self.current_actor.room != self.room:
            print(self.current_actor.name, 'removed from combat')
            if self.current_actor.id in self.participants: 
                self.participants[self.current_actor.id].status = ActorStatusType.NORMAL
                del self.participants[self.current_actor.id]
            self.next_turn()
            return

        if self.current_actor.status == ActorStatusType.DEAD:
            self.next_turn()
            return      

    def combat_over(self):
        for i in self.participants.values():
            if i.status == ActorStatusType.FIGHTING: i.status = ActorStatusType.NORMAL
            if type(i).__name__ == "Player":
                #i.sendLine('@yellowCombat over!@normal')
                i.combat_over_prompt()
              
            #self, skill_id, cooldown, user, other, users_skill_level: int, use_perspectives, success = False, silent_use = False, no_cooldown = False
            '''
            hp = SkillRegenHP30('hp_regen_30',1,self,self,100,None,silent_use=True,no_cooldown=True)
            mp = SkillRegenHP30('hp_regen_30',1,self,self,100,None,silent_use=True,no_cooldown=True)
            hp.use()
            mp.use()
            '''
            '''
            # heal a bit after battle
            if i.status != ActorStatusType.DEAD:
                damage_obj = Damage(
                    damage_taker_actor = i,
                    damage_source_actor = i,
                    damage_value = int(i.stat_manager.stats[StatType.HPMAX]*.25),
                    damage_type = DamageType.HEALING,
                    silent = True
                    )
                damage_obj.run()          
                damage_obj = Damage(
                        damage_taker_actor = i,
                        damage_source_actor = i,
                        damage_value = int(i.stat_manager.stats[StatType.MPMAX]*.25),
                        damage_type = DamageType.HEALING,
                        damage_to_stat = StatType.MP,
                        silent = True
                        )
                damage_obj.run()   
                #i.simple_broadcast('')
            '''

        self.participants = {}
        self.room.combat = None
        print('combat over')

    def next_turn(self):
        team1_died = True
        team2_died = True
        for i in self.participants.values():
            if i.status != ActorStatusType.DEAD and type(i).__name__ == "Player":
                team1_died = False
            if i.status != ActorStatusType.DEAD and type(i).__name__ == "Enemy":
                team2_died = False
        if team1_died or team2_died:
            self.combat_over()
            return

        self.time_since_turn_finished = 0
        if len(self.order) == 0:
            self.initiative()
            return
        
        self.current_actor = self.order[0]
        self.order.pop(0)
        self.current_actor.set_turn()

    def initiative(self):
        for i in self.participants.values():
            if i.status != ActorStatusType.DEAD:
                self.order.append(i)
        
        for i in self.order:
            if type(i).__name__ == "Player":
                combat_stats = f'\n@yellowCombat overview (Round {self.round})@normal:'
                for participant in self.order:
                    #combat_stats = combat_stats + f'''\n{participant.pretty_name()} [@red{participant.stat_manager.stats[StatType.HP]}@normal/@red{participant.stat_manager.stats[StatType.HPMAX]}@normal] {participant.party_manager.get_party_id()}'''
                    combat_stats = combat_stats + f'''\n{participant.pretty_name()} [@red{participant.stat_manager.stats[StatType.HP]}@normal/@red{participant.stat_manager.stats[StatType.HPMAX]}@normal]'''
                i.sendLine(combat_stats)
                #i.sendLine(f'@yellowTurn order: {[actor.name for actor in self.order]}@normal')
        
        self.round += 1
        for i in self.order:
            i.status = ActorStatusType.FIGHTING

        if len(self.order) == 0:
            self.combat_over()
            return

        self.next_turn()
        #self.current_actor = self.order[0]
        #self.current_actor.set_turn()

        
