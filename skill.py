import constants
import emojis
import formulas
import messager
from battler import Battler


class Skill:
    """
    Class that represents a Jutsu (skill) inside the game.
    """

    def __init__(
        self, name: str, description: str, chakra_cost: int = 0, stamina_cost: int = 0,
        power: int = 0, element: str = "Nenhum", cooldown: int = 1, tags: list = None,
        percentage_cost: bool = False, skill_type: str = constants.SKILL_TYPE_NINJUTSU,
    ):
        self.name = name
        self.description = description
        self.chakra_cost = chakra_cost
        self.stamina_cost = stamina_cost
        self.power = power
        self.element = element
        self.cooldown = cooldown
        self.tags = tags if tags is not None else []
        self.percentage_cost = percentage_cost
        self.skill_type = skill_type

    def effect(self, player_name: str, caster: Battler, target: Battler) -> None:
        emoji = emojis.element_to_emoji.get(self.element) or emojis.skill_type_to_emoji.get(self.skill_type, emojis.NINJA_EMOJI)
        messager.add_message(player_name, f'{caster.name} usa "{self.name}" {emoji}!')

        if self.skill_type == constants.SKILL_TYPE_NINJUTSU:
            self._apply_ninjutsu_damage(player_name, caster, target)
        elif self.skill_type == constants.SKILL_TYPE_TAIJUTSU:
            self._apply_taijutsu_damage(player_name, caster, target)
        elif self.skill_type == constants.SKILL_TYPE_GENJUTSU:
            self._apply_genjutsu(player_name, caster, target)

        if constants.SKILL_TAG_HEALING in self.tags:
            amount = formulas.healing_spell_power(self.power, caster.stats[constants.NINJUTSU_STATKEY])
            if caster.name == target.name:
                messager.add_message(player_name, f"{caster.name} se cura em {amount} HP!")
            else:
                messager.add_message(player_name, f"{caster.name} cura {target.name} em {amount} HP!")
            target.heal(amount)

        if constants.SKILL_TAG_RECOVER_CHAKRA in self.tags:
            amount = formulas.healing_spell_power(self.power, caster.stats[constants.NINJUTSU_STATKEY])
            messager.add_message(player_name, f"{caster.name} recupera {amount} de Chakra!")
            caster.recover_chakra(amount)

        if constants.SKILL_TAG_SHIELD in self.tags:
            amount = int(caster.stats[constants.MAXHP_STATKEY] * self.power / 100)
            caster.shield = amount
            messager.add_message(player_name, f"{caster.name} ganha um escudo de {amount}!")

        if constants.SKILL_TAG_INFLICT_BUFF_DEBUFF in self.tags:
            self.buff_debuff_logic(player_name, target)
        if constants.SKILL_TAG_SELF_INFLICT_BUFF_DEBUFF in self.tags:
            self.buff_debuff_logic(player_name, caster)

        if constants.SKILL_TAG_SELF_REMOVE_DEBUFFS in self.tags:
            caster.remove_all_debuffs()
            messager.add_message(player_name, f"{caster.name} remove seus debuffs!")
        if constants.SKILL_TAG_REMOVE_DEBUFFS in self.tags:
            target.remove_all_debuffs()
            messager.add_message(player_name, f"{target.name} tem seus debuffs removidos!")
        if constants.SKILL_TAG_REMOVE_BUFFS in self.tags:
            target.remove_all_buffs()
            messager.add_message(player_name, f"{target.name} tem seus buffs removidos!")

    def _apply_ninjutsu_damage(self, player_name: str, caster: Battler, target: Battler) -> None:
        ninjutsu_mult = getattr(caster, 'ninjutsu_mult', 1.0)
        level = getattr(caster, 'lvl', 1)
        damage = formulas.damage_ninjutsu(
            self.power, caster.stats[constants.NINJUTSU_STATKEY],
            target.stats[constants.MDEF_STATKEY], level=level,
            ninjutsu_mult=ninjutsu_mult,
            attacker_element=self.element, defender_element=getattr(target, 'element', "Nenhum"),
        )
        if constants.SKILL_TAG_DEBUFF_EXPLOIT in self.tags:
            damage += damage // 2 * target.get_number_of_debbufs()
        if constants.SKILL_TAG_RAINBOW in self.tags:
            damage = target.take_damage(damage, constants.RAINBOW_ELEMENTAL_ATTACK)
        else:
            damage = target.take_damage(damage, self.element)
        messager.add_message(player_name, f"{target.name} recebe {damage} de dano!")
        if constants.SKILL_TAG_LEECH in self.tags:
            heal_amt = formulas.leech_calculation(damage)
            caster.heal(heal_amt)
            messager.add_message(player_name, f"{caster.name} absorve {heal_amt} HP!")

    def _apply_taijutsu_damage(self, player_name: str, caster: Battler, target: Battler) -> None:
        taijutsu_mult = getattr(caster, 'taijutsu_mult', 1.0)
        damage = formulas.damage_taijutsu(
            self.power, caster.stats[constants.ATK_STATKEY],
            target.stats[constants.DEF_STATKEY], taijutsu_mult=taijutsu_mult,
        )
        damage, is_crit = formulas.check_for_critical_damage(caster, damage)
        damage = target.take_damage(damage, None)
        if is_crit:
            messager.add_message(player_name, f"Golpe crítico! {target.name} recebe {damage} de dano!")
        else:
            messager.add_message(player_name, f"{target.name} recebe {damage} de dano!")

    def _apply_genjutsu(self, player_name: str, caster: Battler, target: Battler) -> None:
        damage = formulas.damage_genjutsu(
            self.power, caster.stats[constants.NINJUTSU_STATKEY],
            target.stats[constants.MDEF_STATKEY],
        )
        damage = target.take_damage(damage, self.element)
        messager.add_message(player_name, f"{target.name} recebe {damage} de dano mental!")
        duration = constants.GENJUTSU_DEBUFF_DURATION
        if constants.SKILL_TAG_PARALYSIS in self.tags:
            target.add_buff_debuff(constants.DEBUFF_PARALYSIS, duration)
            messager.add_message(player_name, f"{target.name} está paralisado! {emojis.buff_debuff_to_emoji['PARALYSIS']}")
        if constants.SKILL_TAG_CONFUSION in self.tags:
            target.add_buff_debuff(constants.DEBUFF_CONFUSION, duration)
            messager.add_message(player_name, f"{target.name} está confuso! {emojis.buff_debuff_to_emoji['CONFUSION']}")
        self.buff_debuff_logic(player_name, target)

    def buff_debuff_logic(self, player_name: str, who: Battler):
        buffs_and_debuffs = list(set(constants.BUFFS) & set(self.tags) | set(constants.DEBUFFS) & set(self.tags))
        for bd in buffs_and_debuffs:
            if bd in (constants.DEBUFF_PARALYSIS, constants.DEBUFF_CONFUSION):
                continue
            who.add_buff_debuff(bd)
            messager.add_message(
                player_name,
                f"{who.name} stats alterados! {constants.BUFF_DEBUFF_TO_MESSAGE[bd]} "
                f"{emojis.buff_debuff_to_emoji.get(bd, '')}!",
            )

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @property
    def chakra_cost(self) -> int:
        return self._chakra_cost

    @chakra_cost.setter
    def chakra_cost(self, value: int) -> None:
        self._chakra_cost = value

    @property
    def stamina_cost(self) -> int:
        return self._stamina_cost

    @stamina_cost.setter
    def stamina_cost(self, value: int) -> None:
        self._stamina_cost = value

    @property
    def power(self) -> int:
        return self._power

    @power.setter
    def power(self, value: int) -> None:
        self._power = value

    @property
    def element(self) -> str:
        return self._element

    @element.setter
    def element(self, value: str) -> None:
        self._element = value

    @property
    def skill_type(self) -> str:
        return self._skill_type

    @skill_type.setter
    def skill_type(self, value: str) -> None:
        self._skill_type = value
