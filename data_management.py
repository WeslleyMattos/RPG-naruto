import copy
import json
import os
import area
import battle
import blessing
import constants
import dungeon
import enemy
import equipment
import item
import messager
import mission
import peewee_models
import player
import shop
import skill
import inventory
import peewee


escordia_db = peewee.SqliteDatabase('escordia_db')
escordia_db.connect()

ITEM_CACHE = {}
EQUIPMENT_CACHE = {}
AREAS_CACHE = {}
DUNGEON_CACHE = {}
CURRENT_DUNGEONS_CACHE = {}
PLAYER_CACHE = {}
ENEMIES_CACHE = {}
BATTLE_CACHE = {}
SHOP_CACHE = {}
SKILLS_CACHE = {}
SKILLS_BY_ELEMENT = {}
SKILLS_BY_CLAN = {}
BLESSINGS_CACHE = {}
MISSION_CACHE = {}


def create_new_player(player_name: str) -> None:
    player_inst = player.Player(
        player_name,
        inventory=inventory.Inventory(player_name),
        equipment=constants.INITIAL_EQUIPMENT.copy(),
    )
    PLAYER_CACHE.update({player_name: player_inst})
    peewee_models.PlayerModel.create(
        name=player_name, stats=str(player_inst.stats), lvl=player_inst.lvl,
        xp=player_inst.xp, xp_to_next_lvl=player_inst.xp_to_next_lvl,
        xp_rate=player_inst.xp_rate, ryo=player_inst.ryo, essence=player_inst.essence,
        chakra=player_inst.chakra, stamina=player_inst.stamina,
        clan=player_inst.clan, element=player_inst.element,
        ninja_rank=player_inst.ninja_rank,
        inventory=str(player_inst.inventory.items), equipment=str(player_inst.equipment),
        skills=str(player_inst.skills), passives=str(player_inst.passives),
        current_area=player_inst.current_area, in_fight=player_inst.in_fight,
        in_dungeon=player_inst.in_dungeon, defeated_bosses=str(player_inst.defeated_bosses),
        blessings=str(player_inst.blessings),
        missions_completed=str(player_inst.missions_completed),
        active_mission=player_inst.active_mission,
        mission_end_time=player_inst.mission_end_time,
    )
    messager.messager_add_player(player_name)


def create_new_battle(player_inst: player.Player, enemy_inst: enemy.Enemy) -> None:
    BATTLE_CACHE.update({player_inst.name: battle.Battle(player_inst, enemy_inst)})
    print(f"Created battle with player: {player_inst.name} and enemy: {enemy_inst.name}")


def create_new_dungeon_inst(player_inst: player.Player, dungeon_inst: dungeon.Dungeon) -> None:
    CURRENT_DUNGEONS_CACHE.update({player_inst.name: copy.deepcopy(dungeon_inst)})


def create_escordia_tables() -> None:
    try:
        escordia_db.create_tables([peewee_models.PlayerModel])
    except peewee.OperationalError:
        print("Peewee error on creating/accessing tables.")


def update_player_info(player_name: str) -> None:
    player_inst = PLAYER_CACHE[player_name]
    player_inst.chakra = player_inst.stats[constants.CHAKRA_STATKEY]
    player_inst.stamina = player_inst.stats[constants.STAMINA_STATKEY]
    peewee_models.PlayerModel.update(
        stats=str(player_inst.stats), lvl=player_inst.lvl, xp=player_inst.xp,
        xp_to_next_lvl=player_inst.xp_to_next_lvl, xp_rate=player_inst.xp_rate,
        ryo=player_inst.ryo, essence=player_inst.essence,
        chakra=player_inst.chakra, stamina=player_inst.stamina,
        clan=player_inst.clan, element=player_inst.element,
        ninja_rank=player_inst.ninja_rank,
        inventory=str(player_inst.inventory.items), equipment=str(player_inst.equipment),
        skills=str(player_inst.skills), passives=str(player_inst.passives),
        current_area=player_inst.current_area, in_fight=player_inst.in_fight,
        in_dungeon=player_inst.in_dungeon, defeated_bosses=str(player_inst.defeated_bosses),
        blessings=str(player_inst.blessings),
        missions_completed=str(player_inst.missions_completed),
        active_mission=player_inst.active_mission,
        mission_end_time=player_inst.mission_end_time,
    ).where(peewee_models.PlayerModel.name == player_name).execute()
    print(f"Updated player: {player_name} info in database.")


