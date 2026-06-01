import data_management
import emojis
import error_msgs
import formulas
import constants
import messager
import inventory as inventory_module
from battler import Battler
from StringProgressBar import progressBar


# Placeholder for future data/clans.json integration
CLAN_BONUS_TEMPLATE = {
    "Uchiha": {"NINJ": 2, "NINJUTSU_MULT": 1.10},
    "Senju": {"MAXHP": 5, "MAXCHAKRA": 3},
    "Hyuuga": {"CRITCH": 3, "ATK": 2},
    "Uzumaki": {"MAXCHAKRA": 5, "CHAKRA_REGEN": 1},
    "Nara": {"MDEF": 3, "SPEED": 1},
    "Inuzuka": {"ATK": 3, "SPEED": 2},
    "Aburame": {"DEF": 3, "MDEF": 2},
}


class Player(Battler):
    """
    Class that represents a Player (Ninja) in the game.
    """

    def __init__(
        self, name: str, *, stats: dict = None, lvl: int = 1, xp: int = 0,
        xp_to_next_lvl: int = 15, xp_rate: float = 1, ryo: int = 50, essence: int = 0,
        chakra: int = 10, stamina: int = 100, clan: str = "Nenhum", element: str = "Nenhum",
        ninja_rank: str = "Estudante da Academia",
        inventory: inventory_module.Inventory = None, equipment: dict = None,
        skills: list = None, passives: list = None, current_area: int = 1,
        in_fight: bool = False, in_dungeon: bool = False, defeated_bosses: list = None,
        blessings: list = None, missions_completed: dict = None,
        active_mission: str = "None", mission_end_time: float = 0,
    ):
        if stats is None:
            stats = constants.INITIAL_STATS.copy()
        if skills is None:
            skills = ["First Aid"]
        if passives is None:
            passives = []
        if equipment is None:
            equipment = constants.INITIAL_EQUIPMENT.copy()
        if defeated_bosses is None:
            defeated_bosses = []
        if blessings is None:
            blessings = []
        if missions_completed is None:
            missions_completed = {rank: 0 for rank in constants.MISSION_RANKS}

        super().__init__(name, stats)

        self.lvl = lvl
        self.xp = xp
        self.xp_to_next_lvl = xp_to_next_lvl
        self.xp_rate = xp_rate
        self.ryo = ryo
        self.essence = essence
        self.chakra = chakra
        self.stamina = stamina
        self.clan = clan
        self.element = element
        self.ninja_rank = ninja_rank
        self.inventory = inventory
        self.equipment = equipment
        self.skills = skills
        self.passives = passives
        self.current_area = current_area
        self.in_fight = in_fight
        self.in_dungeon = in_dungeon
        self.defeated_bosses = defeated_bosses
        self.blessings = blessings
        self.missions_completed = missions_completed
        self.active_mission = active_mission
        self.mission_end_time = mission_end_time
        self.dungeon_cooldowns = {}
        self.ninjutsu_mult = 1.0
        self.taijutsu_mult = 1.0
        self.chakra_reduction = 0.0
        self._clan_bonuses_applied = False

        self._sync_resource_stats()

    def _sync_resource_stats(self) -> None:
        """Keeps chakra/stamina columns in sync with the stats dict."""
        self.stats[constants.CHAKRA_STATKEY] = self.chakra
        self.stats[constants.STAMINA_STATKEY] = self.stamina

    def apply_clan_bonuses(self) -> None:
        """
        Applies passive bonuses based on clan.
        Future: load from data/clans.json instead of CLAN_BONUS_TEMPLATE.
        """
        if self.clan == "Nenhum" or self._clan_bonuses_applied:
            return
        if self.clan not in CLAN_BONUS_TEMPLATE:
            return
        for stat, bonus in CLAN_BONUS_TEMPLATE[self.clan].items():
            if stat == "NINJUTSU_MULT":
                self.ninjutsu_mult += bonus - 1.0
            elif stat in self.stats:
                self.stats[stat] += bonus
            elif stat == "MAXCHAKRA":
                self.stats[constants.MAXCHAKRA_STATKEY] += bonus
            elif stat == "MAXHP":
                self.stats[constants.MAXHP_STATKEY] += bonus
        self._clan_bonuses_applied = True

    def set_ninja_identity(self, clan: str, element: str) -> bool:
        """
        Sets the player's clan and elemental affinity after Academy registration.
        """
        if clan not in constants.CLANS or element not in constants.ELEMENTS:
            return False
        if clan == "Nenhum" and element == "Nenhum":
            return False
        self.clan = clan
        self.element = element
        self.apply_clan_bonuses()
        self.assign_skills_based_on_identity()
        messager.add_message(self.name, f"Você se registrou como ninja do clã {clan} com afinidade {element}!")
        return True

    def assign_skills_based_on_identity(self) -> None:
        """
        Assigns starting jutsus based on clan and element.
        Future: load skill lists from data/clans.json and element skill files.
        """
        self.skills = ["First Aid"]
        if self.element != "Nenhum":
            element_skills = data_management.search_skills_by_element(self.element)
            for skill_name in element_skills[:2]:
                if skill_name not in self.skills:
                    self.skills.append(skill_name)
        if self.clan != "Nenhum":
            clan_skills = data_management.search_skills_by_clan(self.clan)
            for skill_name in clan_skills[:1]:
                if skill_name not in self.skills:
                    self.skills.append(skill_name)

    def add_exp(self, exp: int) -> bool:
        """Adds XP and handles level-up."""
        exp *= self.xp_rate
        self.xp += exp
        leveled_up = False

        while self.xp >= self.xp_to_next_lvl:
            self.xp -= self.xp_to_next_lvl
            self.lvl += 1
            leveled_up = True
            self.xp_to_next_lvl = formulas.xp_next_lvl_formula(self.xp_to_next_lvl, self.lvl)
            for stat in self.stats:
                if stat not in constants.STATS_NOT_UPGRADING_WHEN_LEVELING_UP:
                    self.stats[stat] += constants.STAT_UPGRADE_WHEN_LEVELING_UP
            if constants.FULLY_RECOVER_WHEN_LEVELING_UP:
                self.recover()
            messager.add_message(self.name, f"You leveled up! You are now level {self.lvl}")
            self.check_rank_promotion()
        return leveled_up

    def add_ryo(self, amount: int) -> None:
        self.ryo += amount

    def spend_stamina(self, amount: int) -> bool:
        if self.stamina < amount:
            return False
        self.stamina -= amount
        self.stats[constants.STAMINA_STATKEY] = self.stamina
        return True

    def complete_mission(self, mission_rank: str) -> None:
        if mission_rank not in self.missions_completed:
            self.missions_completed[mission_rank] = 0
        self.missions_completed[mission_rank] += 1
        self.check_rank_promotion()

    def check_rank_promotion(self) -> bool:
        """
        Checks and applies ninja rank promotion based on level and missions.
        """
        promoted = False
        current_idx = constants.RANK_INDEX.get(self.ninja_rank, 0)

        for rank_name, requirements in constants.RANK_PROMOTION_REQUIREMENTS.items():
            target_idx = constants.RANK_INDEX.get(rank_name, 0)
            if target_idx <= current_idx:
                continue
            if self.lvl < requirements.get("min_level", 0):
                continue
            mission_reqs = requirements.get("missions", {})
            meets_missions = all(
                self.missions_completed.get(rank, 0) >= count
                for rank, count in mission_reqs.items()
            )
            if not meets_missions:
                continue

            self.ninja_rank = rank_name
            current_idx = target_idx
            promoted = True
            self.ninjutsu_mult += 0.05
            self.taijutsu_mult += 0.05
            self.stats[constants.MAXCHAKRA_STATKEY] += 5
            self.stats[constants.MAXSTAMINA_STATKEY] += 10
            messager.add_message(
                self.name,
                f"Promoção! Você agora é {rank_name}! Seus multiplicadores passivos aumentaram.",
            )
        return promoted

    def show_player_info(self) -> str:
        stat_string = ''.join([f'**{stat}**: {self.stats[stat]}\n' for stat in constants.STATKEYS])
        player_xp_bar = progressBar.filledBar(int(self.xp_to_next_lvl), int(self.xp), size=10)[0]
        return (
            f'**Nome**: {self.name.capitalize()}\n'
            f'**Nível**: {self.lvl}\n'
            f'**Rank Ninja**: {self.ninja_rank}\n'
            f'**Clã**: {self.clan} {emojis.clan_to_emoji.get(self.clan, "")}\n'
            f'**Afinidade**: {self.element} {emojis.element_to_emoji.get(self.element, "")}\n'
            f'**XP**: {int(self.xp)}/{self.xp_to_next_lvl} {player_xp_bar}\n'
        )

    def show_player_stats(self) -> str:
        player_hp_bar = progressBar.filledBar(
            int(self.stats[constants.MAXHP_STATKEY]),
            int(self.stats[constants.HP_STATKEY]), size=10,
        )[0]
        player_chakra_bar = progressBar.filledBar(
            int(self.stats[constants.MAXCHAKRA_STATKEY]),
            int(self.stats[constants.CHAKRA_STATKEY]), size=10,
        )[0]
        player_stamina_bar = progressBar.filledBar(
            int(self.stats[constants.MAXSTAMINA_STATKEY]),
            int(self.stats[constants.STAMINA_STATKEY]), size=10,
        )[0]
        return (
            f'{emojis.HP_EMOJI} **HP**: {self.stats[constants.HP_STATKEY]}/'
            f'{self.stats[constants.MAXHP_STATKEY]} {player_hp_bar}\n'
            f'{emojis.CHAKRA_EMOJI} **Chakra**: {self.stats[constants.CHAKRA_STATKEY]}/'
            f'{self.stats[constants.MAXCHAKRA_STATKEY]} {player_chakra_bar}\n'
            f'{emojis.STAMINA_EMOJI} **Stamina**: {self.stats[constants.STAMINA_STATKEY]}/'
            f'{self.stats[constants.MAXSTAMINA_STATKEY]} {player_stamina_bar}\n\n'
            + ''.join([f'**{stat}**: {self.stats[stat]}\n' for stat in constants.STATKEYS_NO_RESOURCES])
        )

    def show_ninja_profile(self) -> str:
        return (
            f'**Rank Ninja**: {self.ninja_rank}\n'
            f'**Clã**: {self.clan} {emojis.clan_to_emoji.get(self.clan, "")}\n'
            f'**Afinidade**: {self.element} {emojis.element_to_emoji.get(self.element, "")}\n'
            f'**Saldo**: {self.ryo} {emojis.RYO_EMOJI}\n'
        )

    def show_current_skills_as_list(self) -> str:
        skill_str = "**Jutsus**\n"
        for skill in self.skills:
            skill_inst = data_management.search_cache_skill_by_name(skill)
            if skill_inst is not None:
                skill_str += (
                    f"- {skill} {emojis.skill_emoji(skill_inst, self.clan)} "
                    f"[{skill_inst.skill_type}]\n"
                )
        return skill_str

    def equip_item(self, equipment: str) -> (bool, list):
        e = self.inventory.item_exists(equipment)
        if e is not None:
            if e.object_type != "EQUIPMENT":
                return False, [error_msgs.ERROR_CANNOT_EQUIP_THAT_ITEM]
            self.inventory.remove_item(equipment, 1)
            if self.equipment[e.translate_equipment_type()] is not None:
                self.unequip_item(self.equipment[e.translate_equipment_type()])
            self.equipment.update({e.translate_equipment_type(): e.name})

            for stat in e.stat_change_list:
                self.stats[stat] += e.stat_change_list[stat]
            if hasattr(e, 'ninjutsu_mult'):
                self.ninjutsu_mult += e.ninjutsu_mult - 1.0
            if hasattr(e, 'taijutsu_mult'):
                self.taijutsu_mult += e.taijutsu_mult - 1.0
            if hasattr(e, 'chakra_reduction'):
                self.chakra_reduction += e.chakra_reduction
            messager.add_message(self.name, f'You have equipped your {equipment}.')
            return True, [f'You have successfully equipped your {equipment}.']
        return False, [error_msgs.ERROR_CHARACTER_DOES_NOT_HAVE_THAT_ITEM]

    def unequip_item(self, equipment) -> None:
        self.inventory.add_item(equipment, 1)
        equipment = data_management.search_cache_item_by_name(equipment)
        for stat in equipment.stat_change_list:
            self.stats[stat] -= equipment.stat_change_list[stat]
        if hasattr(equipment, 'ninjutsu_mult'):
            self.ninjutsu_mult -= equipment.ninjutsu_mult - 1.0
        if hasattr(equipment, 'taijutsu_mult'):
            self.taijutsu_mult -= equipment.taijutsu_mult - 1.0
        if hasattr(equipment, 'chakra_reduction'):
            self.chakra_reduction -= equipment.chakra_reduction

    def die(self) -> None:
        messager.add_message(
            self.name,
            "You have died. You are brought back to safety, but half your ryo is gone...",
        )
        self._in_fight = False
        self._in_dungeon = False
        data_management.delete_cache_dungeon_inst(self.name)
        self.ryo = formulas.ryo_lost_when_dying(self.ryo)

    def respawn(self) -> None:
        if not self.alive:
            self.alive = True
            self.recover()

    def recover(self) -> None:
        super().fully_heal()
        super().fully_recover_chakra()
        super().fully_recover_stamina()
        self.chakra = self.stats[constants.CHAKRA_STATKEY]
        self.stamina = self.stats[constants.STAMINA_STATKEY]

    @property
    def lvl(self) -> int:
        return self._lvl

    @lvl.setter
    def lvl(self, value: int) -> None:
        if value < 0:
            raise ValueError("Player's level cannot be set to a value below 0.")
        self._lvl = value

    @property
    def xp(self) -> int:
        return self._xp

    @xp.setter
    def xp(self, value: int) -> None:
        if value < 0:
            raise ValueError("Player's XP cannot be set to a value below 0.")
        self._xp = value

    @property
    def xp_to_next_lvl(self) -> int:
        return self._xp_to_next_lvl

    @xp_to_next_lvl.setter
    def xp_to_next_lvl(self, value: int) -> None:
        if value < 0:
            raise ValueError("Player's XP to next level cannot be set to a value below 0.")
        self._xp_to_next_lvl = value

    @property
    def xp_rate(self) -> float:
        return self._xp_rate

    @xp_rate.setter
    def xp_rate(self, value: float) -> None:
        if value < 0:
            raise ValueError("Player's XP rate cannot be set to a value below 0.")
        self._xp_rate = value

    @property
    def ryo(self) -> int:
        return self._ryo

    @ryo.setter
    def ryo(self, value: int) -> None:
        if value < 0:
            raise ValueError("Player's ryo cannot be set to a value below 0.")
        self._ryo = value

    @property
    def equipment(self) -> dict:
        return self._equipment

    @equipment.setter
    def equipment(self, value: dict) -> None:
        self._equipment = value

    @property
    def skills(self) -> list:
        return self._skills

    @skills.setter
    def skills(self, value: list) -> None:
        self._skills = value

    @property
    def passives(self) -> list:
        return self._passives

    @passives.setter
    def passives(self, value: list) -> None:
        self._passives = value

    @property
    def current_area(self) -> int:
        return self._current_area

    @current_area.setter
    def current_area(self, value: int) -> None:
        self._current_area = value

    @property
    def in_fight(self) -> bool:
        return self._in_fight

    @in_fight.setter
    def in_fight(self, value: bool) -> None:
        self._in_fight = value

    @property
    def in_dungeon(self) -> bool:
        return self._in_dungeon

    @in_dungeon.setter
    def in_dungeon(self, value: bool) -> None:
        self._in_dungeon = value

    @property
    def defeated_bosses(self) -> list:
        return self._defeated_bosses

    @defeated_bosses.setter
    def defeated_bosses(self, value: list) -> None:
        self._defeated_bosses = value

    @property
    def clan(self) -> str:
        return self._clan

    @clan.setter
    def clan(self, value: str) -> None:
        self._clan = value

    @property
    def element(self) -> str:
        return self._element

    @element.setter
    def element(self, value: str) -> None:
        self._element = value

    @property
    def ninja_rank(self) -> str:
        return self._ninja_rank

    @ninja_rank.setter
    def ninja_rank(self, value: str) -> None:
        self._ninja_rank = value
