import constants
from item import Item


class Equipment(Item):

    def __init__(
        self, name, description, individual_value, object_type, equipment_type,
        stat_change_list, ninjutsu_mult=1.0, taijutsu_mult=1.0, chakra_reduction=0.0,
    ):
        super().__init__(name, description, individual_value, object_type)
        self.equipment_type = equipment_type
        self.stat_change_list = stat_change_list
        self.ninjutsu_mult = ninjutsu_mult
        self.taijutsu_mult = taijutsu_mult
        self.chakra_reduction = chakra_reduction

    def translate_equipment_type(self) -> str:
        if self.equipment_type in constants.HEADBAND_TYPES:
            return constants.HEADBAND_KEY
        elif self.equipment_type in constants.ARMOR_TYPES:
            return constants.ARMOR_KEY
        elif self.equipment_type in constants.WEAPON_TYPES:
            return constants.WEAPON_KEY
        elif self.equipment_type in constants.TOOL_TYPES:
            return constants.TOOL_KEY
        return constants.TOOL_KEY

    def stat_list_formatted(self) -> str:
        stat_list = []
        for stat in self.stat_change_list:
            val = self.stat_change_list[stat]
            stat_list.append(f"{stat} +{val}" if val >= 0 else f"{stat} {val}")
        if self.ninjutsu_mult > 1.0:
            stat_list.append(f"Ninjutsu x{self.ninjutsu_mult:.2f}")
        if self.taijutsu_mult > 1.0:
            stat_list.append(f"Taijutsu x{self.taijutsu_mult:.2f}")
        if self.chakra_reduction > 0:
            stat_list.append(f"Chakra -{int(self.chakra_reduction * 100)}%")
        return ', '.join(stat_list)
