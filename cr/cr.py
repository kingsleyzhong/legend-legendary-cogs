import discord
from redbot.core import commands, Config, checks
import clashroyale

class ClashRoyaleCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2512325)
        default_user = {"tag" : None}
        self.config.register_user(**default_user)
        
    async def initialize(self):
        apikey = await self.bot.db.api_tokens.get_raw("crapi", default={"api_key": None})
        if apikey["api_key"] is None:
            raise ValueError("The Clash Royale API key has not been set. Use [p]set api crapi api_key,YOURAPIKEY")
        self.crapi = clashroyale.OfficialAPI(apikey["api_key"], is_async=True)

    def cog_unload(self):
        self.bsapi.close()
        
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

    @commands.command(aliases=['p'])
    async def profile(self, ctx, member=None):
        """Clash Royale profile"""
        await ctx.trigger_typing()
        prefix = "/"
        tag = ""

        member = ctx.author if member is None else member

        if isinstance(member, discord.Member):
            tag = await self.config.user(member).tag()
            if tag is None:
                return await ctx.send(embed = self.badEmbed(f"This user has no tag saved! Use {prefix}save <tag>"))
        elif isinstance(member, str) and member.startswith("<"):
            id = member.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
            try:
                member = discord.utils.get(ctx.guild.members, id=int(id))
                if member is not None:
                    tag = await self.config.user(member).tag()
                    if tag is None:
                        return await ctx.send(embed = self.badEmbed(f"This user has no tag saved! Use {prefix}save <tag>"))
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
                        return await ctx.send(embed = self.badEmbed(f"This user has no tag saved! Use {prefix}save <tag>"))
            except ValueError:
                member = discord.utils.get(ctx.guild.members, name=member)
                if member is not None:
                    tag = await self.config.user(member).tag()
                    if tag is None:
                        return await ctx.send(embed = self.badEmbed(f"This user has no tag saved! Use {prefix}save <tag>"))

        if tag is None or tag == "":
            desc = "/profile\n/profile @user\n/profile discord_name\n/profile discord_id\n/profile #CRTAG"
            embed = discord.Embed(title="Invalid argument!", colour=discord.Colour.red(), description=desc)
            return await ctx.send(embed=embed)
        try:
            player = await self.crapi.get_player(tag)
            chests = await self.crapi.get_player_chests(tag)
            
        except clashroyale.NotFoundError:
            return await ctx.send(embed = self.badEmbed("No clan with this tag found, try again!"))

        except clashroyale.RequestError as e:
            return await ctx.send(embed = self.badEmbed(f"CR API is offline, please try again later! ({str(e)})"))
        
        except Exception as e:
            return await ctx.send(embed = self.badEmbed("Something went wrong, this is unusual and shouldn't happen. Please message the bot to report this error."))

        embed=discord.Embed(color=discord.Colour.blue())
        embed.set_author(name=f"{player.name} {player.tag}", icon_url="https://i.imgur.com/Qs0Ter9.png")
        embed.add_field(name="Trophies", value=f"<:trophycr:587316903001718789>{player.trophies}")
        embed.add_field(name="Highest Trophies", value=f"<:nicertrophy:587565339038973963>{player.bestTrophies}")
        embed.add_field(name="Level", value=f"<:level:451064038420381717>{player.expLevel}")
        embed.add_field(name="Arena", value=f"<:training:587566327204544512>{player.arena.name}")
        if player.clan is not None:
            clanbadge = discord.utils.get(self.bot.emojis, name = str(player.clan.badgeId))
            embed.add_field(name="Clan", value=f"{clanbadge}{player.clan.name}")
            embed.add_field(name="Role", value=f"<:social:451063078096994304>{player.role.capitalize()}")
        embed.add_field(name="Total Games Played", value=f"<:swords:449650442033430538>{player.battleCount}")
        embed.add_field(name="Wins/Losses", value=f"<:starcr:587705837817036821>{player.wins}/{player.losses}")
        embed.add_field(name="Three Crown Wins", value=f"<:crownblue:449649785528516618>{player.threeCrownWins}")
        embed.add_field(name="War Day Wins", value=f"<:cw_win:449644364981993475>{player.warDayWins}")
        embed.add_field(name="Clan Cards Collected", value=f"<:cw_cards:449641339580317707>{player.clanCardsCollected}")
        embed.add_field(name="Max Challenge Wins", value=f"<:tournament:587706689357217822>{player.challengeMaxWins}")
        embed.add_field(name="Challenge Cards Won", value=f"<:cardcr:587702597855477770>{player.challengeCardsWon}")
        embed.add_field(name="Favourite Card", value=f"<:epic:587708123087634457>{player.currentFavouriteCard.name}")
        embed.add_field(name="Total Donations", value=f"<:deck:451062749565550602>{player.totalDonations}")

        chests_msg = ""
        i = 0
        for chest in chests:
            emoji = discord.utils.get(self.bot.emojis, name = str(chest.name.lower().replace(" ", "")))
            chests_msg += f"{emoji}`{chest.index}`"
            if i == 8:
                chests_msg +="X"
            i+=1
        embed.add_field(name="Upcoming Chests", value=chests_msg.split("X")[0], inline=False)
        embed.add_field(name="Rare Chests", value=chests_msg.split("X")[1], inline=False)
        await ctx.send(embed=embed)
