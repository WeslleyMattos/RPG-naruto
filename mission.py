import random
import time
import constants
import messager


class Mission:
    """Represents a ninja mission from the village mission board."""

    def __init__(
        self, name: str, description: str, rank: str, rank_required: str,
        stamina_cost: int, xp_reward: int, ryo_reward: int, duration: int = 0,
    ):
        self.name = name
        self.description = description
        self.rank = rank
        self.rank_required = rank_required
        self.stamina_cost = stamina_cost
        self.xp_reward = xp_reward
        self.ryo_reward = ryo_reward
        self.duration = duration

    def player_can_accept(self, player) -> bool:
        player_idx = constants.RANK_INDEX.get(player.ninja_rank, 0)
        required_idx = constants.RANK_INDEX.get(self.rank_required, 0)
        return player_idx >= required_idx

    def attempt_instant(self, player) -> bool:
        """
        Instant mission resolution with failure chance based on player stats.
        Higher level and rank improve success rate.
        """
        base_chance = 50 + player.lvl * 2
        rank_bonus = constants.RANK_INDEX.get(player.ninja_rank, 0) * 5
        rank_penalty = constants.MISSION_RANKS.index(self.rank) * 8 if self.rank in constants.MISSION_RANKS else 0
        success_chance = min(95, max(10, base_chance + rank_bonus - rank_penalty))
        return random.randint(1, 100) <= success_chance

    def complete(self, player) -> None:
        player.add_exp(self.xp_reward)
        player.add_ryo(self.ryo_reward)
        player.complete_mission(self.rank)
        messager.add_message(
            player.name,
            f"Missão '{self.name}' concluída! +{self.xp_reward} XP, +{self.ryo_reward} Ryo.",
        )


def accept_mission(player, mission: Mission) -> (bool, str):
    """Player accepts a mission, paying stamina cost."""
    if player.active_mission != "None":
        return False, "Você já tem uma missão em andamento."
    if not mission.player_can_accept(player):
        return False, f"Rank insuficiente. Requer: {mission.rank_required}."
    if not player.spend_stamina(mission.stamina_cost):
        return False, f"Stamina insuficiente. Custo: {mission.stamina_cost}."

    player.active_mission = mission.name
    if mission.duration > 0:
        player.mission_end_time = time.time() + mission.duration
        return True, f"Missão '{mission.name}' aceita! Retorne em {mission.duration}s."
    if mission.attempt_instant(player):
        mission.complete(player)
        player.active_mission = "None"
        player.mission_end_time = 0
        return True, "success"
    player.active_mission = "None"
    player.mission_end_time = 0
    messager.add_message(player.name, f"Missão '{mission.name}' falhou!")
    return True, "fail"


def check_mission_completion(player, mission_cache: dict) -> (bool, str):
    """Checks if a timed mission is ready to complete."""
    if player.active_mission == "None":
        return False, "Nenhuma missão ativa."
    if time.time() < player.mission_end_time:
        remaining = int(player.mission_end_time - time.time())
        return False, f"Missão em progresso. Aguarde {remaining}s."
    mission = mission_cache.get(player.active_mission)
    if mission is None:
        player.active_mission = "None"
        return False, "Missão não encontrada."
    if mission.attempt_instant(player):
        mission.complete(player)
        result = "success"
    else:
        result = "fail"
    player.active_mission = "None"
    player.mission_end_time = 0
    return True, result
