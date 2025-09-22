import asyncio
import re
from utils.database import get_guild_config, save_guild_config
from utils.expression import safe_numexpr_eval

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

def get_random_string(string_list):
    import random
    return random.choice(string_list)

# Message Counting Logic
state_lock = asyncio.Lock()

async def handle_message(message, bot):
    if message.author.bot or message.guild is None:
        return

    guild_id = str(message.guild.id)
    guild_config = await get_guild_config(guild_id)

    if not guild_config or message.channel.id != guild_config.get("channel_id"):
        return

    if message.attachments or message.embeds:
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
            # Remove zero-width spaces and other invisible characters
            expression = re.sub(r'[\u200B-\u200E\uFEFF]', '', expression)
            # Remove markdown bold formatting
            expression = expression.replace('**', '')
        
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
                            elif str(number).endswith("67"):
                                await message.add_reaction("🤷‍♂️")

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
