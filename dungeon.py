import constants


class Dungeon:
    """Class holding all info related to ninja dungeons / instanced missions."""

    def __init__(
        self, dungeon_name: str, recommended_lvl: int, min_rank: str,
        enemy_list: list, boss: str, enemy_count: int, loot_pool: list,
        ryo_reward: int = 0,
    ):
        self.dungeon_name = dungeon_name
        self.recommended_lvl = recommended_lvl
        self.min_rank = min_rank
        self.enemy_list = enemy_list
        self.boss = boss
        self.enemy_count = enemy_count
        self.loot_pool = loot_pool
        self.ryo_reward = ryo_reward
        self.current_enemies_defeated = 0
        self.boss_defeated = False

    def player_can_enter(self, player_rank: str, player_level: int) -> bool:
        player_idx = constants.RANK_INDEX.get(player_rank, 0)
        required_idx = constants.RANK_INDEX.get(self.min_rank, 0)
        return player_idx >= required_idx and player_level >= self.recommended_lvl
