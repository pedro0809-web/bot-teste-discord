import os
import discord

from discord.ext import commands
from discord.ui import View, button

from supabase import create_client
from dotenv import load_dotenv

# ==================================================
# CARREGAR .ENV
# ==================================================

load_dotenv()

TOKEN = os.getenv("TOKEN")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ==================================================
# CONECTAR SUPABASE
# ==================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ==================================================
# CONFIG DISCORD
# ==================================================

intents = discord.Intents.default()

intents.guilds = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ==================================================
# CONFIG
# ==================================================

CATEGORIA_SALAS = "SALAS FREE FIRE"

# ==================================================
# VIEW DOS BOTÕES
# ==================================================

class PainelSalas(View):

    def __init__(self):
        super().__init__(timeout=None)

    # ===============================================
    # BOTÃO 1X1
    # ===============================================

    @button(
        label="1x1 - R$5",
        style=discord.ButtonStyle.green,
        emoji="🎮",
        custom_id="1x1_5"
    )
    async def sala_1x1(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await criar_sala(
            interaction,
            "1x1",
            "5"
        )

    # ===============================================
    # BOTÃO 2X2
    # ===============================================

    @button(
        label="2x2 - R$10",
        style=discord.ButtonStyle.blurple,
        emoji="🔥",
        custom_id="2x2_10"
    )
    async def sala_2x2(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await criar_sala(
            interaction,
            "2x2",
            "10"
        )

    # ===============================================
    # BOTÃO 4X4
    # ===============================================

    @button(
        label="4x4 - R$20",
        style=discord.ButtonStyle.red,
        emoji="🏆",
        custom_id="4x4_20"
    )
    async def sala_4x4(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await criar_sala(
            interaction,
            "4x4",
            "20"
        )

# ==================================================
# FUNÇÃO CRIAR SALA
# ==================================================

async def criar_sala(
    interaction,
    modalidade,
    valor
):

    guild = interaction.guild

    # ===============================================
    # PROCURAR CATEGORIA
    # ===============================================

    categoria = discord.utils.get(
        guild.categories,
        name=CATEGORIA_SALAS
    )

    # ===============================================
    # CRIAR CATEGORIA SE NÃO EXISTIR
    # ===============================================

    if categoria is None:

        categoria = await guild.create_category(
            CATEGORIA_SALAS
        )

    # ===============================================
    # NOME DO CANAL
    # ===============================================

    nome_canal = (
        f"{modalidade}-{interaction.user.name}"
    )

    # ===============================================
    # PERMISSÕES
    # ===============================================

    overwrites = {

        guild.default_role:
        discord.PermissionOverwrite(
            read_messages=False
        ),

        interaction.user:
        discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True
        )
    }

    # ===============================================
    # CRIAR CANAL
    # ===============================================

    canal = await guild.create_text_channel(
        nome_canal,
        category=categoria,
        overwrites=overwrites
    )

    # ===============================================
    # SALVAR NO SUPABASE
    # ===============================================

    supabase.table("salas").insert({

        "usuario_id":
        str(interaction.user.id),

        "usuario_nome":
        interaction.user.name,

        "modalidade":
        modalidade,

        "valor":
        valor,

        "canal_id":
        str(canal.id)

    }).execute()

    # ===============================================
    # EMBED
    # ===============================================

    embed = discord.Embed(
        title="🔥 SALA CRIADA",
        color=discord.Color.green()
    )

    embed.add_field(
        name="🎮 Modalidade",
        value=modalidade,
        inline=True
    )

    embed.add_field(
        name="💰 Valor",
        value=f"R${valor}",
        inline=True
    )

    embed.add_field(
        name="👤 Jogador",
        value=interaction.user.mention,
        inline=False
    )

    embed.set_footer(
        text="Boa sorte!"
    )

    await canal.send(embed=embed)

    # ===============================================
    # RESPOSTA
    # ===============================================

    await interaction.response.send_message(
        f"✅ Sala criada: {canal.mention}",
        ephemeral=True
    )

# ==================================================
# SLASH COMMAND
# ==================================================

@bot.tree.command(
    name="painel",
    description="Enviar painel de apostas"
)
async def painel(
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="🎮 PAINEL FREE FIRE",
        description=(
            "Escolha uma modalidade:"
        ),
        color=discord.Color.orange()
    )

    embed.add_field(
        name="⚔️ Modalidades",
        value=(
            "🎮 1x1 → R$5\n"
            "🔥 2x2 → R$10\n"
            "🏆 4x4 → R$20"
        ),
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        view=PainelSalas()
    )

# ==================================================
# READY
# ==================================================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"BOT ONLINE: {bot.user}")
    print("=" * 50)

    # Mantém botões ativos
    bot.add_view(PainelSalas())

    # Sincroniza comandos slash
    await bot.tree.sync()

    print("Slash commands sincronizados!")

# ==================================================
# INICIAR BOT
# ==================================================

bot.run(TOKEN)