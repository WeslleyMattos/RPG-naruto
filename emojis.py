# /// YOUR ICON DICTIONARY HERE /// #
ICON_DICT = {}

'''
Status Icons
'''

HP_EMOJI = '\U00002764'
CHAKRA_EMOJI = '\U0001F300'
STAMINA_EMOJI = '\U000026A1'
RYO_EMOJI = '\U0001F4B4'

'''
Normal Icons/Emojis
'''

SPARKLER_EMOJI = '\U0001F387'
SKULL_EMOJI = '\U0001F480'
CHARACTER_EMOJI = '\U0001F9D9'
CROSSED_SWORDS_EMOJI = '\U00002694'
CASTLE_EMOJI = '\U0001F3F0'
NINJA_EMOJI = '\U0001F977'
CRYSTAL_BALL_EMOJI = '\U0001F52E'
BED_EMOJI = '\U0001F6CF'
SHOP_EMOJI = '\U0001F6D2'
EXTRACT_ESSENCE_EMOJI = '\U0001F48E'
MAP_EMOJI = '\U0001F4CD'
SHIELD_EMOJI = '\U0001F6E1'
DAGGER_EMOJI = '\U0001F5E1'
HEART_EMOJI = '\U00002764'
SCROLL_EMOJI = '\U0001F4DC'
MISSION_EMOJI = '\U0001F4CB'
CHEST_EMOJI = '\U0001F4E6'

'''
Escordia Icons (fallback to unicode when ICON_DICT is empty)
'''

def _icon(key: str, fallback: str) -> str:
    return ICON_DICT.get(key, fallback)


ESC_RYO_ICON = _icon("RyoIcon", RYO_EMOJI)
ESC_ESSENCE_ICON = _icon("EssenceIcon", '\U0001F48E')
ESC_DUNGEON_ICON = _icon("DungeonIcon", CASTLE_EMOJI)
ESC_CHEST_ICON = _icon("ChestIcon", CHEST_EMOJI)

ESC_KUNAI_ICON = _icon("KunaiIcon", DAGGER_EMOJI)
ESC_SHURIKEN_ICON = _icon("ShurikenIcon", '\U00002B50')
ESC_KATANA_ICON = _icon("KatanaIcon", '\U0001F5E1')
ESC_STAFF_ICON = _icon("StaffIcon", '\U0001FA93')
ESC_FAN_ICON = _icon("FanIcon", '\U0001F38A')
ESC_SCROLL_ICON = _icon("ScrollIcon", SCROLL_EMOJI)

ESC_HEADBAND_ICON = _icon("HeadbandIcon", '\U0001F3BD')
ESC_FLAK_ICON = _icon("FlakIcon", SHIELD_EMOJI)
ESC_TOOL_ICON = _icon("ToolIcon", SCROLL_EMOJI)

ESC_ATK_DOWN_ICON = _icon("AtkDownIcon", '\U00002B07')
ESC_ATK_UP_ICON = _icon("AtkUpIcon", '\U00002B06')
ESC_DEF_DOWN_ICON = _icon("DefDownIcon", '\U00002B07')
ESC_DEF_UP_ICON = _icon("DefUpIcon", '\U00002B06')
ESC_NINJ_DOWN_ICON = _icon("NinjDownIcon", '\U00002B07')
ESC_NINJ_UP_ICON = _icon("NinjUpIcon", '\U00002B06')
ESC_MDEF_DOWN_ICON = _icon("MdfDownIcon", '\U00002B07')
ESC_MDEF_UP_ICON = _icon("MdfUpIcon", '\U00002B06')
ESC_LUK_DOWN_ICON = _icon("LukDownIcon", '\U00002B07')
ESC_LUK_UP_ICON = _icon("LukUpIcon", '\U00002B06')

'''
Element & Clan Emojis
'''

element_to_emoji = {
    "Nenhum": '\U000026AA',
    "Katon": '\U0001F525',
    "Suiton": '\U0001F4A7',
    "Doton": '\U0001FAA8',
    "Fuuton": '\U0001F4A8',
    "Raiton": '\U000026A1',
}

clan_to_emoji = {
    "Nenhum": '\U000026AA',
    "Uchiha": '\U0001F441',
    "Senju": '\U0001F333',
    "Hyuuga": '\U0001F52D',
    "Uzumaki": '\U0001F9E9',
    "Nara": '\U0001F319',
    "Inuzuka": '\U0001F415',
    "Aburame": '\U0001F41B',
}

skill_type_to_emoji = {
    "Ninjutsu": CHAKRA_EMOJI,
    "Taijutsu": STAMINA_EMOJI,
    "Genjutsu": CRYSTAL_BALL_EMOJI,
}

equipment_to_emoji = {
    "HEADBAND": ESC_HEADBAND_ICON, "MASK": ESC_HEADBAND_ICON,
    "FLAK_JACKET": ESC_FLAK_ICON, "ANBU_ARMOR": ESC_FLAK_ICON, "ROBE": ESC_FLAK_ICON,
    "KUNAI": ESC_KUNAI_ICON, "SHURIKEN": ESC_SHURIKEN_ICON, "KATANA": ESC_KATANA_ICON,
    "STAFF": ESC_STAFF_ICON, "FAN": ESC_FAN_ICON, "CLAWS": DAGGER_EMOJI,
    "SCROLL": ESC_SCROLL_ICON, "PILL": '\U0001F48A', "SEAL": '\U0001F516',
    "TOOL": ESC_TOOL_ICON,
}

buff_debuff_to_emoji = {
    "ATK_UP": ESC_ATK_UP_ICON, "ATK_DOWN": ESC_ATK_DOWN_ICON,
    "DEF_UP": ESC_DEF_UP_ICON, "DEF_DOWN": ESC_DEF_DOWN_ICON,
    "NINJ_UP": ESC_NINJ_UP_ICON, "NINJ_DOWN": ESC_NINJ_DOWN_ICON,
    "MDEF_UP": ESC_MDEF_UP_ICON, "MDEF_DOWN": ESC_MDEF_DOWN_ICON,
    "LUK_UP": ESC_LUK_UP_ICON, "LUK_DOWN": ESC_LUK_DOWN_ICON,
    "PARALYSIS": '\U000026D4', "CONFUSION": '\U0001F4AB',
}


object_type_to_emoji = {
    "LOOT": CHEST_EMOJI,
    "CONSUMABLE": '\U0001F48A',
    "KEY_ITEM": SCROLL_EMOJI,
}


def obj_emoji(item: 'Item') -> str:
    try:
        if item.object_type == "EQUIPMENT":
            return equipment_to_emoji.get(item.equipment_type, NINJA_EMOJI)
        return object_type_to_emoji.get(item.object_type, NINJA_EMOJI)
    except Exception:
        return NINJA_EMOJI


def select_emoji(emoji: str):
    """Returns a valid emoji for Discord SelectOption, or None to omit the field."""
    if emoji and str(emoji).strip():
        return emoji
    return None


def skill_emoji(skill: 'Skill', clan: str = None) -> str:
    try:
        if skill.element and skill.element in element_to_emoji:
            return element_to_emoji[skill.element]
        if skill.skill_type in skill_type_to_emoji:
            return skill_type_to_emoji[skill.skill_type]
        if clan and clan in clan_to_emoji:
            return clan_to_emoji[clan]
        return NINJA_EMOJI
    except Exception:
        return NINJA_EMOJI
