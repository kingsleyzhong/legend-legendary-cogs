import discord
from redbot.core import commands, Config, checks
import clashroyale

class ClashRoyale(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2512325)
        default_user = {"tag" : None}
        self.config.register_user(**default_user)

    @commands.command()
    async def save(self, ctx, tag):
        tag = await self.config.user(ctx.author).tag
        await ctx.send(tag)

    @commands.command()
    async def get(self, ctx):
        tag = await self.config.user(ctx.author).tag()
        await ctx.send(tag)