def search_cache_player(player_name: str) -> player.Player:
    try:
        return PLAYER_CACHE[player_name]
    except KeyError:
        return None


def search_cache_battle_by_player(player_name: str) -> battle.Battle:
    try:
        return BATTLE_CACHE[player_name]
    except KeyError:
        return None


def search_cache_enemy_by_name(enemy_name: str) -> enemy.Enemy:
    try:
        return ENEMIES_CACHE[enemy_name]
    except KeyError:
        return None


def search_cache_dungeon_inst_by_player(player_name: str) -> dungeon.Dungeon:
    try:
        return CURRENT_DUNGEONS_CACHE[player_name]
    except KeyError:
        return None


def search_cache_dungeon_by_name(dungeon_name: str) -> dungeon.Dungeon:
    try:
        return DUNGEON_CACHE[dungeon_name]
    except KeyError:
        return None


def search_cache_area_by_number(number: int) -> area.Area:
    try:
        return AREAS_CACHE[number]
    except KeyError:
        return None


def search_cache_area_by_name(name: str) -> area.Area:
    try:
        for i in AREAS_CACHE.keys():
            if AREAS_CACHE[i].name == name:
                return AREAS_CACHE[i]
        return None
    except KeyError:
        return None


def search_cache_item_by_name(item_name: str) -> item.Item:
    try:
        return EQUIPMENT_CACHE[item_name]
    except KeyError:
        try:
            return ITEM_CACHE[item_name]
        except KeyError:
            return None


def search_cache_shop_by_area(area_index: int) -> shop.Shop:
    try:
        return SHOP_CACHE[area_index]
    except KeyError:
        return None


def search_cache_skill_by_name(skill_name: str) -> skill.Skill:
    try:
        return SKILLS_CACHE[skill_name]
    except KeyError:
        return None


def search_skills_by_element(element: str) -> list:
    return SKILLS_BY_ELEMENT.get(element, [])


def search_skills_by_clan(clan: str) -> list:
    return SKILLS_BY_CLAN.get(clan, [])


def search_cache_mission_by_name(mission_name: str) -> mission.Mission:
    try:
        return MISSION_CACHE[mission_name]
    except KeyError:
        return None


def search_available_missions_for_player(player_inst: player.Player) -> list:
    available = []
    for m in MISSION_CACHE.values():
        if m.player_can_accept(player_inst):
            available.append(m)
    return available


def search_cache_blessing(blessing_name: str) -> blessing.Blessing:
    try:
        return BLESSINGS_CACHE[blessing_name]
    except KeyError:
        return None


def delete_cache_battle_by_player(player_name: str) -> None:
    b = search_cache_battle_by_player(player_name)
    if b is not None:
        BATTLE_CACHE.pop(player_name)


def delete_cache_dungeon_inst(player_name: str) -> None:
    d = search_cache_dungeon_inst_by_player(player_name)
    if d is not None:
        CURRENT_DUNGEONS_CACHE.pop(player_name)


def _migrate_stats(old_stats: dict) -> dict:
    """Migrates legacy MP/MATK stats to Chakra/Ninjutsu."""
    stats = constants.INITIAL_STATS.copy()
    if not old_stats:
        return stats
    migrated = dict(old_stats)
    if 'MP' in migrated:
        migrated[constants.CHAKRA_STATKEY] = migrated.pop('MP')
    if 'MAXMP' in migrated:
        migrated[constants.MAXCHAKRA_STATKEY] = migrated.pop('MAXMP')
    if 'MATK' in migrated:
        migrated[constants.NINJUTSU_STATKEY] = migrated.pop('MATK')
    for key in [constants.MAXSTAMINA_STATKEY, constants.STAMINA_STATKEY]:
        if key not in migrated:
            migrated[key] = constants.INITIAL_STATS[key]
    stats.update(migrated)
    return stats


