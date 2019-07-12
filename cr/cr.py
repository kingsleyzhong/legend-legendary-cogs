import discord
from redbot.core import commands, Config, checks
import clashroyale
import os

class ClashRoyaleCog(commands.Cog):
    
    async def initialize(self):
        apikey = await self.bot.db.api_tokens.get_raw("crapi", default={"api_key": None})
        if apikey is None:
            raise ValueError("The Clash Royake API key has not been set. Use [p]set api crapi api_key,YOURAPIKEY")
        self.crapi = clashroyale.OfficialAPI(apikey, is_async=True)
    
    def __init__(self, bot, apikey):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2512325)
        default_user = {"tag" : None}
        self.config.register_user(**default_user)
        
    def badEmbed(self, text):
        bembed = discord.Embed(color=0xff0000)
        bembed.set_author(name=text, icon_url="https://i.imgur.com/FcFoynt.png")
        return bembed
        
    def goodEmbed(self, text):
        gembed = discord.Embed(color=0x45cafc)
        gembed.set_author(name=text, icon_url="https://i.imgur.com/qYmbGK6.png")
        return gembed        

    @commands.command()
    async def save(self, ctx, tag, member: discord.Member = None):
        """Save your Clash Royale player tag"""
        if member == None:
            member = ctx.author        
        
        tag = tag.lower().replace('O', '0')
        if tag.startswith("#"):
            tag = tag.strip('#')

        try:
            player = await self.crapi.get_player("#" + tag)
            await self.config.user(ctx.author).tag.set(tag)
            await ctx.send(embed = self.goodEmbed("CR account {} was saved to {}".format(player.name, member.name)))
            
        except clashroyale.NotFoundError as e:
            await ctx.send(embed = self.badEmbed("No player with this tag found, try again!"))

        except clashroyale.RequestError as e:
            await ctx.send(embed = self.badEmbed(f"CR API is offline, please try again later! ({str(e)})"))
        
        except Exception as e:
            await ctx.send(embed = self.badEmbed("Something went wrong, this is unusual and shouldn't happen. Please message the bot to report this error."))

    @commands.command()
    async def get(self, ctx):
        tag = await self.config.user(ctx.author).tag()
        await ctx.send(tag)
