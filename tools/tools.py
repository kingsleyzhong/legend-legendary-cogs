import discord
from redbot.core import commands, Config, checks

class Tools(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2555525)
        default_global = {"countdowns" : {}}
        self.config.register_global(**default_global)

    def convertToLeft(self, sec):
        if sec > 3600:
            return f"{sec/3600} hours"
        elif sec > 60:
            return f"{sec/60} minutes"
        else:
            return f"{sec} seconds"

        
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
            seconds = timeunit
        elif timeunit == "m":
            seconds = timeunit * 60
        elif timeunit == "h":
            seconds = timeunit * 3600

        countdownMessage = await ctx.send(embed=discord.Embed(description=self.convertToLeft(seconds)))

        await self.config.global.countdowns.set_raw(
                ctx.guild.id, ctx.channel.id : {countdownMessage.id : seconds}
            )

