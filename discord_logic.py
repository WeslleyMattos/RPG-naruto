import constants
import random
import discord
import discord_embeds
import discord_ui
import emojis
import info_msgs
import interface
import data_management
import messager
import battle

from error_msgs import *


async def create_character(ctx) -> None:
    no_error, msgs = interface.create_player(ctx.author.name)
    if no_error:
        await ctx.send(
            f'Bem-vindo, {ctx.author.mention}, ao mundo ninja!\n'
            f'Complete seu registro na Academia Ninja.',
            embed=discord_embeds.embed_academy_msg(ctx),
            view=discord_ui.AcademyNinjaView(ctx),
        )
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def academy_ninja(ctx) -> None:
    player_inst = data_management.search_cache_player(ctx.author.name)
    if player_inst is None:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {ERROR_CHARACTER_DOES_NOT_EXIST}')
        return
    await ctx.send(
        embed=discord_embeds.embed_academy_msg(ctx),
        view=discord_ui.AcademyNinjaView(ctx),
    )


async def begin_fight(ctx, action_menu_ui: discord.ui.View) -> None:
    if constants.TREASURE_CHANCE_WHEN_FIGHTING >= random.randint(0, 100):
        no_error, msgs = interface.receive_treasure(ctx.author.name, constants.NUMBER_OF_ITEMS_IN_TREASURE)
        if no_error:
            await ctx.send(f'Enquanto explorava, {ctx.author.mention} encontrou um tesouro!')
            await ctx.send(embed=discord_embeds.embed_treasure_found(ctx, msgs))
        else:
            await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')
    else:
        no_error, msgs = interface.begin_battle(ctx.author.name, False)
        if no_error:
            battle_inst = data_management.search_cache_battle_by_player(ctx.author.name)
            await ctx.send(
                embed=discord_embeds.embed_fight_msg(ctx, battle_inst.player, battle_inst.enemy),
                view=action_menu_ui,
            )
        else:
            await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def begin_pvp_fight(ctx, action_menu_ui, duel_starter_player, dueled_player, coin_choice):
    result = random.choice(["HEADS", "TAILS"])
    if result == coin_choice:
        pass
    else:
        pass


async def begin_boss_fight(ctx, action_menu_ui) -> None:
    no_error, msgs = interface.begin_battle(ctx.author.name, True)
    if no_error:
        battle_inst = data_management.search_cache_battle_by_player(ctx.author.name)
        await ctx.send(
            embed=discord_embeds.embed_fight_msg(ctx, battle_inst.player, battle_inst.enemy),
            view=action_menu_ui,
        )
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def attack(ctx) -> None:
    no_error, msgs = interface.normal_attack(ctx.author.name)
    await continue_battle(ctx, no_error, msgs, discord_ui.ActionMenu(ctx))


async def rest(ctx) -> None:
    no_error, msgs = interface.player_rest(ctx.author.name)
    if no_error:
        await ctx.send(msgs_to_msg_str(msgs))
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def inventory(ctx) -> None:
    no_error, msgs = interface.show_player_inventory(ctx.author.name)
    if no_error:
        await ctx.send(msgs_to_msg_str(msgs))
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def shop(ctx) -> None:
    no_error, msgs = interface.show_shop_inventory(ctx.author.name)
    if no_error:
        player_inst = data_management.search_cache_player(ctx.author.name)
        item_list = data_management.search_cache_shop_by_area(player_inst.current_area).item_list
        await ctx.send(
            f"Selecione um item, {ctx.author.mention}. Saldo: **{player_inst.ryo}** {emojis.RYO_EMOJI}",
            view=discord_ui.ItemBuySelectView(ctx, item_list),
        )
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def equipment(ctx) -> None:
    player_inst = data_management.search_cache_player(ctx.author.name)
    if player_inst is None:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {ERROR_CHARACTER_DOES_NOT_EXIST}')
        return
    if data_management.search_cache_battle_by_player(ctx.author.name) is not None:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {ERROR_CANNOT_DO_WHILE_IN_FIGHT}')
        return

    await ctx.send(f"{emojis.NINJA_EMOJI} Equipamento atual, {ctx.author.mention}:")
    for e_type in constants.EQUIPMENT_TYPES:
        item_list = player_inst.inventory.get_equipment_from_type(e_type)
        if len(item_list) == 0 and player_inst.equipment[e_type] is None:
            await ctx.send(f"**{e_type}**\nNenhum item.")
        else:
            await ctx.send(
                f"**{e_type}**",
                view=discord_ui.EquipmentSelectView(ctx, item_list, player_inst.equipment[e_type]),
            )


async def essence(ctx) -> None:
    no_error, msgs = interface.essence_crafting(ctx.author.name)
    if no_error:
        player_inst = data_management.search_cache_player(ctx.author.name)
        if len(player_inst.inventory.items) == 0:
            await ctx.send(f"{ctx.author.mention} {info_msgs.ESSENCE_MSG}\nSem itens para destruir.")
        else:
            await ctx.send(
                f"{ctx.author.mention} {info_msgs.ESSENCE_MSG}",
                view=discord_ui.ItemDestroySelectView(ctx, player_inst.inventory.items),
            )
        await ctx.send(
            f"{ctx.author.mention} Essência: **{player_inst.essence}** {emojis.ESC_ESSENCE_ICON}.",
            view=discord_ui.BlessingBuySelectView(ctx, player_inst.blessings),
        )
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def about(ctx) -> None:
    await ctx.send(f'{ctx.author.mention} {info_msgs.ABOUT_MSG}')


