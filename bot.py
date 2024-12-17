import discord
import sys
import random
from discord.ext import commands
import json
import os
import asyncio
import subprocess 

try:
    import dotenv
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    import dotenv 

dotenv.load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=["sisyphus ", "Sisyphus ", "Sis ", "sis "], intents=intents)

GAME_DATA_FILE = "game_data.json"

fail_messages = [
    "Intelligence is chasing you, but you are faster.",
    "Wisdom is not a flower that blooms in every garden.",
    "Can you count how many letters are in L-O-S-E-R?",
    "Do you hate me? Why are you doing this to me?",
    "Ah. You must be a business major the way you can't count.",
    "YOU NEED TO LEAVE!",
    "I should ban you for that.",
    "Here you go, it's a dunce cap. 🎩",
    "You nincompoop.",
    "Yeah so I'm going to stop you right there actually.",
    "Pack it up buddy.",
    "First name Stu, last name Pid.",
    "IM GONNA GO INSANE IM GONNA GO INSANE GET THE VOICES OUT OF MY HEAD!!!!",
    "Thanks for bringing down the average IQ. Now I appear smarter.",
    "The lights are on, but nobody's home.",
    "You are proof that evolution can reverse itself.",
    "Truly a scholar in the art of poor judgement.",
    "I trusted you with all my heart, and you broke it.",
    "Well now we know who's NOT smarter than a 5th grader.",
    "I wanted to believe in you... I was naive...",
    "Oh... you're doing great sweetheart...",
    "Can you count how many ways I dislike you right now?",
    "Are you sure you're not competing for 'most confused'?",
    "Well at least you're consistent... consistently wrong.",
    "I can't tell if you're intentionally slow or just naturally gifted at it.",
    "It's not that you're wrong, it's that you're not even close.",
    "It takes REAL talent to be this oblivious.",
    "Ladies and gentlemen, in this exhibit we have an example of a Sapien that didn't develop critical thinking.",
    "I hope you step in a puddle with socks on.",
    "I hope you wash your hands and get your long sleeves wet."
    "I hope you get an itch where you can't reach."
]

config = {"servers":{}}

def get_random_string(string_list):
    return random.choice(string_list)

def load_game_data():
    global config
    if os.path.exists(GAME_DATA_FILE):
        with open(GAME_DATA_FILE, "r") as f:
            config = json.load(f)
    else:
        config = {"servers": {}}

def save_game_data():
    with open(GAME_DATA_FILE, "w") as f:
        json.dump(config, f, indent=4)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    load_game_data()

state_lock = asyncio.Lock()

@bot.listen('on_message')
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    guild_id = str(message.guild.id)
    guild_config = config["servers"].get(guild_id)

    if not guild_config or message.channel.id != guild_config.get("channel_id"):
        return

    async with state_lock:
        expected_number = guild_config.get("expected_number", 1)
        last_user_name = guild_config.get("last_user_name", None)
        record_number = guild_config.get("record_number", 1)
        record_holder = guild_config.get("record_holder", None)

        try:
            parts = message.content.split(' ', 1)
            
            if any(char.isalpha() for char in parts[0]):
                return
            
            number = eval(parts[0])

            if isinstance(number, (int, float)):
                if number == expected_number:
                    if message.author.name == last_user_name:
                        await message.reply(
                            f"{message.author.mention} {get_random_string(fail_messages)} **You can't count twice in a row. Now you have to restart from 1.**"
                        )
                        await message.add_reaction("❌")
                        config["servers"][guild_id]["expected_number"] = 1
                        config["servers"][guild_id]["last_user_name"] = None
                    else:
                        username = message.author.name
                        if "scores" not in guild_config:
                            guild_config["scores"] = {}

                        if username not in guild_config["scores"]:
                            guild_config["scores"][username] = 0

                        guild_config["scores"][username] += 1

                        if number == 100:
                            await message.add_reaction("💯")
                        else:
                            await message.add_reaction("✅")
                            
                        if number > record_number:
                            guild_config["record_number"] = number
                            guild_config["record_holder"] = message.author.name

                        config["servers"][guild_id]["expected_number"] += 1
                        config["servers"][guild_id]["last_user_name"] = message.author.name
                        
                else:
                    await message.reply(
                        f"{message.author.mention} {get_random_string(fail_messages)} You ruined it at **{expected_number}**. **Now you have to restart from 1.**"
                    )
                    await message.add_reaction("❌")
                    config["servers"][guild_id]["expected_number"] = 1
                    config["servers"][guild_id]["last_user_name"] = None

                save_game_data()

        except (ValueError, SyntaxError):
            pass


