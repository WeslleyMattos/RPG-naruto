import math
import constants


class Battler:
    """
    Class that represents a Battler Character in the game (Player & Enemies)
    """

    def __init__(self, name: str, stats: dict):
        self.name = name
        self.stats = stats
        self.alive = True
        self.weaknesses = []
        self.resistances = []
        self.buffs_and_debuffs = {}
        self.shield = 0
        self.element = "Nenhum"

    def fully_heal(self) -> None:
        self.stats[constants.HP_STATKEY] = self.stats[constants.MAXHP_STATKEY]

    def fully_recover_chakra(self) -> None:
        self.stats[constants.CHAKRA_STATKEY] = self.stats[constants.MAXCHAKRA_STATKEY]

    def fully_recover_stamina(self) -> None:
        self.stats[constants.STAMINA_STATKEY] = self.stats[constants.MAXSTAMINA_STATKEY]

    def heal(self, amount: int) -> None:
        new_hp = self.stats[constants.HP_STATKEY] + amount
        if new_hp > self.stats[constants.MAXHP_STATKEY]:
            self.fully_heal()
        else:
            self.stats[constants.HP_STATKEY] = new_hp

    def recover_chakra(self, amount: int) -> None:
        new_chakra = self.stats[constants.CHAKRA_STATKEY] + amount
        if new_chakra > self.stats[constants.MAXCHAKRA_STATKEY]:
            self.fully_recover_chakra()
        else:
            self.stats[constants.CHAKRA_STATKEY] = new_chakra

    def recover_stamina(self, amount: int) -> None:
        new_stamina = self.stats[constants.STAMINA_STATKEY] + amount
        if new_stamina > self.stats[constants.MAXSTAMINA_STATKEY]:
            self.fully_recover_stamina()
        else:
            self.stats[constants.STAMINA_STATKEY] = new_stamina

    def take_damage(self, dmg: int, damage_element: str) -> int:
        if damage_element in self.weaknesses or damage_element == constants.RAINBOW_ELEMENTAL_ATTACK:
            dmg = round(dmg * constants.WEAKNESS_DAMAGE_BONUS)
        elif damage_element in self.resistances:
            dmg = round(dmg * constants.RESISTANCE_DAMAGE_REDUCTION)

        dmg = max(0, dmg)

        if self.shield > 0:
            damage_left = self.shield - dmg
            if damage_left < 0:
                self.shield = 0
                dmg = abs(damage_left)
            else:
                self.shield = damage_left
                dmg = 0

        self.stats[constants.HP_STATKEY] -= dmg

        if self.stats[constants.HP_STATKEY] <= 0:
            self.alive = False
            self.die()

        return dmg

    def die(self) -> None:
        print(f"{self.name} has died.")

    def is_paralyzed(self) -> bool:
        return constants.DEBUFF_PARALYSIS in self.buffs_and_debuffs

    def is_confused(self) -> bool:
        return constants.DEBUFF_CONFUSION in self.buffs_and_debuffs

    def add_buff_debuff(self, buff_debuff: str, duration: int = None) -> None:
        if buff_debuff in constants.BUFFS or buff_debuff in constants.DEBUFFS:
            if buff_debuff not in self.buffs_and_debuffs:
                if constants.BUFF_DEBUFF_CONTRARIES.get(buff_debuff) in self.buffs_and_debuffs:
                    contrary = constants.BUFF_DEBUFF_CONTRARIES[buff_debuff]
                    self.stat_change_on_buff_debuff(contrary, expires=True)
                    del self.buffs_and_debuffs[contrary]
                else:
                    self.stat_change_on_buff_debuff(buff_debuff, expires=False)
            dur = duration if duration is not None else constants.BUFF_DEBUFF_DURATION
            self.buffs_and_debuffs[buff_debuff] = dur
        else:
            raise ValueError(f"{buff_debuff} is not a valid buff or debuff.")

    def remove_all_debuffs(self) -> None:
        for debuff in constants.DEBUFFS:
            if debuff in self.buffs_and_debuffs:
                self.stat_change_on_buff_debuff(debuff, expires=True)
                del self.buffs_and_debuffs[debuff]

    def remove_all_buffs(self) -> None:
        for buff in constants.BUFFS:
            if buff in self.buffs_and_debuffs:
                self.stat_change_on_buff_debuff(buff, expires=True)
                del self.buffs_and_debuffs[buff]

    def get_number_of_debbufs(self):
        return len([bd for bd in self.buffs_and_debuffs if bd in constants.DEBUFFS])

    def stat_change_on_buff_debuff(self, buff_debuff: str, expires: bool = False) -> None:
        stat_affected = None
        if buff_debuff in constants.ATK_BD:
            stat_affected = constants.ATK_STATKEY
        elif buff_debuff in constants.DEF_BD:
            stat_affected = constants.DEF_STATKEY
        elif buff_debuff in constants.NINJ_BD:
            stat_affected = constants.NINJUTSU_STATKEY
        elif buff_debuff in constants.MDEF_BD:
            stat_affected = constants.MDEF_STATKEY
        elif buff_debuff in constants.LUK_BD:
            stat_affected = constants.CRITCH_STATKEY

        if stat_affected is None:
            return

        is_buff = buff_debuff in constants.BUFFS
        if is_buff:
            if not expires:
                self.stats[stat_affected] = math.ceil(self.stats[stat_affected] * constants.BUFF_MULTIPLIER)
            else:
                self.stats[stat_affected] = math.floor(self.stats[stat_affected] / constants.BUFF_MULTIPLIER)
        else:
            if not expires:
                self.stats[stat_affected] = math.floor(self.stats[stat_affected] * constants.DEBUFF_MULTIPLIER)
            else:
                self.stats[stat_affected] = math.ceil(self.stats[stat_affected] / constants.DEBUFF_MULTIPLIER)

    def pay_costs(self, skill: 'Skill', chakra_reduction: float = 0.0) -> bool:
        import formulas
        chakra_cost = skill.chakra_cost
        stamina_cost = skill.stamina_cost
        if skill.percentage_cost:
            chakra_cost = int(math.ceil(self.stats[constants.MAXCHAKRA_STATKEY] * chakra_cost / 100))
        else:
            chakra_cost = formulas.apply_chakra_reduction(chakra_cost, chakra_reduction)

        if self.stats[constants.CHAKRA_STATKEY] < chakra_cost:
            return False
        if self.stats[constants.STAMINA_STATKEY] < stamina_cost:
            return False

        self.stats[constants.CHAKRA_STATKEY] -= chakra_cost
        self.stats[constants.STAMINA_STATKEY] -= stamina_cost

        if hasattr(self, 'chakra'):
            self.chakra = self.stats[constants.CHAKRA_STATKEY]
        if hasattr(self, 'stamina'):
            self.stamina = self.stats[constants.STAMINA_STATKEY]
        return True

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if value:
            self._name = value
        else:
            raise ValueError("Battler name cannot be empty.")

    @property
    def stats(self) -> dict:
        return self._stats

    @stats.setter
    def stats(self, value: dict) -> None:
        for stat in value:
            if stat not in constants.STATKEYS:
                raise ValueError(f"Invalid stat: {stat}")
        self._stats = value

    @property
    def alive(self) -> bool:
        return self._alive

    @alive.setter
    def alive(self, value: bool) -> None:
        self._alive = value

    @property
    def weaknesses(self) -> list:
        return self._weaknesses

    @weaknesses.setter
    def weaknesses(self, value: list) -> None:
        self._weaknesses = value

    @property
    def resistances(self) -> list:
        return self._resistances

    @resistances.setter
    def resistances(self, value: list) -> None:
        self._resistances = value

    @property
    def buffs_and_debuffs(self) -> dict:
        return self._buffs_and_debuffs

    @buffs_and_debuffs.setter
    def buffs_and_debuffs(self, value: dict) -> None:
        self._buffs_and_debuffs = value

    @property
    def shield(self) -> int:
        return self._shield

    @shield.setter
    def shield(self, value: int) -> None:
        if value < 0:
            raise ValueError("Shield cannot be negative.")
        self._shield = value