async def area(ctx) -> None:
    no_error, msgs = interface.show_area(ctx.author.name)
    if no_error:
        player_inst = data_management.search_cache_player(ctx.author.name)
        await ctx.send(msgs_to_msg_str(msgs), view=discord_ui.AreaSelectView(ctx, player_inst))
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def profile(ctx, player_menu_ui: discord.ui.View) -> None:
    no_error, msgs = interface.show_player_profile(ctx.author.name)
    if no_error:
        player_inst = data_management.search_cache_player(ctx.author.name)
        await ctx.send(
            embed=discord_embeds.embed_player_profile(ctx, ctx.author.name, player_inst),
            view=player_menu_ui,
        )
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def missoes(ctx) -> None:
    no_error, msgs = interface.show_missions(ctx.author.name)
    if no_error:
        player_inst = data_management.search_cache_player(ctx.author.name)
        missions = data_management.search_available_missions_for_player(player_inst)
        await ctx.send(
            embed=discord_embeds.embed_missions_board(ctx, msgs_to_msg_str(msgs)),
            view=discord_ui.MissionSelectView(ctx, missions),
        )
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def show_skills(ctx) -> None:
    player_inst = data_management.search_cache_player(ctx.author.name)
    if player_inst is None:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {ERROR_CHARACTER_DOES_NOT_EXIST}')
        return

    skill_str = ""
    for s in player_inst.skills:
        skill_inst = data_management.search_cache_skill_by_name(s)
        if skill_inst is not None:
            skill_str += (
                f"**{s}** [{skill_inst.skill_type}] "
                f"{emojis.skill_emoji(skill_inst, player_inst.clan)}\n"
                f"_{skill_inst.description}_\n"
                f"Poder: {skill_inst.power} | Chakra: {skill_inst.chakra_cost} | "
                f"Stamina: {skill_inst.stamina_cost} | CD: {skill_inst.cooldown}\n\n"
            )
    await ctx.send(embed=discord_embeds.embed_skills_info(ctx, player_inst.name, skill_str))


async def dungeon(ctx) -> None:
    no_error, msgs = interface.show_dungeons(ctx.author.name)
    if no_error:
        dungeon_list = [data_management.search_cache_dungeon_by_name(d) for d in msgs]
        await ctx.send(
            f"Selecione uma instância, {ctx.author.mention}",
            view=discord_ui.DungeonSelectView(ctx, dungeon_list),
        )
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def duel(ctx, enemy_name: str) -> None:
    no_error, msgs = interface.duel_check(ctx.author.name, enemy_name)
    if no_error:
        await ctx.send(embed=discord_embeds.embed_duel_msg(ctx, enemy_name), view=discord_ui.DuelSelectView(ctx, battle))
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def continue_battle(ctx, no_error: bool, msgs: list, action_menu_ui: discord.ui.View) -> None:
    if no_error:
        battle_inst = data_management.search_cache_battle_by_player(ctx.author.name)
        msg_str = msgs_to_msg_str(msgs)

        if battle_inst.is_over:
            await ctx.send(msg_str)
            if battle_inst.player.alive:
                loot = battle_inst.win_battle()
                await ctx.send('', embed=discord_embeds.embed_victory_msg(ctx, msgs_to_msg_str(messager.empty_queue(ctx.author.name))))
                if loot != '':
                    await ctx.send(embed=discord_embeds.embed_treasure_found(ctx, [loot]))
                if battle_inst.player.in_dungeon:
                    await traverse_dungeon(ctx, battle_inst)
                else:
                    await profile(ctx, discord_ui.PlayerMenu(ctx))
            else:
                battle_inst.lose_battle()
                await ctx.send('', embed=discord_embeds.embed_death_msg(ctx))
                await profile(ctx, discord_ui.PlayerMenu(ctx))
        else:
            await ctx.send(
                msg_str,
                embed=discord_embeds.embed_fight_msg(ctx, battle_inst.player, battle_inst.enemy),
                view=action_menu_ui,
            )
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs}')


async def manage_battle(ctx, no_error: bool, msgs: list, action_menu_ui: discord.ui.View) -> None:
    if no_error:
        battle_inst = data_management.search_cache_battle_by_player(ctx.author.name)
        await ctx.send(
            embed=discord_embeds.embed_fight_msg(ctx, battle_inst.player, battle_inst.enemy),
            view=action_menu_ui,
        )
    else:
        await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')


async def traverse_dungeon(ctx, battle_inst: battle.Battle) -> None:
    dungeon_inst = data_management.search_cache_dungeon_inst_by_player(battle_inst.player.name)
    if dungeon_inst.boss_defeated:
        no_error, msgs = interface.receive_treasure(ctx.author.name, random.randint(2, 3))
        battle_inst.player.in_dungeon = False
        if no_error:
            await ctx.send(embed=discord_embeds.embed_treasure_found(ctx, msgs))
            await profile(ctx, discord_ui.PlayerMenu(ctx))
        else:
            await ctx.send(f'**Naruto RPG Error** - {ctx.author.mention}: {msgs_to_msg_str(msgs)}')
        data_management.delete_cache_dungeon_inst(battle_inst.player.name)
        data_management.update_player_info(battle_inst.player.name)
    else:
        if dungeon_inst.current_enemies_defeated != dungeon_inst.enemy_count:
            no_error, msgs = interface.begin_battle(ctx.author.name, False, enemy=random.choice(dungeon_inst.enemy_list))
            await manage_battle(ctx, no_error, msgs, discord_ui.ActionMenu(ctx))
        else:
            no_error, msgs = interface.begin_battle(ctx.author.name, False, enemy=dungeon_inst.boss)
            await manage_battle(ctx, no_error, msgs, discord_ui.ActionMenu(ctx))


def msgs_to_msg_str(msgs: list) -> str:
    return "\n".join(msgs)
