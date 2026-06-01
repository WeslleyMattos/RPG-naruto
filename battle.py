import random
import constants
import data_management
import emojis
import formulas
import messager

from battler import Battler
from player import Player
from enemy import Enemy
from skill import Skill


class Battle:

    def __init__(self, player: Player, enemy: Battler):
        print(f"Initializing battle with Player: {player.name} and Enemy: {enemy.name}")

        self.player = player
        self.enemy = enemy
        self.is_over = False
        self.skills_in_cooldown = self.player.dungeon_cooldowns
        self.enemy_skills_in_cooldown = {}
        self.player_stats_before_battle = self.player.stats.copy()

    def turn(self, player_action: dict) -> list:
        no_enemy_turn = False

        if self.player.is_paralyzed():
            messager.add_message(self.player.name, f"{self.player.name} está paralisado e perde o turno!")
        elif self.player.is_confused() and random.randint(0, 1) == 0:
            messager.add_message(self.player.name, f"{self.player.name} está confuso e erra a ação!")
        elif player_action["ACTION"] == constants.NORMAL_ATTACK_OPTION:
            stamina_cost = 5
            if self.player.stats[constants.STAMINA_STATKEY] >= stamina_cost:
                self.player.stats[constants.STAMINA_STATKEY] -= stamina_cost
                normal_attack(attacker=self.player, target=self.enemy, player_name=self.player.name)
            else:
                messager.add_message(self.player.name, f"{self.player.name} não tem Stamina suficiente para atacar!")
        elif player_action["ACTION"] == constants.SKILL_OPTION:
            skill = data_management.search_cache_skill_by_name(player_action["SKILL"])
            if skill is None:
                messager.add_message(self.player.name, "Jutsu não encontrado!")
            elif not self._can_afford_skill(self.player, skill):
                messager.add_message(
                    self.player.name,
                    f"{self.player.name} não tem Chakra ou Stamina suficiente para {skill.name}!",
                )
            else:
                target = self.skill_based_target_selection(skill, self.player)
                perform_skill(self.player, target, skill, self.player.name)
                self.skills_in_cooldown.update({skill.name: skill.cooldown})
                if constants.SKILL_TAG_DOES_NOT_SKIP_TURN in skill.tags:
                    no_enemy_turn = True

        self.enemy_turn(no_enemy_turn)
        self.decrease_cooldowns()
        self.decrease_buff_debuff_duration()
        return messager.empty_queue(self.player.name)

    def _can_afford_skill(self, battler: Battler, skill: Skill) -> bool:
        chakra_reduction = getattr(battler, 'chakra_reduction', 0.0)
        chakra_cost = skill.chakra_cost
        if skill.percentage_cost:
            import math
            chakra_cost = int(math.ceil(battler.stats[constants.MAXCHAKRA_STATKEY] * chakra_cost / 100))
        else:
            chakra_cost = formulas.apply_chakra_reduction(chakra_cost, chakra_reduction)
        return (
            battler.stats[constants.CHAKRA_STATKEY] >= chakra_cost
            and battler.stats[constants.STAMINA_STATKEY] >= skill.stamina_cost
        )

    def enemy_turn(self, no_enemy_turn: bool) -> None:
        if self.enemy.alive:
            if not no_enemy_turn:
                if self.enemy.is_paralyzed():
                    messager.add_message(self.player.name, f"{self.enemy.name} está paralisado!")
                    return

                enemy_action = random.choices(constants.POSSIBLE_ENEMY_ACTIONS, weights=constants.ENEMY_AI_WEIGHTS)[0]
                possible_enemy_skills = [
                    s for s in self.enemy.skills if s not in self.enemy_skills_in_cooldown
                ]

                if enemy_action == constants.SKILL_OPTION and len(possible_enemy_skills) > 0:
                    skill = data_management.search_cache_skill_by_name(random.choice(possible_enemy_skills))
                    if skill and self._can_afford_skill(self.enemy, skill):
                        target = self.skill_based_target_selection(skill, self.enemy)
                        perform_skill(self.enemy, target, skill, self.player.name)
                        self.enemy_skills_in_cooldown.update({skill.name: skill.cooldown})
                    else:
                        normal_attack(attacker=self.enemy, target=self.player, player_name=self.player.name)
                else:
                    normal_attack(attacker=self.enemy, target=self.player, player_name=self.player.name)

                if not self.player.alive:
                    self.is_over = True
        else:
            messager.add_message(self.player.name, f"{self.enemy.name} foi derrotado.")
            self.is_over = True

    def win_battle(self) -> str:
        data_management.delete_cache_battle_by_player(self.player.name)

        messager.add_message(
            self.player.name,
            f"{self.player.name} venceu! +{self.enemy.xp_reward} XP e +{self.enemy.ryo_reward} Ryo",
        )

        self.actions_when_battle_is_over()
        self.player.add_exp(self.enemy.xp_reward)
        self.player.add_ryo(self.enemy.ryo_reward)
        self.player.shield = 0

        loot = self.enemy.loot()
        if loot:
            self.player.inventory.add_item(loot, 1)
        else:
            messager.add_message(self.player.name, "Nenhum item encontrado no corpo do inimigo.")

        key_loot = self.enemy.key_item_loot()
        if key_loot:
            self.player.inventory.add_item(key_loot, 1)
            messager.add_message(self.player.name, f"Item raro encontrado: {key_loot}!")

        if self.enemy.is_boss and self.enemy.name not in self.player.defeated_bosses:
            self.player.defeated_bosses.append(self.enemy.name)

        if self.player.in_dungeon:
            self.decrease_cooldowns()
            self.player.dungeon_cooldowns = self.skills_in_cooldown
            dungeon_inst = data_management.search_cache_dungeon_inst_by_player(self.player.name)
            dungeon_inst.current_enemies_defeated += 1
            if dungeon_inst.enemy_count < dungeon_inst.current_enemies_defeated:
                dungeon_inst.boss_defeated = True
                self.player.dungeon_cooldowns = {}
                self.player.recover()
                if dungeon_inst.ryo_reward:
                    self.player.add_ryo(dungeon_inst.ryo_reward)
                    messager.add_message(self.player.name, f"Bônus de dungeon: +{dungeon_inst.ryo_reward} Ryo!")
        else:
            self.player.dungeon_cooldowns = {}
            self.player.recover()

        data_management.update_player_info(self.player.name)
        del self.enemy
        return loot or key_loot

    def lose_battle(self) -> None:
        data_management.delete_cache_battle_by_player(self.player.name)
        self.actions_when_battle_is_over()
        self.player.dungeon_cooldowns = {}
        del self.enemy
        self.player.respawn()
        data_management.update_player_info(self.player.name)

    def decrease_buff_debuff_duration(self) -> None:
        self.decrease_buff_debuff_duration_battler(self.player)
        self.decrease_buff_debuff_duration_battler(self.enemy)

    def decrease_buff_debuff_duration_battler(self, battler: Battler) -> None:
        for bd in list(battler.buffs_and_debuffs):
            if battler.buffs_and_debuffs[bd] == 0:
                remove_buff_debuff(battler, bd)
                messager.add_message(
                    self.player.name,
                    f"{battler.name} {emojis.buff_debuff_to_emoji.get(bd, '')} expirou.",
                )
            else:
                battler.buffs_and_debuffs[bd] -= 1

    def remove_all_buffs_and_debuffs(self) -> None:
        for bd in self.player.buffs_and_debuffs:
            self.player.stat_change_on_buff_debuff(bd, expires=True)
        for bd in self.enemy.buffs_and_debuffs:
            self.enemy.stat_change_on_buff_debuff(bd, expires=True)
        self.player.buffs_and_debuffs = {}
        self.enemy.buffs_and_debuffs = {}

    def actions_when_battle_is_over(self) -> None:
        self.remove_all_buffs_and_debuffs()
        self.player.stats.update({
            key: self.player_stats_before_battle[key]
            for key in self.player_stats_before_battle
            if key not in constants.STATS_NOT_COPYING_AFTER_BATTLE
        })
        self.player.chakra = self.player.stats[constants.CHAKRA_STATKEY]
        self.player.stamina = self.player.stats[constants.STAMINA_STATKEY]

    def skill_based_target_selection(self, skill: Skill, caster: Battler) -> Battler:
        if constants.SKILL_TAG_HEALING not in skill.tags:
            if type(caster) == Player:
                return self.enemy
            return self.player
        if type(caster) == Player:
            return self.player
        return self.enemy

    def decrease_cooldowns(self) -> None:
        for skill in list(self.skills_in_cooldown):
            if self.skills_in_cooldown[skill] == 0:
                self.skills_in_cooldown.pop(skill)
            else:
                self.skills_in_cooldown[skill] -= 1
        for skill in list(self.enemy_skills_in_cooldown):
            if self.enemy_skills_in_cooldown[skill] == 0:
                self.enemy_skills_in_cooldown.pop(skill)
            else:
                self.enemy_skills_in_cooldown[skill] -= 1

    @property
    def player(self) -> Player:
        return self._player

    @player.setter
    def player(self, value: Player) -> None:
        if value:
            self._player = value
        else:
            raise ValueError("Player cannot be None.")

    @property
    def enemy(self) -> Enemy:
        return self._enemy

    @enemy.setter
    def enemy(self, value: Enemy) -> None:
        if value:
            self._enemy = value
        else:
            raise ValueError("Enemy cannot be None.")

    @property
    def is_over(self) -> bool:
        return self._is_over

    @is_over.setter
    def is_over(self, value: bool) -> None:
        self._is_over = value

    @property
    def skills_in_cooldown(self) -> dict:
        return self._skills_in_cooldown

    @skills_in_cooldown.setter
    def skills_in_cooldown(self, value: dict) -> None:
        self._skills_in_cooldown = value

    @property
    def enemy_skills_in_cooldown(self) -> dict:
        return self._enemy_skills_in_cooldown

    @enemy_skills_in_cooldown.setter
    def enemy_skills_in_cooldown(self, value: dict) -> None:
        self._enemy_skills_in_cooldown = value

    @property
    def player_stats_before_battle(self) -> dict:
        return self._player_stats_before_battle

    @player_stats_before_battle.setter
    def player_stats_before_battle(self, value: dict) -> None:
        self._player_stats_before_battle = value

    @enemy.deleter
    def enemy(self):
        del self._enemy