@bot.command(name="set_channel")
async def set_channel(ctx):
    print("hi")
    guild_id = str(ctx.guild.id)

    if "servers" not in config:
        config["servers"] = {}

    config["servers"][guild_id] = {
        "channel_id": ctx.channel.id,
        "expected_number": 1,
        "last_user": None,
    }
    save_game_data()

    await ctx.send(f"Counting game channel has been set to {ctx.channel.mention}.")
    
@bot.command(name="leaderboard", aliases=["leader", "l"])
async def leaderboard(ctx):
    guild_id = str(ctx.guild.id)

    if guild_id not in config["servers"] or "scores" not in config["servers"][guild_id]:
        await ctx.reply("Nobody's even started counting yet, wym?")
        return

    scores = config["servers"][guild_id]["scores"]

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]

    embed = discord.Embed(
        title="🏆 Leaderboard 🏆",
        description="Top 10 players ranked by score:",
        color=discord.Color.gold()
    )

    for rank, (username, score) in enumerate(sorted_scores, start=1):
        embed.add_field(
            name=f"**#{rank}** {username}",
            value=f"**Score:** {score}",
            inline=False 
        )

    await ctx.reply(embed=embed)
    
@bot.command(name="next", aliases=["number", "num", "n"])
async def next(ctx): 
    guild_id = str(ctx.guild.id)  
    
    if guild_id not in config["servers"]:
        await ctx.reply("This server is not set up for counting yet.")
        return
    
    await ctx.reply(f"The next number is **{config["servers"][guild_id]["expected_number"]}**.")
    
@bot.command(name="commands")
async def help_command(ctx):
    user = "<@516674441053470759>"
    
    embed = discord.Embed(
        title="Help - Sisyphus Counter",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="leaderboard (aliases: sis leader, sis l)",
        value="Displays the leaderboard of top 10 players by score.\n**Example usage:** `sis leaderboard`",
        inline=False
    )
    embed.add_field(
        name="next (aliases: sis number, sis num, sis n)",
        value="Shows the next number in the game.\n**Example usage:** `sis next`",
        inline=False
    )
    embed.add_field(
        name="commands",
        value="Displays this help message.\n**Example usage:** `sis commands`",
        inline=False
    )
    embed.add_field(
        name="record (alias: sis r)",
        value="Displays the current high score.\n**Example usage:** `sis r`",
        inline=False
    )

    embed.add_field(
        name="Created by Kevin Farokhrouz :bat:",
        value=f"Feel free to reach out ({user}) if you have any questions!",
        inline=False
    )

    await ctx.reply(embed=embed)
    
@bot.command(name="record", aliases=["r"])
async def record(ctx):
    guild_id = str(ctx.guild.id)

    if guild_id not in config["servers"]:
        await ctx.reply("This server is not set up for counting yet.")
        return

    record_number = config["servers"][guild_id].get("record_number", 1)
    record_holder = config["servers"][guild_id].get("record_holder", "No one yet")
    
    await ctx.reply(f"The current record number is **{record_number}** set by **{record_holder}**.")

@bot.command(name="setnum")
async def setnum(ctx, new_number: int):
    if str(ctx.author.id) != "516674441053470759":
        await ctx.reply("Lol sike u thought :nerd:")
        return

    guild_id = str(ctx.guild.id)

    if guild_id not in config["servers"]:
        await ctx.reply("This server is not set up for counting yet.")
        return

    config["servers"][guild_id]["expected_number"] = new_number
    save_game_data()

    await ctx.reply(f"As you wish, my glorious king. I have set the number to **{new_number}**.")

bot.run(
   bot_token
)
