import discord
import random
from discord.ext import commands
import os
import asyncio
import dotenv
import numexpr
import re
import signal
from motor.motor_asyncio import AsyncIOMotorClient

dotenv.load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
mongo_uri = os.getenv("MONGO_URI")

# ============================================================================
#                               CONFIGURATIONS
# ============================================================================

# Bot Configuration
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=["sisyphus ", "Sisyphus ", "Sis ", "sis "], intents=intents)

# MongoDB setup
mongo_client = AsyncIOMotorClient(mongo_uri)
db = mongo_client.sisyphus_bot
servers_collection = db.servers

# Default configurations
config = {"servers": {}}

# List of fail messages
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
    "I hope you wash your hands and get your long sleeves wet.",
    "I hope you get an itch where you can't reach."
]

# ============================================================================
#                               HELPER FUNCTIONS
# ============================================================================

def get_random_string(string_list):
    return random.choice(string_list)

async def get_guild_config(guild_id: str):
    guild_config = await servers_collection.find_one({"_id": guild_id})
    if not guild_config:
        guild_config = {"_id": guild_id}
    return guild_config

async def save_guild_config(guild_id: str, guild_config: dict):
    # Wait for the operation to complete and get the result
    result = await servers_collection.replace_one(
        {"_id": guild_id},
        guild_config,
        upsert=True
    )
    
    if not result.acknowledged:
        print(f"Warning: Database update for guild {guild_id} was not acknowledged")
    
    return result

def timeout_handler(signum, frame):
    raise TimeoutException("Calculation timed out")

def safe_numexpr_eval(expression, timeout=1):
    """
    Safely evaluates a simple arithmetic expression using numexpr,
    with strict input sanitization (no parentheses or decimals) and a timeout
    to prevent denial-of-service.
    """
    # Replace every ^ with **
    expression = expression.replace("^", "**")
    
    # Sanitize input using a regular expression to allow only digits,
    # basic arithmetic operators (+, -, *, /, **), and spaces
    if not re.match(r"^[\d+\-*/\s]+$", expression):
        return None

    try:
        # Set up a timeout handler to prevent long calculations
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        # Evaluate the expression using numexpr.evaluate()
        result = numexpr.evaluate(expression)

        # Clear the alarm after a successful result
        signal.alarm(0)

        return result.item()

    except (TypeError, ZeroDivisionError, NameError, SyntaxError) as e:
        print(f"Error evaluating expression: {e}")
        return None
    except TimeoutException:
        print("Calculation timed out!")
        return None
    finally:
        signal.alarm(0)

async def is_operator(ctx) -> bool:
    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    operators = guild_config.get("operators", [])
    return str(ctx.author.id) == "516674441053470759" or str(ctx.author.id) in operators or ctx.author.id == ctx.guild.owner_id

async def is_admin(ctx) -> bool:
    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    admins = guild_config.get("admins", [])
    operators = guild_config.get("operators", [])
    return str(ctx.author.id) in admins or str(ctx.author.id) in operators or str(ctx.author.id) == "516674441053470759" or ctx.author.id == ctx.guild.owner_id

# ============================================================================
#                               BOT EVENTS
# ============================================================================

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

# --- Message Counting Logic ---
state_lock = asyncio.Lock()

@bot.listen('on_message')
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    guild_id = str(message.guild.id)
    guild_config = await get_guild_config(guild_id)

    if not guild_config or message.channel.id != guild_config.get("channel_id"):
        return

    async with state_lock:
        
        guild_config = await get_guild_config(guild_id)
        if not guild_config or message.channel.id != guild_config.get("channel_id"):
            return
        
        expected_number = guild_config.get("expected_number", 1)
        last_user_name = guild_config.get("last_user_name", None)
        record_number = guild_config.get("record_number", 1)

        try:
            parts = message.content.split(' ', 1)
            expression = parts[0]
            expression = expression.lstrip('0')
            
            if not expression:
                number = 0
            else:
                number = safe_numexpr_eval(expression)

            if isinstance(number, (int, float)):
                # Check if user is banned
                banned_users = guild_config.get("banned_users", [])
                if str(message.author.id) in banned_users:
                    await message.add_reaction("😹")
                    return  # Ignore further processing for this message
                elif number == expected_number:
                    if message.author.name == last_user_name:
                        await message.reply(
                            f"{message.author.mention} {get_random_string(fail_messages)} **You can't count twice in a row. Now you have to restart from 1.**"
                        )
                        await message.add_reaction("❌")
                        guild_config["expected_number"] = 1
                        guild_config["last_user_name"] = None
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
                            if str(number).endswith("69"):
                                await asyncio.gather(
                                    message.add_reaction("🇳"),
                                    message.add_reaction("🇮"),
                                    message.add_reaction("🇨"),
                                    message.add_reaction("🇪")
                                )

                        if number > record_number:
                            guild_config["record_number"] = number
                            guild_config["record_holder"] = message.author.name

                        guild_config["expected_number"] = expected_number + 1
                        guild_config["last_user_name"] = message.author.name

                else:
                    await message.reply(
                        f"{message.author.mention} {get_random_string(fail_messages)} You ruined it at **{expected_number}**. **Now you have to restart from 1.**"
                    )
                    await message.add_reaction("❌")
                    guild_config["expected_number"] = 1
                    guild_config["last_user_name"] = None

                await save_guild_config(guild_id, guild_config)

        except (ValueError, SyntaxError):
            pass

