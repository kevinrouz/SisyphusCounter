import discord
from discord.ext import commands
from utils.database import get_guild_config, save_guild_config
from utils.permissions import is_operator

class OperatorCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setoperator")
    async def setoperator(self, ctx, new_operator: discord.Member = None):
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

    @commands.command(name="removeoperator")
    async def removeoperator(self, ctx, remove_operator_id: int = None):
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
            user = await self.bot.fetch_user(int(remove_operator_id))
            user_name = user.name
        except:
            user_name = f"User {remove_operator_id}"

        await ctx.reply(f"As you wish, *{user_name}* is gone :nerd: :point_up:") 