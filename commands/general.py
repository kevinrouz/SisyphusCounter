import discord
from discord.ext import commands
from utils.database import get_guild_config, save_guild_config
from utils.permissions import is_admin, is_operator

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_channel")
    async def set_channel(self, ctx):
        guild_id = str(ctx.guild.id)
        guild_config = await get_guild_config(guild_id)
        
        guild_config["channel_id"] = ctx.channel.id
        guild_config["expected_number"] = 1
        guild_config["last_user"] = None
        
        await save_guild_config(guild_id, guild_config)
        await ctx.send(f"Counting game channel has been set to {ctx.channel.mention}.")

    @commands.command(name="leaderboard", aliases=["leader", "l"])
    async def leaderboard(self, ctx):
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

    @commands.command(name="next", aliases=["number", "num", "n"])
    async def next(self, ctx):
        guild_id = str(ctx.guild.id)
        guild_config = await get_guild_config(guild_id)

        if "channel_id" not in guild_config:
            await ctx.reply("This server is not set up for counting yet.")
            return

        await ctx.reply(f"The next number is **{guild_config['expected_number']}**.")

    @commands.command(name="commands")
    async def help_command(self, ctx):
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

        if await is_admin(ctx):
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

        if await is_operator(ctx):
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

    @commands.command(name="record", aliases=["r"])
    async def record(self, ctx):
        guild_id = str(ctx.guild.id)
        guild_config = await get_guild_config(guild_id)

        record_number = guild_config.get("record_number", 1)
        record_holder = guild_config.get("record_holder", "No one yet")

        await ctx.reply(f"The current record number is **{record_number}** set by **{record_holder}**.") 