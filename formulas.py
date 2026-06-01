import math
import random
import constants


def xp_next_lvl_formula(xp_to_next_lvl: int, lvl: int) -> int:
    return round(xp_to_next_lvl * 1.25 + 5 * lvl * lvl / 2)


def ryo_lost_when_dying(ryo: int) -> int:
    return ryo // 2


def miss_formula(atk_speed: int, def_speed: int) -> int:
    return math.floor(math.sqrt(max(0, (5 * def_speed - atk_speed * 2))))


def check_for_critical_damage(attacker: 'Battler', dmg: int) -> (int, bool):
    if 'CRITCH' in attacker.stats:
        if random.randint(0, 100) <= attacker.stats['CRITCH']:
            return int(dmg + dmg * attacker.stats['CRITDMG'] / 100), True
    return dmg, False


def normal_attack_dmg(atk_value: int, def_value: int) -> int:
    return round(atk_value * (100 / (100 + def_value * 1.5)))


def healing_spell_power(spell_power: int, ninj_value: int) -> int:
    return int(spell_power * (100 + ninj_value * 1.5) / 100)


def elemental_multiplier(attacker_element: str, defender_element: str) -> float:
    if not attacker_element or attacker_element == "Nenhum":
        return 1.0
    if not defender_element or defender_element == "Nenhum":
        return 1.0
    if constants.ELEMENT_BEATS.get(attacker_element) == defender_element:
        return constants.ELEMENTAL_ADVANTAGE_BONUS
    if constants.ELEMENT_BEATS.get(defender_element) == attacker_element:
        return constants.ELEMENTAL_DISADVANTAGE_REDUCTION
    return 1.0


def damage_ninjutsu(
    spell_power: int, ninj_value: int, mdef_value: int, level: int = 1,
    ninjutsu_mult: float = 1.0, attacker_element: str = None, defender_element: str = None,
) -> int:
    base = spell_power * ninj_value / 10 * (100 / (100 + mdef_value * 1.5))
    base *= (1 + level * 0.05)
    base *= ninjutsu_mult
    base *= elemental_multiplier(attacker_element, defender_element)
    return int(base)


def damage_taijutsu(
    spell_power: int, atk_value: int, def_value: int, taijutsu_mult: float = 1.0,
) -> int:
    base = spell_power * atk_value / 10 * (100 / (100 + def_value * 1.5))
    return int(base * taijutsu_mult)


def damage_genjutsu(spell_power: int, ninj_value: int, mdef_value: int) -> int:
    """Genjutsu deals minimal direct damage; debuffs are the main effect."""
    return int(spell_power * ninj_value / 20 * (100 / (100 + mdef_value * 2)))


def leech_calculation(damage: int) -> int:
    return round(damage * constants.LEECH_AMOUNT)


def apply_chakra_reduction(base_cost: int, reduction: float) -> int:
    return max(0, int(math.ceil(base_cost * (1 - reduction))))
