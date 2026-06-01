import discord
import data_management
import emojis
import formulas
import enemy
import player
import info_msgs

from StringProgressBar import progressBar


def embed_help_msg(ctx) -> discord.Embed:
    embed = discord.Embed(
        title='Naruto RPG - Ajuda',
        description=f'{info_msgs.HELP_MSG}',
        color=discord.Colour.red()
    )
    return embed


def embed_fight_msg(ctx, player_obj, enemy_inst) -> discord.Embed:
    hp_bar = progressBar.filledBar(enemy_inst.stats['MAXHP'], enemy_inst.stats['HP'], size=10)
    player_hp_bar = progressBar.filledBar(player_obj.stats['MAXHP'], player_obj.stats['HP'], size=10)
    player_chakra_bar = progressBar.filledBar(
        player_obj.stats['MAXCHAKRA'], player_obj.stats['CHAKRA'], size=10,
    )
    player_stamina_bar = progressBar.filledBar(
        player_obj.stats['MAXSTAMINA'], player_obj.stats['STAMINA'], size=10,
    )
    player_shield = f"SHIELD: {player_obj.shield}{emojis.SHIELD_EMOJI}\n"
    enemy_shield = f"SHIELD: {enemy_inst.shield}{emojis.SHIELD_EMOJI}\n"

    embed = discord.Embed(
        title=f'Combate - {ctx.author.name.capitalize()}',
        description=(
            f'Você está lutando contra **{enemy_inst.name}**.\n'
            f'{enemy_shield if enemy_inst.shield > 0 else ""}'
            f'HP: {hp_bar[0]} - {enemy_inst.stats["HP"]}/{enemy_inst.stats["MAXHP"]}'
        ),
        color=discord.Colour.red()
    )
    embed.set_thumbnail(url=enemy_inst.image_url if enemy_inst.image_url else None)
    if ctx.author.avatar:
        embed.set_image(url=ctx.author.avatar.url)

    if len(enemy_inst.buffs_and_debuffs.keys()) > 0:
        embed.add_field(
            name="Alterações do inimigo:",
            value=" ".join([emojis.buff_debuff_to_emoji.get(bd, '') for bd in enemy_inst.buffs_and_debuffs]),
            inline=True,
        )
    if len(player_obj.buffs_and_debuffs.keys()) > 0:
        embed.add_field(
            name="Suas alterações:",
            value=" ".join([emojis.buff_debuff_to_emoji.get(bd, '') for bd in player_obj.buffs_and_debuffs]),
            inline=True,
        )

    embed.set_footer(
        text=(
            f'{player_obj.name}\n'
            f'{player_shield if player_obj.shield > 0 else ""}'
            f'{emojis.HP_EMOJI} HP: {player_obj.stats["HP"]}/{player_obj.stats["MAXHP"]} | {player_hp_bar[0]}\n'
            f'{emojis.CHAKRA_EMOJI} Chakra: {player_obj.stats["CHAKRA"]}/{player_obj.stats["MAXCHAKRA"]} | {player_chakra_bar[0]}\n'
            f'{emojis.STAMINA_EMOJI} Stamina: {player_obj.stats["STAMINA"]}/{player_obj.stats["MAXSTAMINA"]} | {player_stamina_bar[0]}\n'
            f'Acerto: {100 - formulas.miss_formula(player_obj.stats["SPEED"], enemy_inst.stats["SPEED"])}% | '
            f'Crítico: {player_obj.stats["CRITCH"]}%'
        )
    )
    return embed


def embed_victory_msg(ctx, msg: str) -> discord.Embed:
    embed = discord.Embed(
        title=f'{emojis.SPARKLER_EMOJI} Vitória! {emojis.SPARKLER_EMOJI}',
        description=msg,
        color=discord.Colour.red()
    )
    if ctx.author.avatar:
        embed.set_image(url=ctx.author.avatar.url)
    return embed


def embed_death_msg(ctx) -> discord.Embed:
    embed = discord.Embed(
        title=f'{emojis.SKULL_EMOJI} Derrota {emojis.SKULL_EMOJI}',
        description='Você foi derrotado.',
        color=discord.Colour.red()
    )
    if ctx.author.avatar:
        embed.set_image(url=ctx.author.avatar.url)
    return embed


def embed_duel_msg(ctx, enemy_name: str) -> discord.Embed:
    embed = discord.Embed(
        title=f'{emojis.CROSSED_SWORDS_EMOJI} Duelo {emojis.CROSSED_SWORDS_EMOJI}',
        description=(
            f'@{enemy_name}, {ctx.author.name.capitalize()} desafiou você para um duelo! '
            f'Escolha **cara** ou **coroa**.'
        ),
        color=discord.Colour.red()
    )
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    return embed


