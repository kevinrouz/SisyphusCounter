import discord
from discord.ext import commands
from utils.database import get_guild_config, save_guild_config
from utils.permissions import is_admin, is_operator

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setnum")
    async def setnum(self, ctx, new_number: int):
        if not await is_admin(ctx):
            await ctx.reply("Lol sike u thought :nerd:")
            return

        guild_id = str(ctx.guild.id)
        guild_config = await get_guild_config(guild_id)
        
        guild_config["expected_number"] = new_number
        await save_guild_config(guild_id, guild_config)

        await ctx.reply(f"As you wish, my glorious king. I have set the number to **{new_number}**.")

    @commands.command(name="setadmin")
    async def setadmin(self, ctx, new_admin: discord.Member = None):
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

    @commands.command(name="removeadmin")
    async def removeadmin(self, ctx, remove_admin_id: int = None):
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
            user = await self.bot.fetch_user(int(remove_admin_id))
            user_name = user.name
        except:
            user_name = f"User {remove_admin_id}"  # Fallback if the user can't be found

        await ctx.reply(f"As you wish, *{user_name}* is gone :nerd: :point_up:")

    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member = None):
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
        
    @commands.command(name="unban")
    async def unban(self, ctx, member: discord.Member = None):
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