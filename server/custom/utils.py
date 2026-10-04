from systems.dialog import Dialog

class CustomDialogQuestionList(Dialog):
    def __init__(self, *args, **kwargs):
        self.dialog_tree = {
    
            "start": {
                "dialog": [
                {
                    "line": "slop"
                }
                ]
            },
            "write": {
                "append_to": "start",
                "options": [
                {
                    "line": "slop\n",
                    "goto": "start"
                }
                ]
            }
        }

        self.questions = {
            'a':    'a',
            'b':    'b',
        }

        if 'questions' in kwargs:
            self.questions = kwargs['questions']
            del kwargs['questions']

        super().__init__(*args, **kwargs)
        # key is the key / var and the value is the answer of the player / the question
        
        # this gets filled with key and vals
        self.answers = {}
        self.current_step = 0
        

    def end_dialog(self, forced = 0):
        if forced == 1:
            self.npc.question_list_dialog_answers(self)
            return super().end_dialog()

    def print_dialog(self):
        if self.current_step >= len(self.questions):
            return
        key = list(self.questions.keys())[self.current_step]
        self.player.send_line(f'{self.questions[key]}')

    def answer(self, line):
        key = list(self.questions.keys())[self.current_step]

        self.answers[key] = line

        self.current_step += 1
        self.print_dialog()

        if self.current_step >= len(self.questions):
            self.end_dialog(1)
            return True

        return True