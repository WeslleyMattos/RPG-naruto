import data_management
import enemy
import random
import copy
import warnings
import constants


class Area:
    """Stores information about ninja mission areas in the game."""

    def __init__(
        self, name: str, number: int, enemy_list: list, boss: str,
        dungeons: list, treasures: list, min_rank: str = "Estudante da Academia",
    ):
        self.name = name
        self.number = number
        self.enemy_list = enemy_list
        self.boss = boss
        self.dungeons = dungeons
        self.treasures = treasures
        self.min_rank = min_rank

    def player_can_access(self, player_rank: str) -> bool:
        player_idx = constants.RANK_INDEX.get(player_rank, 0)
        required_idx = constants.RANK_INDEX.get(self.min_rank, 0)
        return player_idx >= required_idx

    def spawn_random_enemy(self) -> enemy.Enemy:
        enemy_name = random.choice(self.enemy_list)
        enemy_inst = data_management.search_cache_enemy_by_name(enemy_name)
        return copy.deepcopy(enemy_inst)

    def spawn_boss(self) -> enemy.Enemy:
        enemy_inst = data_management.search_cache_enemy_by_name(self.boss)
        return copy.deepcopy(enemy_inst)

    def spawn_random_treasure(self) -> str:
        return random.choice(self.treasures)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if value:
            self._name = value
        else:
            raise ValueError("An area's name cannot be empty.")

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, value: int) -> None:
        if value >= 0:
            self._number = value
        else:
            raise ValueError("Area's number cannot be negative.")

    @property
    def enemy_list(self) -> list:
        return self._enemy_list

    @enemy_list.setter
    def enemy_list(self, value: list) -> None:
        if len(value) == 0:
            raise ValueError("An area's enemy list cannot be empty.")
        self._enemy_list = value

    @property
    def boss(self) -> str:
        return self._boss

    @boss.setter
    def boss(self, value: str) -> None:
        if value:
            self._boss = value
        else:
            raise ValueError("An area needs to have a boss.")

    @property
    def treasures(self) -> list:
        return self._treasures

    @treasures.setter
    def treasures(self, value: list) -> None:
        if len(value) == 0:
            warnings.warn("An area's treasure list is empty.")
        self._treasures = value

    @property
    def min_rank(self) -> str:
        return self._min_rank

    @min_rank.setter
    def min_rank(self, value: str) -> None:
        self._min_rank = value
