import discord
import asyncio

from discord.ext import commands
from bot.background.read_holo import read_holo
from bot.background.broadcast import broadcast
from bot.background.reset_db import reset_db
from bot.background.read_vroz import read_vroz
from bot.background.broadcast_vroz import broadcast_vroz
from bot.background.save_muted_members import save_muted_members
from bot.utils.database import channelDataDB

from bot import LOGGER, TOKEN, EXTENSIONS, BOT_NAME_TAG_VER

async def status_task():
    while True:
        try:
            await bot.change_presence(
                activity = discord.Game ("/help : 도움말"),
                status = discord.Status.online,
            )
            await asyncio.sleep(10)
            channel_list = channelDataDB().get_on_channel("broadcastChannel")
            if channel_list is not None:
                await bot.change_presence(
                    activity = discord.Game (f"{len(channel_list)}개의 채널에 알림을 보내주고 있어요!"),
                    status = discord.Status.online,
                )
                await asyncio.sleep(10)
        except Exception:
            pass

class Bot (commands.Bot):
    def __init__ (self):
        super().__init__ (
            intents=intents
        )
        self.remove_command("help")

        for i in EXTENSIONS:
            self.load_extension("bot.cogs." + i)

    async def on_ready (self):
        LOGGER.info(BOT_NAME_TAG_VER)
        await self.change_presence(
            activity = discord.Game ("/help : 도움말"),
            status = discord.Status.online,
        )

        while background_list != {}:
            module_name = list(background_list.keys())[0]
            pass_variable = background_list.pop(module_name)

            if pass_variable:
                bot.loop.create_task(globals()[module_name](bot))
            else:
                bot.loop.create_task(globals()[module_name]())

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

background_list = {
    "status_task": False,
    "read_holo": False,
    "broadcast": True,
    "reset_db": False,
    "read_vroz": False,
    "broadcast_vroz": True,
    "save_muted_members": True,
}

intents = discord.Intents().all()

bot = Bot()
bot.run(TOKEN)