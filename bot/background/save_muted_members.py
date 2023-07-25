import asyncio

from bot import LOGGER
from bot.utils.database import Muted

async def save_muted_members(bot):
    LOGGER.info("Save_muted_members start")
    while True:
        muted = Muted()
        muted.open()
        target_guilds = muted.get_all_guild_id()

        data = {}
        if target_guilds != []:
            for guild in target_guilds:
                guild_id = guild[0]
                role_id = guild[2]

                data[guild_id] = []

                guild = bot.get_guild(guild_id)
                role = guild.get_role(role_id)

                if role is not None:
                    members = role.members
                    for member in members:
                        data[guild_id].append(member.id)

            muted.set_database(data)
            muted.close()

        await asyncio.sleep(60)