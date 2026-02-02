class TriggerManager:
    def __init__(self, trigger_owner):
        self.trigger_owner = trigger_owner
        self.triggers = {}

    def trigger_add(self, trigger_key, trigger_action):
        self.triggers[trigger_key] = {'trigger_key': trigger_key, 'trigger_action': trigger_action}

    def trigger_remove(self, trigger_key):
        if trigger_key in self.triggers:
            del self.triggers[trigger_key]

    def trigger_check(self, player, line):
        for i in self.triggers.values():
            if '123'+i['trigger_key'] not in '123'+line:
                continue

            # if the trigger does not return True then it failed some internal check
            # and should be ignored
            if i['trigger_action'](player, line):
                return True # found something that triggered
        return False # did not find anything to trigger
