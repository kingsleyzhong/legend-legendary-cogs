import discord
from redbot.core import commands, Config, checks
from discord.ext import tasks

class Tools(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2555525)
        default_global = {"countdowns" : {}}
        self.config.register_global(**default_global)
        self.updater.start()

    def convertToLeft(self, sec):
        if sec > 3600:
            return f"{sec/3600} hours"
        elif sec > 60:
            return f"{sec/60} minutes"
        else:
            return f"{sec} seconds"

    @tasks.loop(seconds=10.0)
    async def updater(self):
        countdowns = self.config.countdowns()
        for m in countdowns.keys():
            msg = await self.bot.fetch_message(m)
            seconds = cooldowns["m"]-10
            await msg.edit(embed=discord.Embed(description=self.convertToLeft(seconds), colour=discord.Colour.blue()))
            await self.config.set_raw(m, value=seconds)
    
    @updater.before_loop
    async def before_updater(self):
        await self.bot.wait_until_ready()
        
    @commands.command()
    async def countdown(self, ctx, amount : int, timeunit : str):
        """
        Start a countdown
        /countdown 1 h
        Accepted time units - s, m, h
        """
        
        if timeunit not in ["s", "m", "h", "seconds", "minutes", "hours", ]:
            return await ctx.send("Invalid time unit! Use \"s\", \"m\" or \"h\".")

        seconds = 0

        if timeunit == "s":
            seconds = amount
        elif timeunit == "m":
            seconds = amount * 60
        elif timeunit == "h":
            seconds = amount * 3600

        countdownMessage = await ctx.send(embed=discord.Embed(description=self.convertToLeft(seconds), colour=discord.Colour.blue()))

        await self.config.countdowns.set_raw(countdownMessage.id, value=seconds)

