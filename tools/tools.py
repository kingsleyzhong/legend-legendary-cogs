import discord
from redbot.core import commands, Config, checks
from discord.ext import tasks
from datetime import datetime

class Tools(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2555525)
        default_global = {"countdowns" : {}}
        self.config.register_global(**default_global)
        self.updater.start()
        
    def cog_unload(self):
        self.updater.stop()

    def convertToLeft(self, sec):
        if sec > 3600:
            return f"{int(sec/3600)} hours {int((sec%3600)/60)} minutes"
        elif sec > 60:
            return f"{int(sec/60)} minutes {int(sec%60)} seconds"
        else:
            return f"{sec} seconds"

    @tasks.loop(seconds=60.0)
    async def updater(self):
        countdowns = await self.config.countdowns()
        for m in countdowns.keys():
            chan = self.bot.get_channel(countdowns[m]["channel"])
            msg = await chan.fetch_message(m)
            seconds = countdowns[m]["left"]-60
            if seconds < 0:
                await self.config.countdowns.clear_raw(m)
                await msg.edit(embed=discord.Embed(description="Countdown ended!", colour=discord.Colour.red()))
            else:
                await msg.edit(embed=discord.Embed(description=f"Time left: {self.convertToLeft(seconds)}", colour=discord.Colour.blue()))
                await self.config.countdowns.set_raw(m, "left", value=seconds)
    
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

        countdownMessage = await ctx.send(embed=discord.Embed(description=f"Time left: {self.convertToLeft(seconds)}", colour=discord.Colour.blue()))

        await self.config.countdowns.set_raw(countdownMessage.id, value={"left" : seconds, "channel" : ctx.channel.id})
        await ctx.message.delete(delay=10)
        
    @commands.command()
    async def postjob(self, ctx):
        author = ctx.author
        intro = await ctx.send("Please head over to a DM with me to answer some questions.")
        await ctx.message.delete(delay=10)
        await intro.delete(delay=10)
        
        def check(msg):
            return msg.channel == author.dm_channel
        
        await author.send("Job posting/position opening:")
        job = (await client.wait_for('message', check=check)).content
        await author.send("Completion deadline:")
        deadline = (await client.wait_for('message', check=check)).content
        await author.send("Availability:")
        availability = (await client.wait_for('message', check=check)).content
        await author.send("How to contact:")
        contact = (await client.wait_for('message', check=check)).content
        await author.send("Job description:")
        jobdesc = (await client.wait_for('message', check=check)).content
        
        embed=discord.Embed(colour=discord.Colour.green())
        embed.add_field(name=job, value="\u200b")
        embed.add_field(name="Posted by:", value=f"{author.mention} ({author.top_role})")
        embed.add_field(name="Date:", value=datetime.now().strftime('%d %b %Y'))
        embed.add_field(name="Completion deadline:", value=deadline)
        embed.add_field(name="Availability:", value=availability)
        embed.add_field(name="How to contact:", value=contact)
        embed.add_field(name="Job description:", value=jobdesc)
        
        jobChannel = self.bot.get_channel(599320984675156020)
        await jobChannel.send(embed=embed)
        
        
        
        
        

