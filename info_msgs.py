import emojis

HELP_MSG = (
    f"{emojis.SPARKLER_EMOJI} **--- GERAL ---** {emojis.SPARKLER_EMOJI}\n"
    "`!start` - Cria um novo ninja\n"
    "`!tutorial` - Mostra o tutorial\n"
    "`!help` - Lista todos os comandos\n"
    f"{emojis.NINJA_EMOJI} **--- NINJA ---** {emojis.NINJA_EMOJI}\n"
    "`!profile` - Registro ninja (perfil)\n"
    "`!menu` - Menu principal com botões\n"
    "`!rest` - Recupera HP, Chakra e Stamina\n"
    "`!skills` - Detalhes dos seus jutsus\n"
    "`!equipment` - Equipamentos\n"
    "`!academy` - Academia Ninja (Clã e Elemento)\n"
    "`!shop` - Loja da área atual\n"
    f"{emojis.CROSSED_SWORDS_EMOJI} **--- COMBATE ---** {emojis.CROSSED_SWORDS_EMOJI}\n"
    "`!fight` - Procurar inimigo na área\n"
    "`!dungeon` - Instâncias disponíveis\n"
    "`!boss` - Lutar contra o boss da área\n"
    f"{emojis.MISSION_EMOJI} **--- MISSÕES ---** {emojis.MISSION_EMOJI}\n"
    "`!missoes` - Quadro de Missões da Vila\n"
)

TUTORIAL_MSG = (
    "Olá, futuro ninja! Bem-vindo ao **Naruto RPG**!\n\n"
    "Lute contra inimigos na sua **área**, ganhe **Ryo** e **XP**. Compre **equipamentos** na **loja** "
    "ou explore **instâncias** (dungeons). Se estiver ferido, use **!rest** para recuperar "
    f"{emojis.HP_EMOJI} HP, {emojis.CHAKRA_EMOJI} Chakra e {emojis.STAMINA_EMOJI} Stamina.\n\n"
    "Após `!start`, complete seu registro na **Academia Ninja** escolhendo **Clã** e **Afinidade Elemental**. "
    "Suba de **Rank Ninja** (Genin → Chunin → Jonin) completando missões e ganhando níveis.\n\n"
    "Use `!missoes` para aceitar missões do quadro da vila. Quando estiver pronto, enfrente o **boss** "
    "da área para desbloquear a próxima!\n\n"
    "--> __Jogue quase tudo pelo comando__ `!menu` :) <--"
)

ESSENCE_MSG = (
    f"Você pode destruir itens por essência {emojis.ESC_ESSENCE_ICON}. "
    "Gaste essência em bênçãos permanentes."
)
PVP_MSG = (
    "Arena PvP: duelos 1v1 sem recompensas, apenas honra. "
    "Use `!duel [nome do personagem]`."
)
CREDITS = (
    "**CRÉDITOS**\nProjeto base Escordia RPG por **rodmarkun**. "
    "Refatorado para tema Naruto."
)
SUPPORT = (
    f"**SUPORTE**\n"
    f"- **Star** {emojis.SPARKLER_EMOJI} no Github!\n"
    f"- **Compartilhe** {emojis.HEART_EMOJI} com seus amigos!\n\nObrigado!"
)
ABOUT_MSG = (
    "\n**SOBRE O NARUTO RPG**\n"
    "Bot de RPG para Discord baseado no sistema Escordia, adaptado ao universo ninja.\n\n"
    f"{CREDITS}\n\n{SUPPORT}"
)
