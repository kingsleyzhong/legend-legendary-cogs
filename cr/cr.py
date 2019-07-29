import discord
from redbot.core import commands, Config, checks
import clashroyale

class ClashRoyaleCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2512325)
        default_user = {"tag" : None, "nick" : None}
        self.config.register_user(**default_user)
        default_guild = {"clans" : {}}
        self.config.register_guild(**default_guild)
        
    async def initialize(self):
        apikey = await self.bot.db.api_tokens.get_raw("crapi", default={"api_key": None})
        if apikey["api_key"] is None:
            raise ValueError("The Clash Royale API key has not been set. Use [p]set api crapi api_key,YOURAPIKEY")
        self.crapi = clashroyale.OfficialAPI(apikey["api_key"], is_async=True)

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
            await self.config.user(member).tag.set(tag)
            await self.config.user(member).nick.set(player.name)
            await ctx.send(embed = self.goodEmbed("CR account {} was saved to {}".format(player.name, member.name)))
            
        except clashroyale.NotFoundError as e:
            await ctx.send(embed = self.badEmbed("No player with this tag found, try again!"))

        except clashroyale.RequestError as e:
            await ctx.send(embed = self.badEmbed(f"CR API is offline, please try again later! ({str(e)})"))
        
        except Exception as e:
            await ctx.send("**Something went wrong, please send a personal message to LA Modmail bot or try again!**")

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
            return await ctx.send("**Something went wrong, please send a personal message to <@590906101554348053> or try again!**")


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
        
        
    @commands.guild_only()
    @commands.group(aliases=['clan'], invoke_without_command=True)
    async def clans(self, ctx, key:str=None):
        """View all clans saved in this server"""
        offline = False
        prefix = ctx.prefix
        await ctx.trigger_typing()

        if key == "forceoffline":
            offline = True
            key = None

        if key is not None:
            try:
                if key.startswith("<"):
                    memberid = key.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                    member = discord.utils.get(ctx.guild.members, id=int(memberid))
                    if member is not None:
                        mtag = await self.config.user(member).tag()
                        if mtag is None:
                            return await ctx.send(embed = self.badEmbed(f"This user has no tag saved! Use {prefix}save <tag>"))

                        try:
                            player = await self.crapi.get_player(mtag)
                            tag = player.clan.tag
                        except clashroyale.RequestError as e:
                            await ctx.send(embed = self.badEmbed(f"CR API is offline, please try again later! ({str(e)})"))
                else:
                    tag = await self.config.guild(ctx.guild).clans.get_raw(key.lower(), "tag", default=None)
                    if tag is None:
                        return await ctx.send(embed = self.badEmbed(f"{key.title()} isn't saved clan in this server!"))
                try:
                    clan = await self.crapi.get_clan(tag)
                    clan = clan.raw_data
                
                except clashroyale.RequestError as e:
                    await ctx.send(embed = self.badEmbed(f"CR API is offline, please try again later! ({str(e)})"))
                    return
                
                badge = discord.utils.get(self.bot.emojis, name = str(clan['badgeId']))
                embed=discord.Embed(title=f"{badge}{clan['name']} ({clan['tag']})", description=f"```{clan['description']}```", color=0x891193)
                embed.add_field(name="Members", value=f"<:people:449645181826760734> {clan['members']}/50")
                embed.add_field(name="Required Trophies", value= f"<:trophycr:587316903001718789> {str(clan['requiredTrophies'])}")
                embed.add_field(name="Score", value= f"<:crstar:449647025999314954> {str(clan['clanScore'])}")
                embed.add_field(name="Clan War Trophies", value= f"<:cw_trophy:449640114423988234> {str(clan['clanWarTrophies'])}")
                embed.add_field(name="Type", value= f"<:bslock:552560387279814690> {clan['type'].title()}")
                embed.add_field(name="Location", value=f":earth_africa: {clan['location']['name']}")
                embed.add_field(name="Average Donations Per Week", value= f"<:deck:451062749565550602> {str(clan['donationsPerWeek'])}")
                return await ctx.send(embed=embed)            
                
            except ZeroDivisionError as e:
                return await ctx.send("**Something went wrong, please send a personal message to LA Modmail bot or try again!**")
                                
        try:
            try:
                clans = []
                for key in (await self.config.guild(ctx.guild).clans()).keys():
                    clan = await self.crapi.get_clan(await self.config.guild(ctx.guild).clans.get_raw(key, "tag"))
                    clans.append(clan.raw_data)
            except clashroyale.RequestError as e:
                offline = True
            
            embed = discord.Embed(color = discord.Colour.blue())
            embed.set_author(name=f"{ctx.guild.name} clans".upper(), icon_url=ctx.guild.icon_url)
            
            if not offline:
                clans = sorted(clans, key=lambda sort: (sort['requiredTrophies'], sort['clanScore']), reverse=True)
                
                for i in range(len(clans)):   
                    cemoji = discord.utils.get(self.bot.emojis, name = str(clans[i]['badgeId']))
                    key = ""
                    for k in (await self.config.guild(ctx.guild).clans()).keys():
                        if clans[i]['tag'].replace("#", "") == await self.config.guild(ctx.guild).clans.get_raw(k, "tag"):
                            key = k
                                
                    self.saved_clans[family][key]['lastMemberCount'] = clans[i]['members']
                    self.saved_clans[family][key]['lastRequirement'] = clans[i]['requiredTrophies']
                    self.saved_clans[family][key]['lastScore'] = clans[i]['clanScore']
                    self.saved_clans[family][key]['lastPosition'] = i
                    self.saved_clans[family][key]['lastBadgeId'] = clans[i]['badgeId']
                    self.saved_clans[family][key]['warTrophies'] = clans[i]['clanWarTrophies']
                   
                    e_name = f"{str(cemoji)} {clans[i]['name']} [{key}] ({clans[i]['tag']}) {self.saved_clans[family][key]['info']}"
                    e_value = f"<:people:449645181826760734>`{clans[i]['members']}` <:trophycr:587316903001718789>`{clans[i]['requiredTrophies']}+` <:crstar:449647025999314954>`{clans[i]['clanScore']}` <:cw_trophy:449640114423988234>`{clans[i]['clanWarTrophies']}`"
                    embed.add_field(name=e_name, value=e_value, inline=False)
                
                embed.set_footer(text = "Do you need more info about a clan? Use {}clan [key]".format(prefix))
                await ctx.send(embed = embed)
            
            else:
                offclans = []
                for ckey in self.saved_clans[family].keys():
                    offclans.append([self.saved_clans[family][ckey]['lastPosition'], self.saved_clans[family][ckey]['name'], self.saved_clans[family][ckey]['tag'], self.saved_clans[family][ckey]['info'], self.saved_clans[family][ckey]['lastMemberCount'], self.saved_clans[family][ckey]['lastRequirement'], self.saved_clans[family][ckey]['lastScore'], self.saved_clans[family][ckey]['warTrophies'], self.saved_clans[family][ckey]['lastBadgeId'], ckey])
                    
                offclans = sorted(offclans, key=lambda x: x[0])
                
                for clan in offclans:
                    cname = clan[1]
                    ctag = clan[2]
                    cinfo = clan[3]
                    cmembers = clan[4]
                    creq = clan[5]
                    cscore = clan[6]
                    ccw = clan[7] 
                    cbadgeid = clan[8]
                    ckey = clan[9]
                    
                    cemoji = discord.utils.get(self.bot.emojis, name = str(cbadgeid))
                    
                    e_name = f"{cemoji} {cname} [{ckey}] (#{ctag}) {cinfo}"
                    e_value = f"<:people:449645181826760734>`{cmembers}` <:trophycr:587316903001718789>`{creq}+` <:crstar:449647025999314954>`{cscore}` <:cw_trophy:449640114423988234>`{ccw}`"
                    embed.add_field(name=e_name, value=e_value, inline=False)
                    embed.set_footer(text = "API is offline, showing last saved data.")
                await ctx.send(embed = embed)
        
        except TypeError as e:
            await ctx.send(embed = self.badEmbed("No clans to show yet, atleast 2 must be added! Add them using {}clans add!".format(prefix)))

        except ZeroDivisionError as e:
            return await ctx.send("**Something went wrong, please send a personal message to **LA Modmail** bot or try again!**")
                                
                                
    @commands.guild_only()
    @commands.has_permissions(administrator = True) 
    @clans.command(name="add")
    async def clans_add(self, ctx, key : str, tag : str):
        """
        Add a clan to /clans command

        key - key for the clan to be used in other commands
        tag - in-game tag of the clan
        """
        await ctx.trigger_typing()
        if tag.startswith("#"):
            tag = tag.strip('#').upper().replace('O', '0')
        
        if key in (await self.config.guild(ctx.guild).clans()).keys():
            return await ctx.send(embed = self.badEmbed("This clan is already saved!"))

        try:
            clan = await self.crapi.get_clan(tag)
            clan = clan.raw_data
            result = {
                "name" : clan['name'],
                "nick" : key.title(),
                "tag" : clan['tag'].replace("#", ""),
                "lastMemberCount" : clan['members'],
                "lastRequirement" : clan['requiredTrophies'],
                "lastScore" : clan['clanScore'],
                "info" : "",
                "warTrophies" : clan['clanWarTrophies']
                }
            key = key.lower()
            await self.config.guild(ctx.guild).clans.set_raw(key, value=result)
            await ctx.send(embed = self.goodEmbed(f"{clan['name']} was successfully saved for this server!"))

        except clashroyale.NotFoundError as e:
            await ctx.send(embed = self.badEmbed("No clan with this tag found, try again!"))

        except clashroyale.RequestError as e:
            await ctx.send(embed = self.badEmbed(f"CR API is offline, please try again later! ({str(e)})"))

        except Exception as e:
            return await ctx.send("**Something went wrong, please send a personal message to **LA Modmail** bot or try again!**")
