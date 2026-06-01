import random
import discord
import constants
import discord_logic
import emojis
import interface
import data_management
import discord_embeds


def _select_option(label: str, *, description: str = None, emoji=None, **kwargs) -> discord.SelectOption:
    """Builds a SelectOption, omitting emoji when empty (Discord rejects blank emojis)."""
    opt = {"label": label[:100], **kwargs}
    if description:
        opt["description"] = description[:100]
    resolved = emoji if emoji is not None else None
    if isinstance(resolved, str):
        resolved = emojis.select_emoji(resolved)
    if resolved:
        opt["emoji"] = resolved
    return discord.SelectOption(**opt)


class ActionMenu(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="Ataque", style=discord.ButtonStyle.red)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.attack(self.ctx)
            await interaction.response.defer()

    @discord.ui.button(label="Jutsu", style=discord.ButtonStyle.primary)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            battle_inst = data_management.search_cache_battle_by_player(self.ctx.author.name)
            cooldown_str = ""
            if len(battle_inst.skills_in_cooldown) != 0:
                skills_in_cooldown_str_list = [
                    f"**{s}**: {battle_inst.skills_in_cooldown[s] + 1}"
                    for s in battle_inst.skills_in_cooldown
                ]
                cooldown_str = f"\nEm cooldown - {','.join(skills_in_cooldown_str_list)}"
            skill_list = battle_inst.player.skills.copy()
            for skill_name in battle_inst.skills_in_cooldown:
                if skill_name in skill_list:
                    skill_list.remove(skill_name)
            if len(skill_list) == 0:
                await self.ctx.send(f"**Naruto RPG Error** - {self.ctx.author.mention}: Nenhum jutsu disponível!")
            else:
                await interaction.response.send_message(
                    f"Selecione um jutsu, {self.ctx.author.mention}.\n"
                    f"Use `!skills` para detalhes.\n{cooldown_str}",
                    view=SkillSelectView(self.ctx, skill_list, battle_inst.player),
                )

    @discord.ui.button(label="Inspecionar", style=discord.ButtonStyle.green)
    async def menu3(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await interaction.response.send_message(
                embed=discord_embeds.embed_enemy_info(
                    self.ctx,
                    data_management.search_cache_battle_by_player(self.ctx.author.name).enemy,
                )
            )


class PlayerMenu(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label=emojis.CROSSED_SWORDS_EMOJI + " Lutar", style=discord.ButtonStyle.red)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.begin_fight(self.ctx, ActionMenu(self.ctx))
            await interaction.response.defer()

    @discord.ui.button(label=emojis.CASTLE_EMOJI + " Instância", style=discord.ButtonStyle.red)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.dungeon(self.ctx)
            await interaction.response.defer()

    @discord.ui.button(label=emojis.SKULL_EMOJI + " Boss", style=discord.ButtonStyle.red)
    async def menu3(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.begin_boss_fight(self.ctx, ActionMenu(self.ctx))
            await interaction.response.defer()

    @discord.ui.button(label=emojis.MAP_EMOJI + " Mapa", style=discord.ButtonStyle.primary)
    async def menu4(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.area(self.ctx)
            await interaction.response.defer()

    @discord.ui.button(label=emojis.NINJA_EMOJI + " Equip.", style=discord.ButtonStyle.primary)
    async def menu5(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.equipment(self.ctx)
            await interaction.response.defer()

    @discord.ui.button(label=emojis.SPARKLER_EMOJI + " Jutsus", style=discord.ButtonStyle.primary)
    async def menu6(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.show_skills(self.ctx)
            await interaction.response.defer()

    @discord.ui.button(label=emojis.SCROLL_EMOJI + " Academia", style=discord.ButtonStyle.primary)
    async def menu7(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.academy_ninja(self.ctx)
            await interaction.response.defer()

    @discord.ui.button(label=emojis.MISSION_EMOJI + " Missões", style=discord.ButtonStyle.primary)
    async def menu8(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.missoes(self.ctx)
            await interaction.response.defer()

    @discord.ui.button(label=emojis.SHOP_EMOJI + " Loja", style=discord.ButtonStyle.green)
    async def menu9(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.shop(self.ctx)
            await interaction.response.defer()

    @discord.ui.button(label=emojis.EXTRACT_ESSENCE_EMOJI + " Essência", style=discord.ButtonStyle.green)
    async def menu10(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.essence(self.ctx)
            await interaction.response.defer()

    @discord.ui.button(label=f"{emojis.HEART_EMOJI} Sobre", style=discord.ButtonStyle.green)
    async def menu11(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            await discord_logic.about(self.ctx)
            await interaction.response.defer()


class AcademyNinjaView(discord.ui.View):
    """Academy registration: clan + element selection."""

    def __init__(self, ctx):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.selected_clan = None
        self.selected_element = None
        self.add_item(ClanSelect(ctx, self))
        self.add_item(ElementSelect(ctx, self))

    @discord.ui.button(label="Confirmar Registro", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await check_button_pressed(self.ctx, interaction):
            return
        if not self.selected_clan or not self.selected_element:
            await interaction.response.send_message("Selecione Clã e Elemento antes de confirmar.")
            return
        no_error, msgs = interface.set_ninja_identity(
            self.ctx.author.name, self.selected_clan, self.selected_element,
        )
        if no_error:
            await interaction.response.send_message(discord_logic.msgs_to_msg_str(msgs))
            await discord_logic.profile(self.ctx, PlayerMenu(self.ctx))
        else:
            await interaction.response.send_message(f"Erro: {discord_logic.msgs_to_msg_str(msgs)}")


class ClanSelect(discord.ui.Select):
    def __init__(self, ctx, parent_view):
        clans = [c for c in constants.CLANS if c != "Nenhum"]
        options = [
            discord.SelectOption(label=c, emoji=emojis.clan_to_emoji.get(c), description=f"Clã {c}")
            for c in clans
        ]
        super().__init__(placeholder="Escolha seu Clã", min_values=1, max_values=1, options=options)
        self.ctx = ctx
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if await check_button_pressed(self.ctx, interaction):
            self.parent_view.selected_clan = self.values[0]
            await interaction.response.send_message(f"Clã selecionado: **{self.values[0]}**", ephemeral=True)


class ElementSelect(discord.ui.Select):
    def __init__(self, ctx, parent_view):
        elements = [e for e in constants.ELEMENTS if e != "Nenhum"]
        options = [
            discord.SelectOption(label=e, emoji=emojis.element_to_emoji.get(e), description=f"Elemento {e}")
            for e in elements
        ]
        super().__init__(placeholder="Escolha sua Afinidade Elemental", min_values=1, max_values=1, options=options)
        self.ctx = ctx
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if await check_button_pressed(self.ctx, interaction):
            self.parent_view.selected_element = self.values[0]
            await interaction.response.send_message(f"Elemento selecionado: **{self.values[0]}**", ephemeral=True)


class MissionSelect(discord.ui.Select):
    def __init__(self, ctx, mission_list):
        options = [
            discord.SelectOption(
                label=f"[{m.rank}] {m.name}",
                value=m.name,
                description=f"Stamina: {m.stamina_cost} | Ryo: {m.ryo_reward} | XP: {m.xp_reward}",
                emoji=emojis.MISSION_EMOJI,
            )
            for m in mission_list[:25]
        ]
        super().__init__(placeholder="Aceitar missão", min_values=1, max_values=1, options=options or [
            discord.SelectOption(label="Nenhuma missão", value="none"),
        ])
        self.ctx = ctx
        self.mission_list = mission_list

    async def callback(self, interaction: discord.Interaction):
        if await check_button_pressed(self.ctx, interaction):
            mission_name = self.values[0]
            no_error, msgs = interface.accept_mission(self.ctx.author.name, mission_name)
            if no_error:
                await interaction.response.send_message(discord_logic.msgs_to_msg_str(msgs))
            else:
                await interaction.response.send_message(f"Erro: {discord_logic.msgs_to_msg_str(msgs)}")


class MissionSelectView(discord.ui.View):
    def __init__(self, ctx, mission_list):
        super().__init__(timeout=None)
        if mission_list:
            self.add_item(MissionSelect(ctx, mission_list))


class ItemBuySelect(discord.ui.Select):
    def __init__(self, ctx, item_list):
        items_in_options = [data_management.search_cache_item_by_name(i) for i in item_list]
        options = [
            _select_option(
                label=i.name,
                description=(
                    f"{i.description if i.object_type != 'EQUIPMENT' else ''}"
                    f"{i.stat_list_formatted() if hasattr(i, 'stat_list_formatted') else ''} - {i.individual_value} Ryo"
                ),
                emoji=emojis.obj_emoji(i),
            )
            for i in items_in_options if i is not None
        ]
        super().__init__(placeholder="Comprar item", max_values=1, min_values=1, options=options)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        if await check_button_pressed(self.ctx, interaction):
            item = data_management.search_cache_item_by_name(self.values[0])
            no_error, msgs = interface.buy_item(self.ctx.author.name, item.name)
            if no_error:
                await interaction.response.send_message(discord_logic.msgs_to_msg_str(msgs))
            else:
                await self.ctx.send(f'**Naruto RPG Error** - {self.ctx.author.mention}: {msgs}')


class ItemBuySelectView(discord.ui.View):
    def __init__(self, ctx, item_list):
        super().__init__(timeout=None)
        self.add_item(ItemBuySelect(ctx, item_list))


class ItemDestroySelect(discord.ui.Select):
    def __init__(self, ctx, item_list):
        items_in_options = [data_management.search_cache_item_by_name(i) for i in item_list]
        options = [
            _select_option(
                label=i.name,
                description=(
                    f"{i.description if i.object_type != 'EQUIPMENT' else ''}"
                    f"{i.stat_list_formatted() if hasattr(i, 'stat_list_formatted') else ''}"
                ),
                emoji=emojis.obj_emoji(i),
            )
            for i in items_in_options if i is not None
        ]
        super().__init__(placeholder="Destruir item", max_values=1, min_values=1, options=options)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        if await check_button_pressed(self.ctx, interaction):
            item = data_management.search_cache_item_by_name(self.values[0])
            no_error, msgs = interface.destroy_item_for_essence(self.ctx.author.name, item.name)
            if no_error:
                await interaction.response.send_message(discord_logic.msgs_to_msg_str(msgs))
            else:
                await self.ctx.send(f'**Naruto RPG Error** - {self.ctx.author.mention}: {msgs}')


class ItemDestroySelectView(discord.ui.View):
    def __init__(self, ctx, item_list):
        super().__init__(timeout=None)
        self.add_item(ItemDestroySelect(ctx, item_list))
        self.ctx = ctx

    @discord.ui.button(label="Destruir todos", style=discord.ButtonStyle.red)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed(self.ctx, interaction):
            no_error, msgs = interface.destroy_all_items_for_essence(self.ctx.author.name)
            if no_error:
                await interaction.response.send_message(discord_logic.msgs_to_msg_str(msgs))
            else:
                await self.ctx.send(f'**Naruto RPG Error** - {self.ctx.author.mention}: {msgs}')


class BlessingBuySelect(discord.ui.Select):
    def __init__(self, ctx, player_blessing_list):
        items_in_options = []
        for b in data_management.BLESSINGS_CACHE:
            if b not in player_blessing_list:
                items_in_options.append(data_management.search_cache_blessing(b))
        options = [
            discord.SelectOption(
                label=b.name,
                description=f"{' '.join(b.stat_change_list)} - {b.essence_cost} Essência",
                emoji=emojis.ESC_ESSENCE_ICON,
            )
            for b in items_in_options
        ]
        super().__init__(placeholder="Comprar bênção", max_values=1, min_values=1, options=options or [
            discord.SelectOption(label="Nenhuma disponível", value="none"),
        ])
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        if await check_button_pressed(self.ctx, interaction):
            no_error, msgs = interface.purchase_blessing(self.ctx.author.name, self.values[0])
            if no_error:
                await interaction.response.send_message(discord_logic.msgs_to_msg_str(msgs))
            else:
                await self.ctx.send(f'**Naruto RPG Error** - {self.ctx.author.mention}: {msgs}')


class BlessingBuySelectView(discord.ui.View):
    def __init__(self, ctx, player_blessing_list):
        super().__init__(timeout=None)
        self.add_item(BlessingBuySelect(ctx, player_blessing_list))


class EquipmentSelect(discord.ui.Select):
    def __init__(self, ctx, item_list, player_equipment):
        default_option = None
        player_eq_inst = None
        if player_equipment is not None:
            player_eq_inst = data_management.search_cache_item_by_name(player_equipment)
            default_option = _select_option(
                label=player_eq_inst.name,
                description=f"{player_eq_inst.stat_list_formatted()}",
                emoji=emojis.obj_emoji(player_eq_inst),
                default=True,
            )
        items_in_options = [data_management.search_cache_item_by_name(i.name) for i in item_list]
        if player_eq_inst in items_in_options:
            items_in_options.remove(player_eq_inst)
        options = [
            _select_option(label=i.name, description=f"{i.stat_list_formatted()}", emoji=emojis.obj_emoji(i))
            for i in items_in_options if i is not None
        ]
        if default_option is not None:
            options.append(default_option)
        super().__init__(placeholder="Equipar item", max_values=1, min_values=1, options=options or [
            discord.SelectOption(label="Vazio", value="empty"),
        ])
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        if await check_button_pressed(self.ctx, interaction):
            item = data_management.search_cache_item_by_name(self.values[0])
            no_error, msgs = interface.equip_item(self.ctx.author.name, item.name)
            if no_error:
                await interaction.response.send_message(discord_logic.msgs_to_msg_str(msgs))
            else:
                await self.ctx.send(f'**Naruto RPG Error** - {self.ctx.author.mention}: {msgs}')


class EquipmentSelectView(discord.ui.View):
    def __init__(self, ctx, item_list, player_equipment):
        super().__init__(timeout=None)
        self.add_item(EquipmentSelect(ctx, item_list, player_equipment))


class AreaSelect(discord.ui.Select):
    def __init__(self, ctx, player_inst):
        current_area = data_management.search_cache_area_by_number(player_inst.current_area)
        default_option = discord.SelectOption(
            label=current_area.name, description=f"Área {current_area.number}",
            emoji=emojis.MAP_EMOJI, default=True,
        )
        areas_in_options = [
            data_management.search_cache_area_by_number(a)
            for a in data_management.AREAS_CACHE
            if int(a) <= len(player_inst.defeated_bosses) + 1
        ]
        if current_area in areas_in_options:
            areas_in_options.remove(current_area)
        options = [
            discord.SelectOption(label=a.name, description=f"Rank: {a.min_rank}", emoji=emojis.MAP_EMOJI)
            for a in areas_in_options
        ]
        options.append(default_option)
        super().__init__(placeholder="Viajar para área", max_values=1, min_values=1, options=options)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        if await check_button_pressed(self.ctx, interaction):
            area = data_management.search_cache_area_by_name(self.values[0])
            no_error, msgs = interface.travel_to_area(self.ctx.author.name, area.number)
            if no_error:
                await interaction.response.send_message(discord_logic.msgs_to_msg_str(msgs))
            else:
                await self.ctx.send(f'**Naruto RPG Error** - {self.ctx.author.mention}: {msgs}')


class AreaSelectView(discord.ui.View):
    def __init__(self, ctx, player_inst):
        super().__init__(timeout=None)
        self.add_item(AreaSelect(ctx, player_inst))


class DungeonSelect(discord.ui.Select):
    def __init__(self, ctx, dungeon_list):
        options = [
            discord.SelectOption(
                label=i.dungeon_name,
                description=f"Rank: {i.min_rank} | Nv.{i.recommended_lvl} | Inimigos: {i.enemy_count + 1}",
                emoji=emojis.ESC_DUNGEON_ICON,
            )
            for i in dungeon_list if i is not None
        ]
        super().__init__(placeholder="Explorar instância", max_values=1, min_values=1, options=options)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        if await check_button_pressed(self.ctx, interaction):
            dungeon = data_management.search_cache_dungeon_by_name(self.values[0])
            no_error, msgs = interface.start_dungeon(self.ctx.author.name, dungeon.dungeon_name)
            if no_error:
                if data_management.search_cache_player(self.ctx.author.name).in_dungeon:
                    no_error, msgs = interface.begin_battle(
                        self.ctx.author.name, False, enemy=random.choice(dungeon.enemy_list),
                    )
                    await discord_logic.manage_battle(self.ctx, no_error, msgs, ActionMenu(self.ctx))
                    await interaction.response.defer()
            else:
                await self.ctx.send(f'**Naruto RPG Error** - {self.ctx.author.mention}: {msgs}')


class DungeonSelectView(discord.ui.View):
    def __init__(self, ctx, dungeon_list):
        super().__init__(timeout=None)
        self.add_item(DungeonSelect(ctx, dungeon_list))


class SkillSelect(discord.ui.Select):
    def __init__(self, ctx, skill_list, player_inst):
        skills_in_options = [data_management.search_cache_skill_by_name(i) for i in skill_list]
        options = []
        for s in skills_in_options:
            if s is None:
                continue
            can_use = (
                player_inst.stats[constants.CHAKRA_STATKEY] >= s.chakra_cost
                and player_inst.stats[constants.STAMINA_STATKEY] >= s.stamina_cost
            )
            options.append(discord.SelectOption(
                label=s.name,
                description=(
                    f"[{s.skill_type}] Chakra:{s.chakra_cost} Stamina:{s.stamina_cost} "
                    f"{'✓' if can_use else '✗'}"
                ),
                emoji=emojis.skill_emoji(s, player_inst.clan),
            ))
        super().__init__(placeholder="Selecionar jutsu", max_values=1, min_values=1, options=options)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction) -> None:
        if await check_button_pressed(self.ctx, interaction):
            skill_inst = data_management.search_cache_skill_by_name(self.values[0])
            no_error, msgs = interface.skill_attack(self.ctx.author.name, skill_inst.name)
            await discord_logic.continue_battle(self.ctx, no_error, msgs, ActionMenu(self.ctx))
            await interaction.response.defer()


class SkillSelectView(discord.ui.View):
    def __init__(self, ctx, skill_list, player_inst):
        super().__init__(timeout=None)
        self.add_item(SkillSelect(ctx, skill_list, player_inst))


class DuelSelectView(discord.ui.View):
    def __init__(self, ctx, battle_module):
        super().__init__(timeout=None)
        self.ctx = ctx


class ToinCossMenu(discord.ui.View):
    def __init__(self, ctx, dueled_player: str):
        super().__init__(timeout=None)
        self.dueled_player = dueled_player
        self.ctx = ctx

    @discord.ui.button(label="Cara", style=discord.ButtonStyle.red)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed_by_certain_name(self.ctx, interaction, self.dueled_player):
            await discord_logic.begin_pvp_fight(self.ctx, ActionMenu(self.ctx), self.ctx.author, self.dueled_player, "HEADS")
            await interaction.response.defer()

    @discord.ui.button(label="Coroa", style=discord.ButtonStyle.red)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await check_button_pressed_by_certain_name(self.ctx, interaction, self.dueled_player):
            await discord_logic.begin_pvp_fight(self.ctx, ActionMenu(self.ctx), self.ctx.author, self.dueled_player, "TAILS")
            await interaction.response.defer()


async def check_button_pressed(ctx, interaction: discord.Interaction) -> bool:
    if interaction.user.name == ctx.author.name:
        return True
    await interaction.response.send_message(f"Esse botão não é para você, {interaction.user.mention}!")
    return False


async def check_button_pressed_by_certain_name(ctx, interaction: discord.Interaction, certain_name: str) -> bool:
    if interaction.user.name == certain_name:
        return True
    await interaction.response.send_message(f"Esse botão não é para você, {interaction.user.mention}!")
    return False
