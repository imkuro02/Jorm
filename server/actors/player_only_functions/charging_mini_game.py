from actors.player_only_functions.checks import check_not_in_combat

import random



class ChargingMiniGame:
    def __init__(self, owner):
        self.LINES_START = [
            ['You kneel down and begin to pray', '#USER# kneels down and begins to pray'],
            ['You close your eyes and press your palms together to pray', '#USER# closes their eyes and presses their palms together to pray'],
            ['You hold your hands together to pray', '#USER# holds their hands together and prays'],
            ['You bow your head in silence', '#USER# bows their head in silence'],
            ['You sit quietly and begin to pray', '#USER# sits quietly and begins to pray'],
            ['You clasp your hands and murmur softly', '#USER# clasps their hands and murmurs softly'],
            ['You lower yourself into a humble posture', '#USER# lowers themselves into a humble posture'],
            ['You fold your hands and take a deep breath', '#USER# folds their hands and takes a deep breath']
        ]

        self.LINES_STOP = [
            ['You slowly get up again', '#USER# slowly gets up again'],
            ['You relax your hands and open your eyes again', '#USER# relaxes their hands and opens their eyes again'],
            ['Your hands let go and you finish your prayer', "#USER#'s hands let go and they finish their prayer"],
            ['You take a deep breath and stand up', '#USER# takes a deep breath and stands up'],
            ['You open your eyes and rise', '#USER# opens their eyes and rises'],
            ['You stand and let your hands fall to your sides', '#USER# stands and lets their hands fall to their sides'],
            ['You lift your head and release a slow breath', '#USER# lifts their head and releases a slow breath'],
            ['You blink slowly as you return to the present', '#USER# blinks slowly as they return to the present']
        ]

        self.LINES_SUCCESS = [
            'You get a faint vision of a bright silhouette',
            'You feel calm and peaceful',
            'You get a feeling of warmth',
            'You feel enlightened',
            'You feel pure',
            'You sense a gentle presence',
            'You feel blessed',
            'You feel watched over',
            'You sense something divine',
            'You feel inner clarity'
        ]

        self.LINES_FAIL = [
            'You get a faint vision of a dark silhouette',
            'You feel anxious and scared',
            'You get a feeling of cold',
            'You feel lost',
            'You feel anger',
            'You sense a harsh presence',
            'You feel judged',
            'You feel a growing dread',
            'You sense something is wrong',
            'You feel a deep unease'
        ]

        self.owner = owner
        self.ticks_passed = 0
        self.charging = False

        self.ticks_to_seconds = 30
        self.ticks_for_charge = 5 * self.ticks_to_seconds

        self.line_id = 0

        self.charges = 0
        self.tries = 0

        self.tick_since_prayer_end = 0
    
    def fail(self):
        self.owner.sendLine(random.choice(self.LINES_FAIL))
        self.ticks_passed = - self.ticks_for_charge
        self.charges -= 1

    def success(self):
        self.charges += 1
        self.owner.sendLine(random.choice(self.LINES_SUCCESS))
        self.ticks_passed = 0
        

    def stop(self):
        if not self.charging:
            return
        self.tick_since_prayer_end = self.owner.factory.ticks_passed
        #self.owner.sendLine('You stop charging')
        self.owner.simple_broadcast(self.LINES_STOP[self.line_id][0],self.LINES_STOP[self.line_id][1].replace('#USER#',self.owner.pretty_name()))
        self.charging = False
        if self.charges <= 0:
            self.charges = 0
        self.owner.gain_exp(self.charges)
        

    def start(self):
        if self.tick_since_prayer_end + (30*3) - self.owner.factory.ticks_passed >= 0:
            self.owner.sendLine('You just prayed and need a moment to reflect')
            return
        #self.owner.sendLine('You begin to charge')
        self.line_id = random.randint(0,len(self.LINES_START)-1)
        self.owner.simple_broadcast(self.LINES_START[self.line_id][0],self.LINES_START[self.line_id][1].replace('#USER#',self.owner.pretty_name()))
        self.charging = True
        self.ticks_passed = 0
        self.charges = 0
        self.tries = 0

    def toggle(self):
        if self.charging:
            self.stop()
        else:
            self.start()

    def charge(self):
        #charge_tick_amount = self.ticks_passed / self.ticks_to_seconds
        
        roll = random.randint(0,10)
        if roll > self.charges:
            self.success()
        else:
            self.fail()
        self.tries += 1

        if self.tries >= 10:
            self.stop()

    def tick(self):
        if not self.charging:
            return
        
        self.ticks_passed += 1
        if self.ticks_passed == self.ticks_for_charge:
            self.charge()
            
@check_not_in_combat
def command_charging_mini_game_toggle(self, line):
    self.charging_mini_game.toggle()