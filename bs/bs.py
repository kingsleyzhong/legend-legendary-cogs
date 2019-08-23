import discord
from redbot.core import commands, Config, checks
import brawlstats

class BrawlStarsCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=5245652)
        default_user = {"tag" : None}
        self.config.register_user(**default_user)
        
    async def initialize(self):
        bsapikey = await self.bot.db.api_tokens.get_raw("bsapi", default={"api_key": None})
        if bsapikey["api_key"] is None:
            raise ValueError("The Brawl Stars API key has not been set. Use [p]set api bsapi api_key,YOURAPIKEY")
        self.bsapi = brawlstats.Client(bsapikey["api_key"], is_async=True)
        
    def badEmbed(self, text):
        bembed = discord.Embed(color=0xff0000)
        bembed.set_author(name=text, icon_url="https://i.imgur.com/FcFoynt.png")
        return bembed
        
    def goodEmbed(self, text):
        gembed = discord.Embed(color=0x45cafc)
        gembed.set_author(name=text, icon_url="https://i.imgur.com/qYmbGK6.png")
        return gembed        

    @commands.command()
    async def bssave(self, ctx, tag, member: discord.Member = None):
        """Save your Brawl Stars player tag"""
        if member == None:
            member = ctx.author        
        
        tag = tag.lower().replace('O', '0')
        if tag.startswith("#"):
            tag = tag.strip('#')

        try:
            player = await self.bsapi.get_player(tag)
            await self.config.user(member).tag.set(tag)
            await ctx.send(embed = self.goodEmbed("BS account {} was saved to {}".format(player.name, member.name)))
            
        except brawlstats.errors.NotFoundError:
            await ctx.send(embed = self.badEmbed("No player with this tag found, try again!"))

        except brawlstats.errors.RequestError as e:
            await ctx.send(embed = self.badEmbed(f"BS API is offline, please try again later! ({str(e)})"))
        
        except Exception as e:
            await ctx.send("**Something went wrong, please send a personal message to <@590906101554348053> or try again!**")
            
    @commands.command(aliases=['bsp'])
    async def bsprofile(self, ctx, member=None):
        """Brawl Stars profile"""
        await ctx.trigger_typing()
        prefix = "/"
        tag = ""

        member = ctx.author if member is None else member

        if isinstance(member, discord.Member):
            tag = await self.config.user(member).tag()
            if tag is None:
                return await ctx.send(embed = self.badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))
        elif isinstance(member, str) and member.startswith("<"):
            id = member.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
            try:
                member = discord.utils.get(ctx.guild.members, id=int(id))
                if member is not None:
                    tag = await self.config.user(member).tag()
                    if tag is None:
                        return await ctx.send(embed = self.badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))
            except ValueError:
                pass
        elif isinstance(member, str) and member.startswith("#"):
            tag = member.upper().replace('O', '0')
        elif isinstance(member, str):
            try:
                member = discord.utils.get(ctx.guild.members, id=int(member))
                if member is not None:
                    tag = await self.config.user(member).tag()
                    if tag is None:
                        return await ctx.send(embed = self.badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))
            except ValueError:
                member = discord.utils.get(ctx.guild.members, name=member)
                if member is not None:
                    tag = await self.config.user(member).tag()
                    if tag is None:
                        return await ctx.send(embed = self.badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))

        if tag is None or tag == "":
            desc = "/bsprofile\n/bsprofile @user\n/bsprofile discord_name\n/bsprofile discord_id\n/bsprofile #CRTAG"
            embed = discord.Embed(title="Invalid argument!", colour=discord.Colour.red(), description=desc)
            return await ctx.send(embed=embed)
        try:
            player = await self.bsapi.get_player(tag)
            
        except brawlstats.errors.NotFoundError:
            return await ctx.send(embed = self.badEmbed("No clan with this tag found, try again!"))

        except brawlstats.errors.RequestError as e:
            return await ctx.send(embed = self.badEmbed(f"BS API is offline, please try again later! ({str(e)})"))
        
        except Exception as e:
            return await ctx.send("**Something went wrong, please send a personal message to <@590906101554348053> or try again!**")

        colour = player.name_color_code
        embed=discord.Embed(color=discord.Colour.from_rgb(int(colour[0:1], 16), int(colour[2:3], 16) int(colour[4:5], 16)))
        embed.set_author(name=f"{player.name} #{player.tag}", icon_url="https://i.imgur.com/4HIznBu.png")
        embed.add_field(name="Trophies", value=f"<:bstrophy:552558722770141204>{player.trophies}")
        embed.add_field(name="Highest Trophies", value=f"<:totaltrophies:614517396111097866>{player.highest_trophies}")
        embed.add_field(name="Level", value=f"<:exp:614517287809974405>{player.exp_level}")
        embed.add_field(name="Unlocked Brawlers", value=f"<:brawlers:614518101983232020>{player.brawlers_unlocked}")
        if player.club is not None:
            embed.add_field(name="Club", value=f"<:bsband:600741378497970177>{player.club.name}")
            embed.add_field(name="Role", value=f"<:role:614520101621989435>{player.club.role.capitalize()}")
        embed.add_field(name="3v3 Wins", value=f"<:3v3:614519914815815693>{player.victories}")
        embed.add_field(name="Solo SD Wins", value=f"<:sd:614517124219666453>{player.solo_showdown_victories}")
        embed.add_field(name="Duo SD Wins", value=f"<:duosd:614517166997372972>{player.duo_showdown_victories}")
        embed.add_field(name="Best Time in Robo Rumble", value=f"<:roborumble:614516967092781076>{player.best_robo_rumble_time}")
        embed.add_field(name="Best Time as Big Brawler", value=f"<:biggame:614517022323245056>{player.best_time_as_big_brawler}")
        await ctx.send(embed=embed)
        


        
