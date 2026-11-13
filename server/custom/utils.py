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
            'question_id_1':    'this is the question that is printed',
            'question_id_2':    'this is the question that is printed 2',
        }

        self.options = {}

        if 'questions' in kwargs:
            self.questions = kwargs['questions']
            del kwargs['questions']

        self.options = {
            'question_id_1': {
                'answer_id_1':    'the answer that is printed',
                'answer_id_2':    'the answer that is printed',

            },
            'question_id_2': {
                'answer_id_1':    'the answer that is printed',
                'answer_id_2':    'the answer that is printed',

            },
        }

        self.options = {}

        if 'options' in kwargs:
            self.options = kwargs['options']
            del kwargs['options']

        self.question_list_dialog_answers_function = None
        if 'question_list_dialog_answers_function' in kwargs:
            self.question_list_dialog_answers_function = kwargs['question_list_dialog_answers_function']
            del kwargs['question_list_dialog_answers_function']

        super().__init__(*args, **kwargs)
        # key is the key / var and the value is the answer of the player / the question
        
        # this gets filled with key and vals
        self.answers = {}
        self.current_step = 0
        

    def end_dialog(self, forced = 1, dont_run_function_to_run = False):
        if self.question_list_dialog_answers_function == None:
            function_to_run = self.npc.question_list_dialog_answers
        else:
            function_to_run = self.question_list_dialog_answers_function

        if dont_run_function_to_run:
            return super().end_dialog()

        if forced == 1:
            function_to_run(self)
            return super().end_dialog()

    def print_dialog(self):
        if self.current_step >= len(self.questions):
            return

        key = list(self.questions.keys())[self.current_step]
        self.player.send_line(f'{self.questions[key]}')
        
        i = 1
        if len(self.options) == 0:
            return
        if len(self.options) >= self.current_step:
            # these are the options for dialog lines
            options = list(self.options.values())[self.current_step]

            # now get each individual answer from those options
            for option in options:

                # add godot 
                if self.player.protocol.enabled_godot:
                    option = f'[url={option}]' + options[option].replace('\n', '[/url]\n')
                else:
                    option = options[option]

                self.player.send_line(f'{i}: {option}')
                i += 1

    def answer(self, line):
        key = list(self.questions.keys())[self.current_step]
        if line.lower() in 'cancel stop 0 quit no n'.split(' '):
            self.end_dialog(dont_run_function_to_run = True)
            self.player.send_line('action cancelled')
            return True

        self.answers[key] = line
        
        # if your answer is an intiger and it exists in options
        # then assign the intiger to the options id
        try:
            line = int(line)-1
            options = list(self.options.values())[self.current_step]
            _answer = list(options.keys())[line]
            self.answers[key] = _answer
        except (ValueError, IndexError) as e:
            pass

        self.current_step += 1
        self.print_dialog()

        if self.current_step >= len(self.questions):
            self.end_dialog(1)
            return True

        return True