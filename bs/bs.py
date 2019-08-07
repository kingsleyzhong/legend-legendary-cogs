import discord
from redbot.core import commands, Config, checks
import brawlstats
from bs4 import BeautifulSoup
from ext.paginator import PaginatorSession
import aiohttp
import datetime
import json
import pytz

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

        else:
            if self.check_tag(tag):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://brawlstats.io/players/{id}') as resp:
                            data = await resp.read()
                    soup = BeautifulSoup(data, 'lxml')
                except Exception as e:
                    await ctx.send(e)
                else:
                    success = True
            else:
                await ctx.send("Invalid tag. Tags can only contain the following characters: `0289PYLQGRJCUV`")
        if success:
            source = str(soup.find_all("img", class_="mr-2"))
            src = source.split('src="')[1]
            imgpath = src.split('" w')[0]

            brawlers = get_all_attrs("div", "brawlers-brawler-slot d-inline-block")
            top = str(brawlers[0])
            name_after = top.split('brawlers/')[1]
            highestbrawler = name_after.split('"')[0].title()

            em = discord.Embed(color=discord.Color.green())
            em.set_thumbnail(url=f'https://brawlstats.io{imgpath}')
            em.title = f"{get_attr('div', 'player-name brawlstars-font')} (#{id})"
            em.description = f"Band: {get_attr('div', 'band-name mr-2')} ({get_attr('div', 'band-tag')})"
            em.add_field(name="Level", value=get_attr('div', 'experience-level'))
            em.add_field(name="Experience", value=get_attr('div', 'progress-text'))
            em.add_field(name="Trophies", value=get_all_attrs('div', 'trophies')[0].text)
            em.add_field(name="Highest Trophies", value=get_all_attrs('div', 'trophies')[1].text)
            em.add_field(name="Highest Brawler", value=highestbrawler)
            em.add_field(name="Highest Brawler Trophies", value=get_all_attrs('div', 'trophies')[2].text)
            em.add_field(name="Victories", value=get_attr('div', 'victories'))
            em.add_field(name="Showdown Victories", value=get_attr('div', 'showdown-victories'))
            em.add_field(name="Best time as boss", value=get_attr('div', 'boss-time'))
            em.add_field(name="Best robo rumble time", value=get_attr('div', 'robo-time'))
            await ctx.send(embed=em)

        


        
