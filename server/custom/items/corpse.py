from configuration.constants.item_type import ItemType
from items.misc import Item
class CustomCorpse(Item):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'shiiiit'
    
    def after_init(self):
        if self.item_properties == {}:
            return
        self.name = f"Corpse of {self.item_properties['corpse_npc_name']}"
        self.description = f"The rotting corpse of {self.item_properties['corpse_npc_name']}"