def load_items_from_json() -> None:
    with open("data/items.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)
        for i in json_file:
            param_list = [i[key] for key in constants.ITEM_KEYS]
            ITEM_CACHE.update({i["NAME"]: item.Item(*param_list)})


def load_equipment_from_json() -> None:
    if not os.path.isdir(constants.EQUIPMENT_PATH):
        return
    for file in os.listdir(constants.EQUIPMENT_PATH):
        if not file.endswith('.json'):
            continue
        with open(constants.EQUIPMENT_PATH + file, 'r', encoding='utf-8') as f:
            json_file = json.load(f)
            for e in json_file:
                e = dict(e)
                e.setdefault("NINJUTSU_MULT", 1.0)
                e.setdefault("TAIJUTSU_MULT", 1.0)
                e.setdefault("CHAKRA_REDUCTION", 0.0)
                e.setdefault("STAT_CHANGE_LIST", {})
                param_list = [e[key] for key in constants.EQUIPMENT_KEYS]
                EQUIPMENT_CACHE.update({e["NAME"]: equipment.Equipment(*param_list)})


def _equipment_default(key: str):
    defaults = {
        "NINJUTSU_MULT": 1.0, "TAIJUTSU_MULT": 1.0, "CHAKRA_REDUCTION": 0.0,
    }
    return defaults.get(key, {} if key == "STAT_CHANGE_LIST" else None)


def load_enemies_from_json() -> None:
    if not os.path.isdir(constants.ENEMIES_PATH):
        return
    for file in os.listdir(constants.ENEMIES_PATH):
        if file in ("area1_enemies.json", "area2_enemies.json"):
            continue
        if not file.endswith('.json'):
            continue
        with open(constants.ENEMIES_PATH + file, 'r', encoding='utf-8') as f:
            json_file = json.load(f)
            for e in json_file:
                e = dict(e)
                if "RYO_REWARD" not in e and "GOLD_REWARD" in e:
                    e["RYO_REWARD"] = e.pop("GOLD_REWARD")
                e.setdefault("ELEMENT", "Nenhum")
                e["STATS"] = _migrate_stats(e.get("STATS", {}))
                param_list = [e[key] for key in constants.ENEMY_KEYS]
                ENEMIES_CACHE.update({e["NAME"]: enemy.Enemy(*param_list)})


def load_areas_from_json() -> None:
    with open("data/areas.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)
        for a in json_file:
            a = dict(a)
            a.setdefault("MIN_RANK", "Estudante da Academia")
            param_list = [a[key] for key in constants.AREAS_KEYS]
            AREAS_CACHE.update({a["NUMBER"]: area.Area(*param_list)})


def load_dungeons_from_json() -> None:
    with open("data/dungeons.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)
        for d in json_file:
            d = dict(d)
            d.setdefault("MIN_RANK", "Genin")
            d.setdefault("RYO_REWARD", 100)
            param_list = [d[key] for key in constants.DUNGEON_KEYS]
            DUNGEON_CACHE.update({d["DUNGEON_NAME"]: dungeon.Dungeon(*param_list)})


def load_shops_from_json() -> None:
    with open("data/shops.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)
        for s in json_file:
            param_list = [s[key] for key in constants.SHOP_KEYS]
            SHOP_CACHE.update({s["AREA_NUMBER"]: shop.Shop(*param_list)})


def load_skills_from_json() -> None:
    if not os.path.isdir(constants.SKILLS_PATH):
        return
    for file in os.listdir(constants.SKILLS_PATH):
        if file in constants.LEGACY_SKILL_FILES:
            continue
        if not file.endswith('.json'):
            continue
        with open(constants.SKILLS_PATH + file, 'r', encoding='utf-8') as f:
            json_file = json.load(f)
            for s in json_file:
                s = dict(s)
                if "CHAKRA_COST" not in s and "MP_COST" in s:
                    s["CHAKRA_COST"] = s.pop("MP_COST")
                s.setdefault("STAMINA_COST", 0)
                s.setdefault("SKILL_TYPE", constants.SKILL_TYPE_NINJUTSU)
                s.setdefault("ELEMENT", "Nenhum")
                skill_inst = skill.Skill(
                    name=s["NAME"],
                    description=s["DESCRIPTION"],
                    chakra_cost=s.get("CHAKRA_COST", 0),
                    stamina_cost=s.get("STAMINA_COST", 0),
                    power=s.get("POWER", 0),
                    element=s.get("ELEMENT", "Nenhum"),
                    cooldown=s.get("COOLDOWN", 1),
                    tags=s.get("TAGS", []),
                    percentage_cost=s.get("PERCENTAGE_COST", False),
                    skill_type=s.get("SKILL_TYPE", constants.SKILL_TYPE_NINJUTSU),
                )
                SKILLS_CACHE.update({s["NAME"]: skill_inst})
                _index_skill_by_file(file, skill_inst)


def _skill_default(key: str):
    defaults = {
        "COOLDOWN": 1, "TAGS": [], "PERCENTAGE_COST": False,
        "STAMINA_COST": 0, "ELEMENT": "Nenhum",
        "SKILL_TYPE": constants.SKILL_TYPE_NINJUTSU,
    }
    return defaults.get(key)


def _index_skill_by_file(filename: str, skill_inst: skill.Skill) -> None:
    base = filename.replace('.json', '').lower()
    for element in constants.ELEMENTS:
        if element.lower() == base:
            SKILLS_BY_ELEMENT.setdefault(element, []).append(skill_inst.name)
            return
    if base.startswith('tai_'):
        clan_key = base.replace('tai_', '')
        for clan in constants.CLANS:
            if clan.lower() == clan_key:
                SKILLS_BY_CLAN.setdefault(clan, []).append(skill_inst.name)
                return


def load_missions_from_json() -> None:
    path = "data/missions.json"
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        json_file = json.load(f)
        for m in json_file:
            param_list = [m[key] for key in constants.MISSION_KEYS]
            MISSION_CACHE.update({m["NAME"]: mission.Mission(*param_list)})


def load_blessings_from_json() -> None:
    with open("data/blessings.json", 'r', encoding='utf-8') as f:
        json_file = json.load(f)
        for b in json_file:
            param_list = [b[key] for key in constants.BLESSING_KEYS]
            BLESSINGS_CACHE.update({b["NAME"]: blessing.Blessing(*param_list)})


def load_players_from_db() -> None:
    for player_model in peewee_models.PlayerModel.select():
        print(f"Loading player {player_model.name} into cache...")
        stats = _migrate_stats(eval(player_model.stats))
        missions_completed = eval(getattr(player_model, 'missions_completed', '{}'))
        if not missions_completed:
            missions_completed = {rank: 0 for rank in constants.MISSION_RANKS}

        player_inst = player.Player(
            player_model.name, stats=stats, lvl=player_model.lvl, xp=player_model.xp,
            xp_to_next_lvl=player_model.xp_to_next_lvl, xp_rate=player_model.xp_rate,
            ryo=getattr(player_model, 'ryo', getattr(player_model, 'money', 50)),
            essence=player_model.essence,
            chakra=getattr(player_model, 'chakra', stats.get(constants.CHAKRA_STATKEY, 10)),
            stamina=getattr(player_model, 'stamina', stats.get(constants.STAMINA_STATKEY, 100)),
            clan=getattr(player_model, 'clan', 'Nenhum'),
            element=getattr(player_model, 'element', 'Nenhum'),
            ninja_rank=getattr(player_model, 'ninja_rank', 'Estudante da Academia'),
            inventory=inventory.Inventory(player_model.name, items=eval(player_model.inventory)),
            equipment=eval(player_model.equipment), skills=eval(player_model.skills),
            passives=eval(player_model.passives), current_area=player_model.current_area,
            in_fight=player_model.in_fight, in_dungeon=player_model.in_dungeon,
            defeated_bosses=eval(player_model.defeated_bosses),
            blessings=eval(player_model.blessings),
            missions_completed=missions_completed,
            active_mission=getattr(player_model, 'active_mission', 'None'),
            mission_end_time=getattr(player_model, 'mission_end_time', 0),
        )
        messager.messager_add_player(player_inst.name)
        PLAYER_CACHE.update({player_model.name: player_inst})


def load_everything() -> None:
    create_escordia_tables()
    print("Loading data...")
    load_items_from_json()
    load_equipment_from_json()
    load_enemies_from_json()
    load_areas_from_json()
    load_dungeons_from_json()
    load_shops_from_json()
    load_skills_from_json()
    load_missions_from_json()
    load_blessings_from_json()
    load_players_from_db()
