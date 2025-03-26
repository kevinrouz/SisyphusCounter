from .database import get_guild_config

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