# ============================================================================
#                               BOT COMMANDS
# ============================================================================

@bot.command(name="set_channel")
async def set_channel(ctx):
    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    
    guild_config["channel_id"] = ctx.channel.id
    guild_config["expected_number"] = 1
    guild_config["last_user"] = None
    
    await save_guild_config(guild_id, guild_config)
    await ctx.send(f"Counting game channel has been set to {ctx.channel.mention}.")

@bot.command(name="leaderboard", aliases=["leader", "l"])
async def leaderboard(ctx):
    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)

    if "scores" not in guild_config:
        await ctx.reply("Nobody's even started counting yet, wym?")
        return

    scores = guild_config["scores"]
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
    guild_config = await get_guild_config(guild_id)

    if "channel_id" not in guild_config:
        await ctx.reply("This server is not set up for counting yet.")
        return

    await ctx.reply(f"The next number is **{guild_config['expected_number']}**.")

@bot.command(name="commands")
async def help_command(ctx):
    """Displays the help message with available commands."""
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

    if is_admin(ctx):
        embed.add_field(
            name="Admin Commands",
            value="These commands are only available to admins.",
            inline=False
        )
        embed.add_field(
            name="setnum",
            value="Sets the expected number in the game.\n**Example usage:** `sis setnum 42`",
            inline=False
        )
        embed.add_field(
            name="setadmin",
            value="Grants admin privileges to a user.\n**Example usage:** `sis setadmin @username`",
            inline=False
        )
        embed.add_field(
            name="removeadmin",
            value="Removes admin privileges from a user.\n**Example usage:** `sis removeadmin user_id`",
            inline=False
        )
        embed.add_field(
            name="ban",
            value="Removes counting privileges from a user.\n**Example usage:** `sis ban @username`",
            inline=False
        )
        embed.add_field(
            name="unban",
            value="Restores counting privileges to a user.\n**Example usage:** `sis unban @username`",
            inline=False
        )

    if is_operator(ctx):
        embed.add_field(
            name="Operator Commands",
            value="These commands are only available to operators.",
            inline=False
        )
        embed.add_field(
            name="setoperator",
            value="Grants operator privileges to a user.\n**Example usage:** `sis setoperator @username`",
            inline=False
        )
        embed.add_field(
            name="removeoperator",
            value="Removes operator privileges from a user.\n**Example usage:** `sis removeoperator user_id`",
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
    guild_config = await get_guild_config(guild_id)

    record_number = guild_config.get("record_number", 1)
    record_holder = guild_config.get("record_holder", "No one yet")

    await ctx.reply(f"The current record number is **{record_number}** set by **{record_holder}**.")

# ============================================================================
#                               ADMIN COMMANDS
# ============================================================================

@bot.command(name="setnum")
async def setnum(ctx, new_number: int):
    if not await is_admin(ctx):
        await ctx.reply("Lol sike u thought :nerd:")
        return

    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    
    guild_config["expected_number"] = new_number
    await save_guild_config(guild_id, guild_config)

    await ctx.reply(f"As you wish, my glorious king. I have set the number to **{new_number}**.")

@bot.command(name="setadmin")
async def setadmin(ctx, new_admin: discord.Member = None):
    if not new_admin:
        await ctx.reply("...are you gonna tell me who? `sis setadmin @username`")
        return

    if not await is_admin(ctx):
        await ctx.reply("Bro who are you? :sob:")
        return

    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    
    admins = guild_config.setdefault("admins", [])

    if str(new_admin.id) in admins:
        await ctx.reply(f"Lock in bruh ... {new_admin.mention} has already been granted admin. :man_facepalming: ")
        return

    admins.append(str(new_admin.id))
    await save_guild_config(guild_id, guild_config)
    await ctx.reply(f"A new torch has been lit. Welcome to the elites, {new_admin.mention}. :palm_up_hand: :candle:")

@bot.command(name="setoperator")
async def setoperator(ctx, new_operator: discord.Member = None):
    if not new_operator:
        await ctx.reply("...are you gonna tell me who? `sis setoperator @username`")
        return

    if not await is_operator(ctx):
        await ctx.reply("Bro who are you? :sob:")
        return

    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    
    operators = guild_config.setdefault("operators", [])

    if str(new_operator.id) in operators:
        await ctx.reply(f"Lock in bruh ... {new_operator.mention} has already been granted operator. :man_facepalming: ")
        return

    operators.append(str(new_operator.id))
    await save_guild_config(guild_id, guild_config)
    await ctx.reply(f"A new torch has been lit. Welcome to the elites, {new_operator.mention}. :palm_up_hand: :candle:")

@bot.command(name="removeadmin")
async def removeadmin(ctx, remove_admin_id: int = None):
    if remove_admin_id is None:
        await ctx.reply("...Are you gonna tell me who? :sob: `sis removeadmin user_id`")
        return

    if not await is_admin(ctx):
        await ctx.reply("Bro who are you? :sob:")
        return

    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    
    operators = guild_config.setdefault("operators", [])
    admins = guild_config.setdefault("admins", [])
    remove_admin_id = str(remove_admin_id)

    if remove_admin_id not in admins:
        await ctx.reply(f"Nah. User *{remove_admin_id}* ain't an admin bozo.")
        return

    admins.remove(remove_admin_id)
    if remove_admin_id in operators:
        operators.remove(remove_admin_id)
    await save_guild_config(guild_id, guild_config)

    try:
        user = await bot.fetch_user(int(remove_admin_id))
        user_name = user.name
    except:
        user_name = f"User {remove_admin_id}"  # Fallback if the user can't be found

    await ctx.reply(f"As you wish, *{user_name}* is gone :nerd: :point_up:")

@bot.command(name="removeoperator")
async def removeoperator(ctx, remove_operator_id: int = None):
    if remove_operator_id is None:
        await ctx.reply("...Are you gonna tell me who? `sis removeoperator user_id`")
        return

    if not await is_operator(ctx):
        await ctx.reply("Bro who are you? :sob:")
        return

    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    
    operators = guild_config.setdefault("operators", [])
    admins = guild_config.setdefault("admins", [])
    remove_operator_id = str(remove_operator_id)

    if remove_operator_id not in operators:
        await ctx.reply(f"Nah. User *{remove_operator_id}* ain't an operator bozo.")
        return

    operators.remove(remove_operator_id)
    if remove_operator_id in admins:
        admins.remove(remove_operator_id)
    await save_guild_config(guild_id, guild_config)

    try:
        user = await bot.fetch_user(int(remove_operator_id))
        user_name = user.name
    except:
        user_name = f"User {remove_operator_id}"

    await ctx.reply(f"As you wish, *{user_name}* is gone :nerd: :point_up:")
    
@bot.command(name="ban")
async def ban(ctx, member: discord.Member = None):
    if not await is_admin(ctx) and not await is_operator(ctx):
        await ctx.reply("Bro who are you? :sob:")
        return

    if member is None:
        await ctx.reply("...are you gonna tell me who? `sis ban @username`")
        return

    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    
    banned_users = guild_config.setdefault("banned_users", [])

    if str(member.id) in banned_users:
        await ctx.reply(f"Lock in bruh ... {member.mention} is already banned. :man_facepalming:")
        return

    banned_users.append(str(member.id))
    await save_guild_config(guild_id, guild_config)
    await ctx.reply(f"No more counting for {member.mention}... #L #Bozo #Ratio :no_entry_sign:")
    
@bot.command(name="unban")
async def unban(ctx, member: discord.Member = None):
    if not await is_admin(ctx) and not await is_operator(ctx):
        await ctx.reply("Bro who are you? :sob:")
        return

    if member is None:
        await ctx.reply("...are you gonna tell me who? `sis unban @username`")
        return

    guild_id = str(ctx.guild.id)
    guild_config = await get_guild_config(guild_id)
    
    banned_users = guild_config.setdefault("banned_users", [])

    if str(member.id) not in banned_users:
        await ctx.reply(f"Nah. {member.mention} ain't even banned bozo.")
        return

    banned_users.remove(str(member.id))
    await save_guild_config(guild_id, guild_config)
    await ctx.reply(f"Alright I'll let {member.mention} count... DON'T test my patience though... :white_check_mark:")

# ============================================================================
#                               BOT STARTUP
# ============================================================================

bot.run(bot_token)