import uuid

from configuration.config import SKILLS, ItemType
from items.misc import Item
from skills.manager import get_skills, use_skill_from_consumable
from systems.utils import get_object_parent


class ConsumableSkillManager:
    def __init__(self, item):
        self.item = item
        self.skills = []


class Consumable(Item):
    def __init__(self):
        super().__init__()
        self.item_type = ItemType.CONSUMABLE
        self.stack_max = 3

        self.skill_manager = ConsumableSkillManager(self)

        self.use_perspectives = {
            "you on you": "no use perspective, check Consumable Class",
            "you on other": "no use perspective, check Consumable Class",
            "user on user": "no use perspective, check Consumable Class",
            "user on you": "no use perspective, check Consumable Class",
            "user on other": "no use perspective, check Consumable Class",
            "you on you fail": "no use perspective, check Consumable Class",
            "you on other fail": "no use perspective, check Consumable Class",
            "user on user fail": "no use perspective, check Consumable Class",
            "user on you fail": "no use perspective, check Consumable Class",
            "user on other fail": "no use perspective, check Consumable Class",
        }

    def to_dict(self):
        my_dict = {"skills": self.skill_manager.skills} | super().to_dict()

        return my_dict

    def identify(self, identifier=None):
        output = super().identify()

        id_to_name, name_to_id = get_skills()
        output += f"Contents: {[id_to_name[skill_id] for skill_id in self.skill_manager.skills]}"
        # output += f'Contents: {self.skill_manager.skills}'
        return output

    def use(self, user, target):
        if get_object_parent(target) != "Actor":
            super().use(user, target)
            return

        # do these checks if the user is attempting to use the item on something else
        if user is not target:
            if user.room.combat == None:
                user.sendLine("You can't use items on others out of combat")
                return

            if user not in user.room.combat.participants.values():
                user.sendLine(
                    f"You can't use items on others while you are not in combat"
                )
                return

            if target not in user.room.combat.participants.values():
                user.sendLine(
                    f"You can't use items on others while they are not fighting"
                )
                return

        first_skill = True
        for skill in self.skill_manager.skills:
            use_skill_from_consumable(
                user=user, target=target, skill_id=skill, consumable_item=self
            )
        user.inventory_manager.remove_item(self, stack=1)
        return True
