import random
from battler import Battler


class Enemy(Battler):
    """
    Class that represent ninja enemies the player can encounter.
    """

    def __init__(
        self, name, stats, description, xp_reward, ryo_reward,
        possible_loot=None, loot_chance=0, skills=None, weaknesses=None,
        resistances=None, image_url='', is_boss=False, element="Nenhum",
    ):
        super().__init__(name, stats)
        self.description = description
        self.xp_reward = xp_reward
        self.ryo_reward = ryo_reward
        self.possible_loot = possible_loot
        self.loot_chance = loot_chance
        self.skills = skills if skills is not None else []
        self.weaknesses = weaknesses if weaknesses is not None else []
        self.resistances = resistances if resistances is not None else []
        self.image_url = image_url
        self.is_boss = is_boss
        self.element = element

    def die(self) -> None:
        self.alive = False

    def loot(self) -> str:
        if self.possible_loot is not None and random.randint(0, 100) <= self.loot_chance:
            return self.possible_loot
        return ''

    def key_item_loot(self) -> str:
        import constants
        if random.randint(0, 100) <= constants.KEY_ITEM_DROP_CHANCE:
            return random.choice(constants.KEY_ITEMS)
        return ''

    def show_enemy_info(self) -> str:
        info = ''.join([f'**{stat}**: {self.stats[stat]}\n' for stat in self.stats])
        if self.element != "Nenhum":
            info += f'**Elemento**: {self.element}\n'
        return info

    @property
    def xp_reward(self) -> int:
        return self._xp_reward

    @xp_reward.setter
    def xp_reward(self, value: int) -> None:
        if value < 0:
            raise ValueError("XP Reward of enemy cannot be negative.")
        self._xp_reward = value

    @property
    def ryo_reward(self) -> int:
        return self._ryo_reward

    @ryo_reward.setter
    def ryo_reward(self, value: int) -> None:
        if value < 0:
            raise ValueError("Ryo Reward of enemy cannot be negative.")
        self._ryo_reward = value

    @property
    def possible_loot(self) -> str:
        return self._possible_loot

    @possible_loot.setter
    def possible_loot(self, value: str) -> None:
        self._possible_loot = value

    @property
    def loot_chance(self) -> int:
        return self._loot_chance

    @loot_chance.setter
    def loot_chance(self, value: int) -> None:
        self._loot_chance = value

    @property
    def skills(self) -> list:
        return self._skills

    @skills.setter
    def skills(self, value: list) -> None:
        self._skills = value

    @property
    def image_url(self) -> str:
        return self._image_url

    @image_url.setter
    def image_url(self, value: str) -> None:
        self._image_url = value

    @property
    def is_boss(self) -> bool:
        return self._is_boss

    @is_boss.setter
    def is_boss(self, value: bool) -> None:
        self._is_boss = value
