import discord
import aiohttp
import logging

from redbot.core import checks, commands, Config
from redbot.core.bot import Red

from typing import Optional, Mapping
from datetime import datetime

from .http import WoWLogsClient, generate_bearer

log = logging.getLogger("red.wowlogs.core")


class WoWLogs(commands.Cog):

    def __init__(self, bot):
        self.bot: Red = bot
        self.config = Config.get_conf(self, identifier=25360018)
        self.http: WoWLogsClient = None
        # Currently doesn't reload the client on an API change... if you want that, just take it from GHC.

        self.config.register_global(
            bearer_timestamp=0
        )

    async def _create_client(self) -> None:
        self.http = WoWLogsClient(bearer=await self._get_bearer())
        bearer_status = await self.http.check_bearer()
        if bearer_status is False:
            await generate_bearer(self.bot, self.config)
            await self.http.recreate_session(await self._get_bearer())

    async def _get_bearer(self) -> str:
        api_tokens = await self.bot.get_shared_api_tokens("wowlogs")
        bearer = api_tokens.get("bearer", "")

        bearer_timestamp = await self.config.bearer_timestamp()
        timestamp_now = int(datetime.utcnow().timestamp())

        if timestamp_now > bearer_timestamp:
            log.info("Bearer token has expired. Generating one")
            bearer = await generate_bearer(self.bot, self.config)
        elif not bearer:
            log.info("Bearer token doesn't exist. Generating one")
            bearer = await generate_bearer(self.bot, self.config)

        if bearer is None:
            return
        return bearer

    def cog_unload(self) -> None:
        self.bot.loop.create_task(self.http.session.close())

    async def red_get_data_for_user(self, **kwargs):
        return {}

    async def red_delete_data_for_user(self, **kwargs):
        return

    @commands.command()
    async def getgear(self, ctx, server: str, realm: str, *, name: str):
        """Get the gear from an charachter. This is capital sensative."""

        # Get the user's last raid encounters
        encounters = await self.http.get_last_encounter(name, realm, server)

        if encounters is False:
            # the user wasn't found on the API.
            return await ctx.send(f"{name} wasn't found on the API.")

        # Continue to fetch the last encounter of an user
        char_data = await self.http.get_gear(name, realm, server, encounters["latest"])
        gear = None

        if char_data is None:
            # Assuming bearer has been invalidated.
            await self._create_client()

        if len(char_data["encounterRankings"]["ranks"]) != 0:
            # Ensure this is the encounter that has gear listed. IF its not, we're moving on with the other encounters.
            gear = char_data["encounterRankings"]["ranks"][0]["gear"]
        else:
            encounters["ids"].remove(encounters["latest"])
            for encounter in encounters["ids"]:
                char_data = await self.http.get_gear(name, realm, server, encounter)
                if len(char_data["encounterRankings"]["ranks"]) != 0:
                    gear = char_data["encounterRankings"]["ranks"][0]["gear"]
                    break

        if gear is None:
            return await ctx.send(f"No gear for {name} found in the last report.")

        item_list = []
        for item in gear:
            item_list.append(f"[{item['name']}](https://classic.wowhead.com/item={item['id']})")

        item_string = "\n".join(item_list)
        embed = discord.Embed()
        embed.description = f"Items for {name}\n\n{item_string}"
        await ctx.send(embed=embed)