def embed_enemy_info(ctx, enemy_inst: enemy.Enemy) -> discord.Embed:
    bd_str = ''
    if len(enemy_inst.buffs_and_debuffs) > 0:
        bd_str = (
            f"\n**Alterações**\n"
            f"{' '.join([emojis.buff_debuff_to_emoji.get(bd, '') for bd in enemy_inst.buffs_and_debuffs])}\n\n"
        )

    enemy_skills_str = "\n"
    for s in enemy_inst.skills:
        skill_inst = data_management.search_cache_skill_by_name(s)
        if skill_inst is not None:
            enemy_skills_str += (
                f"- **{s}** [{skill_inst.skill_type}] {emojis.skill_emoji(skill_inst)}\n"
                f"_{skill_inst.description}_\n"
                f"Poder: {skill_inst.power} | Chakra: {skill_inst.chakra_cost} | "
                f"Stamina: {skill_inst.stamina_cost} | CD: {skill_inst.cooldown}\n\n"
            )

    if enemy_inst.possible_loot is None:
        loot_str = 'Nenhum'
    else:
        loot_str = (
            f'{enemy_inst.possible_loot} '
            f'{emojis.obj_emoji(data_management.search_cache_item_by_name(enemy_inst.possible_loot))} '
            f'- {enemy_inst.loot_chance}%'
        )

    element_str = emojis.element_to_emoji.get(enemy_inst.element, '')
    embed = discord.Embed(
        title=f'Inimigo - {enemy_inst.name}',
        description=(
            f'_{enemy_inst.description}_\n\n{enemy_inst.show_enemy_info()}{bd_str}'
            f'**Elemento**: {enemy_inst.element} {element_str}\n'
            f'**Fraquezas**: {" ".join([emojis.element_to_emoji.get(e, e) for e in enemy_inst.weaknesses])}\n'
            f'**Resistências**: {" ".join([emojis.element_to_emoji.get(e, e) for e in enemy_inst.resistances])}\n'
            f'**Loot Possível**: {loot_str}\n'
            f'**Jutsus**{enemy_skills_str}'
        ),
        color=discord.Colour.red()
    )
    if enemy_inst.image_url:
        embed.set_image(url=enemy_inst.image_url)
    return embed


def embed_player_profile(ctx, player_name: str, player_inst: player.Player) -> discord.Embed:
    embed = discord.Embed(
        title=f'🪪 Registro Ninja: {player_name.capitalize()}',
        description=player_inst.show_player_info(),
        color=discord.Colour.red()
    )

    embed.add_field(name='Identidade Ninja', value=player_inst.show_ninja_profile(), inline=True)
    embed.add_field(name='Status', value=player_inst.show_player_stats(), inline=True)
    embed.add_field(name='Inventário', value=f'{player_inst.inventory.show_inventory()}', inline=True)
    embed.add_field(
        name='Recursos',
        value=(
            f'{player_inst.ryo} {emojis.RYO_EMOJI}  '
            f'{player_inst.essence} {emojis.ESC_ESSENCE_ICON}'
        ),
        inline=True,
    )
    embed.add_field(name='Jutsus', value=player_inst.show_current_skills_as_list(), inline=False)
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    return embed


def embed_skills_info(ctx, player_name: str, skills_str: str) -> discord.Embed:
    embed = discord.Embed(
        title=f'{emojis.SPARKLER_EMOJI} Jutsus - {player_name.capitalize()}',
        description=skills_str,
        color=discord.Colour.red()
    )
    if ctx.author.avatar:
        embed.set_thumbnail(url=ctx.author.avatar.url)
    return embed


def embed_treasure_found(ctx, item_list: list) -> discord.Embed:
    embed = discord.Embed(
        title=f'{emojis.CHEST_EMOJI} Tesouro encontrado! {emojis.CHEST_EMOJI}',
        description='Você encontrou:\n\n' + '\n'.join([
            f'- {item} {emojis.obj_emoji(data_management.search_cache_item_by_name(item))}'
            for item in item_list
        ]),
        color=discord.Colour.red()
    )
    return embed


def embed_academy_msg(ctx) -> discord.Embed:
    embed = discord.Embed(
        title=f'{emojis.NINJA_EMOJI} Academia Ninja',
        description=(
            'Bem-vindo à Academia Ninja! Escolha seu **Clã** e sua **Afinidade Elemental** '
            'para completar seu registro.'
        ),
        color=discord.Colour.blue()
    )
    return embed


def embed_missions_board(ctx, missions_str: str) -> discord.Embed:
    embed = discord.Embed(
        title=f'{emojis.MISSION_EMOJI} Quadro de Missões da Vila',
        description=missions_str,
        color=discord.Colour.green()
    )
    return embed
