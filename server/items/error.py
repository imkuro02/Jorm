from configuration.constants.item_type import ItemType
#from configuration.constants.equipment_slot_type import EquipmentSlotType
#from configuration.constants.stat_type import StatType
from items.misc import Item

class ErrorItem(Item):
    def __init__(self):
        super().__init__()
        self.item_type = ItemType.ERROR

    def identify(self, identifier = None):
        
        #output = super().identify()
        
        output = f'{self.name}: premade_id:{self.premade_id}\nTHIS ITEM HAS A FUCKED premade_id, it does not exist in config/items.yaml'
        return output