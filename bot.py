import discord
from discord.ext import commands
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

# Bot Configuration
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=["sisyphus ", "Sisyphus ", "Sis ", "sis "], intents=intents)

# Import and load cogs
from commands.admin import AdminCommands
from commands.operator import OperatorCommands
from commands.general import GeneralCommands
from events.message_handler import handle_message

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    
    # Load all cogs
    await bot.add_cog(AdminCommands(bot))
    await bot.add_cog(OperatorCommands(bot))
    await bot.add_cog(GeneralCommands(bot))

@bot.listen('on_message')
async def on_message(message):
    await handle_message(message, bot)

# Start the bot
bot.run(bot_token) 