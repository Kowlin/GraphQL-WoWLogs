from redbot.core.bot import Red

from .core import WoWLogs


async def setup(bot: Red) -> None:
    cog = WoWLogs(bot)
    await cog._create_client()
    bot.add_cog(cog)
