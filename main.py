import os
import discord
from discord.ext import commands
from discord import ui
from aiohttp import web
import asyncio

# Pegar configurações das variáveis de ambiente (Render)
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
CANAL_ID = int(os.environ.get("CANAL_ID"))
PORT = int(os.environ.get("PORT", 8080))

# Configurar bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Botão de desfazer
class DesfazerView(ui.View):
    def __init__(self, treino_id):
        super().__init__(timeout=None)
        self.treino_id = treino_id

    @ui.button(label="Desfazer treino", style=discord.ButtonStyle.danger, emoji="🚫")
    async def desfazer(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(f"⚠️ Treino `{self.treino_id}` revertido!", ephemeral=True)
        button.disabled = True
        await interaction.message.edit(view=self)

@bot.event
async def on_ready():
    print(f"🔥 PHOENIX BOT ONLINE NA NUVEM!")
    await bot.change_presence(activity=discord.Game(name="Exército Brasileiro RP"))

@bot.command(name="teste")
async def teste(ctx):
    await ctx.send("🔥 PHOENIX BOT funcionando perfeitamente!")

# Servidor web para receber dados do site do seu amigo
async def handle_promocao(request):
    try:
        data = await request.json()
        
        tipo = data.get('tipo', 'Geral')
        instrutor = data.get('instrutor', 'Desconhecido')
        imagem_url = data.get('imagem', '')
        treino_id = data.get('id', '000')
        promovidos = data.get('promovidos', [])

        lista_texto = ""
        for p in promovidos:
            lista_texto += f"**{p['nick']}** `{p['atual']}` ➔ `{p['nova']}`\n"

        embed = discord.Embed(
            title=f"🎖️ Promoções do treino de {tipo}",
            description=f"**Instrutor:** {instrutor}\n\n{lista_texto}",
            color=0x2ecc71
        )
        if imagem_url:
            embed.set_image(url=imagem_url)

        canal = bot.get_channel(CANAL_ID)
        if canal:
            view = DesfazerView(treino_id)
            await canal.send(embed=embed, view=view)
            return web.Response(text="OK")
        return web.Response(text="Canal não encontrado", status=404)
    except Exception as e:
        print(f"Erro ao receber dados: {e}")
        return web.Response(text="Erro interno", status=500)

async def main():
    # Inicia o servidor web
    app = web.Application()
    app.router.add_post('/promover', handle_promocao)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"🌐 Servidor web rodando na porta {PORT}")
    
    # Inicia o bot do Discord
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