def remove_buff_debuff(target: Battler, bd: str) -> None:
    target.buffs_and_debuffs.pop(bd)
    target.stat_change_on_buff_debuff(bd, expires=True)


def start_battle(player: Player, enemy: Enemy) -> Battle:
    messager.add_message(player.name, f'Você está lutando contra **{enemy.name}**')
    return Battle(player, enemy)


def normal_attack(attacker: Battler, target: Battler, player_name: str) -> None:
    if not check_miss(attacker.stats[constants.SPEED_STATKEY], target.stats[constants.SPEED_STATKEY]):
        dmg = formulas.normal_attack_dmg(attacker.stats[constants.ATK_STATKEY], target.stats[constants.DEF_STATKEY])

        if type(attacker) == Player:
            taijutsu_mult = getattr(attacker, 'taijutsu_mult', 1.0)
            dmg = int(dmg * taijutsu_mult)
            if attacker.equipment.get("WEAPON") is not None:
                dmg = int(dmg * constants.NINJUTSU_DAMAGE_BONUS)

        dmg, is_crit = formulas.check_for_critical_damage(attacker, dmg)
        if is_crit:
            messager.add_message(player_name, f"Crítico! {attacker.name} ataca {target.name} causando {dmg} de dano!")
        else:
            messager.add_message(player_name, f"{attacker.name} ataca {target.name} causando {dmg} de dano!")
        target.take_damage(dmg, None)
    else:
        messager.add_message(player_name, f"{attacker.name} errou o ataque!")


def perform_skill(attacker: Battler, target: Battler, skill: Skill, player_name: str) -> None:
    chakra_reduction = getattr(attacker, 'chakra_reduction', 0.0) if type(attacker) == Player else 0.0
    if attacker.pay_costs(skill, chakra_reduction):
        skill.effect(player_name, attacker, target)
    else:
        messager.add_message(
            player_name,
            f"{attacker.name} não tem Chakra ou Stamina suficiente para {skill.name}!",
        )


def check_miss(atk_speed: int, def_speed: int) -> bool:
    chance = formulas.miss_formula(atk_speed, def_speed)
    return chance > random.randint(0, 100)
