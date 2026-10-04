from configuration.constants.item_type import ItemType
from items.misc import Item
from custom.utils import CustomDialogQuestionList

class CustomLetter(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_properties['letter_title'] = ''
        self.item_properties['letter_message'] = ''
        self.item_properties['letter_signed'] = ''

        self.trigger_manager.trigger_add('write', self.trigger_write)

    def question_list_dialog_answers(self, dialog_obj):
        if len(dialog_obj.answers['title']) >= 30:
            dialog_obj.player.send_line('The title of this letter is too long (max 30)')
            return
        if len(dialog_obj.answers['message']) >= 200:
            dialog_obj.player.send_line('The content of this letter is too long (max 200)')
            return

        self.item_properties['letter_title'] = dialog_obj.answers['title']
        self.item_properties['letter_message'] = dialog_obj.answers['message']
        self.item_properties['letter_signed'] = dialog_obj.player.id

        dialog_obj.player.send_line('You seal the letter')


    def trigger_write(self, player, line):
        item_name_or_id = line.replace('write ','')
        item_found = player.get_item(item_name_or_id)
        if item_found != [self]:
            return False

        if self.item_properties['letter_signed'] != '':
            player.send_line('This letter has already been written in')
            return True

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
        if self.item_properties['letter_signed'] == '':
            self.description = 'An unwritte letter, you can write in it if you want'
        else:
            if self.item_properties['letter_title'] != '':
                self.name = 'Letter titled "' + self.item_properties['letter_title'] +'"'
            if self.item_properties['letter_message'] != '':
                self.description = self.item_properties['letter_message']
            if self.item_properties['letter_signed'] != '':
                _name = self.room.world.factory.db.get_actor_name_from_id(self.item_properties['letter_signed'])
                self.description += f'\nSigned by {_name}'

    def pretty_name(self, *args, **kwargs):
        self.fix()
        return super().pretty_name(*args, **kwargs)

    def identify(self, *args, **kwargs):
        self.fix()
        return super().identify(*args, **kwargs)
