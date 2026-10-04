from configuration.constants.item_type import ItemType
from items.misc import Item
from custom.utils import CustomDialogQuestionList

class CustomLetter(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_properties['letter_title'] = ''
        self.item_properties['letter_message'] = ''
        self.item_properties['letter_sealed'] = ''
        self.item_properties['letter_signed'] = ''

        self.trigger_manager.trigger_add('write', self.trigger_set_title)

    def question_list_dialog_answers(self, dialog_obj):
        self.item_properties['letter_title'] = dialog_obj.answers['title']
        self.item_properties['letter_message'] = dialog_obj.answers['message']
        self.item_properties['letter_sealed'] = '1'
        self.item_properties['letter_signed'] = dialog_obj.player.id


    def trigger_set_title(self, player, line):
        questions = {
            'title':    'What would you like the TITLE of this letter to be?',
            'message':  'What would you like the CONTENT of this letter to be?',
        }
        player.current_dialog = CustomDialogQuestionList(player, self, _dialog_tree = None, questions = questions)
        player.current_dialog.print_dialog()
        return True

    def after_init(self):
        if self.item_properties == {}:
            return
   
    def fix(self):
        pass

    def pretty_name(self, *args, **kwargs):
        self.fix()
        return super().pretty_name(*args, **kwargs)

    def identify(self, *args, **kwargs):
        self.fix()
        return super().identify(*args, **kwargs)
