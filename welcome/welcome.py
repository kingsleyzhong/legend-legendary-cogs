import discord
from redbot.core import commands, Config, checks
import clashroyale
import brawlstats
import asyncio

class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.crconfig = Config.get_conf(None, identifier=2512325, cog_name="ClashRoyaleCog")

    #@commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 440960893916807188 and not member.bot and False:

            await self.do_setup(member)

    async def initialize(self):
        apikey = await self.bot.db.api_tokens.get_raw("crapi", default={"api_key": None})
        if apikey["api_key"] is None:
            raise ValueError("The Clash Royale API key has not been set. Use [p]set api crapi api_key,YOURAPIKEY")
        self.crapi = clashroyale.OfficialAPI(apikey["api_key"], is_async=True)
            
    @commands.guild_only()
    @commands.command(hidden=True)
    async def setup(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author
        await self.do_setup(member)

    async def do_setup(self, member):
        welcomeCategory = discord.utils.get(member.guild.categories, id=598437481775497216)
        overwrites = {member.guild.default_role: discord.PermissionOverwrite(read_messages=False), member: discord.PermissionOverwrite(read_messages=True)}
        setupChannel = await member.guild.create_text_channel(member.name, category=welcomeCategory, overwrites=overwrites, topic=f"Welcoming channel for {member.display_name} ({member.id})" , reason=f"Channel created for {member.display_name} role setup.")
        welcomeLog = self.bot.get_channel(598437710868512798)
        logMessage = await welcomeLog.send(f"--------------------\n__**{member.display_name}:**__")
        async def appendLog(txt):
            await logMessage.edit(content=f"{logMessage.content}\n{txt}")

        try:
            roleNewcomer = member.guild.get_role(597767307397169173)
            roleMemberDivider = member.guild.get_role(597769836097044480)
            roleSubscriptionDivider = member.guild.get_role(597807441698226197)
            await member.add_roles(roleNewcomer, roleMemberDivider, roleSubscriptionDivider)
            await appendLog(f"Assigned roles: {roleNewcomer.name}, Member Divider, Subscription Divider")
        except discord.Forbidden:
            await appendLog(f"!!!Couldn't change roles of this user. ({roleNewcomer.name}, Member Divider, Subscription Divider)")

        welcomeEmbed = discord.Embed(colour = discord.Colour.blue())
        welcomeEmbed.set_image(url="https://i.imgur.com/wwhgP4f.png")
        welcomeEmbed2 = discord.Embed(colour = discord.Colour.blue())
        welcomeEmbed2.set_image(url="https://i.imgur.com/LOLUk7Q.png")
        welcomeEmbed3 = discord.Embed(colour = discord.Colour.blue())
        welcomeEmbed3.set_image(url="https://i.imgur.com/SkR1NsG.png")
        await setupChannel.send(member.mention, embed=welcomeEmbed)
        await setupChannel.send("We are a gamer run community devoted to enhancing the player experience. We offer comprehensive resources, guidance from veteran gamers, and involvement in a vibrant interactive online community that cater to both casual members and players looking for a more competitive edge. We have an eSports team and host frequent tournaments/events for cash prizes.", embed=welcomeEmbed2)
        await setupChannel.send("You can read about our mission statement and how we function at #information.\nPlease follow our discord and gaming rules which can be viewed in detail at #rules.", embed=welcomeEmbed3)
        await asyncio.sleep(2)

        repeat = True
        while repeat:
            repeat = False
            text = "**Choose a game in which you would like to join us:**\n---------------------------\n<:ClashRoyale:595528714138288148> **Clash Royale**\n---------------------------\n<:BrawlStars:595528113929060374> **Brawl Stars**\n---------------------------\n<:nocancel:595535992199315466> **None of the above**\n---------------------------"
            chooseGameMessage = await setupChannel.send(text)
            await chooseGameMessage.add_reaction("<:ClashRoyale:595528714138288148>")
            await chooseGameMessage.add_reaction("<:BrawlStars:595528113929060374>")
            await chooseGameMessage.add_reaction("<:nocancel:595535992199315466>")

            def check(reaction, user):
                return user == member and str(reaction.emoji) in ["<:ClashRoyale:595528714138288148>", "<:BrawlStars:595528113929060374>", "<:nocancel:595535992199315466>"]
            reaction, _ = await self.bot.wait_for('reaction_add', check=check)
            
            if str(reaction.emoji) == "<:ClashRoyale:595528714138288148>":
                await appendLog("Chosen game: Clash Royale")
                sendTagEmbed = discord.Embed(title="Please tell me your Clash Royale tag!", colour = discord.Colour.blue())
                sendTagEmbed.set_image(url="https://i.imgur.com/Fc8uAWH.png")
                await setupChannel.send(embed=sendTagEmbed)
                def checkmsg(m):
                    return m.channel == setupChannel and m.author == member
                tagMessage = await self.bot.wait_for('message', check=checkmsg)
                tag = tagMessage.content.lower().replace('O', '0').replace(' ', '')
                if tag.startswith("#"):
                    tag = tag.strip('#')
                await appendLog(f"Tag input: {tag}")
                
                try:
                    player = await self.crapi.get_player("#" + tag)
                    await appendLog(f"CR account found: {player.name}")
                    playerEmbed = discord.Embed(color=discord.Colour.blue())
                    playerEmbed.set_author(name=f"{player.name}", icon_url="https://i.imgur.com/Qs0Ter9.png")
                    playerEmbed.add_field(name="Trophies", value=f"<:trophycr:587316903001718789>{player.trophies}")
                    if player.clan is not None:
                        playerEmbed.add_field(name="Clan", value=f"{discord.utils.get(self.bot.emojis, name = str(player.clan.badgeId))}{player.clan.name}")
                        playerEmbed.add_field(name="Role", value=f"<:social:451063078096994304>{player.role.capitalize()}")
                    else:
                        playerEmbed.add_field(name="Clan", value="None")
                    playerEmbed.add_field(name="Is this your account? (Choose reaction)", value="<:yesconfirm:595535992329601034> Yes\t<:nocancel:595535992199315466> No", inline=False)
                    confirmMessage = await setupChannel.send(f"**Clash Royale** account with tag **#{tag.upper()}** found:", embed=playerEmbed)
                    await confirmMessage.add_reaction("<:yesconfirm:595535992329601034>")
                    await confirmMessage.add_reaction("<:nocancel:595535992199315466>")

                    def ccheck(reaction, user):
                        return user == member and str(reaction.emoji) in ["<:yesconfirm:595535992329601034>", "<:nocancel:595535992199315466>"]

                    reaction, _ = await self.bot.wait_for('reaction_add', check=ccheck)

                    if str(reaction.emoji) == "<:yesconfirm:595535992329601034>":
                        await appendLog(f"User's account: Yes")
                        nick=f"{player.name} | {player.clan.name}" if player.clan is not None else f"{player.name}"
                        try:
                            await member.edit(nick=nick[:31])
                            await appendLog(f"Nickname changed: {nick[:31]}")
                        except discord.Forbidden:
                            await appendLog(f"!!!Couldn't change nickname of this user. ({nick[:31]})")

                        await self.crconfig.user(member).tag.set(tag)

                        try:
                            roleVerifiedMember = member.guild.get_role(597768235324145666)
                            roleCRMember = member.guild.get_role(440982993327357963)
                            await member.add_roles(roleVerifiedMember, roleCRMember)
                            await appendLog(f"Assigned roles: {roleVerifiedMember.name}, {roleCRMember.name}")
                        except discord.Forbidden:
                            await appendLog(f"!!!Couldn't change roles of this user. ({roleVerifiedMember.name}, {roleCRMember.name})")

                        
                        LAClans = ["1", "2", "3"]
                        if player.clan is not None and player.clan in LAClans:
                            #give LA_CR_Member + clan role
                            await setupChannel.send(f"Give LA_CR_Member and Clan role.")
                        
                        repeat = False
                        await setupChannel.send("You account has been saved!\n\n**WHAT TO DO NEXT?**\n\nPlease go to <#534426447868198922> to open up the channels of your choice and personalize your experience.\n\nCheck out <#440974277894864906> for bot use and <#488321784781996032> to help navigate the site.\n\nLet us know if you need anything by sending a personal message to <@590906101554348053>.\n\n**Thank you, and enjoy your stay!**\n*- Legendary Alliance Community*")

                    elif str(reaction.emoji) == "<:nocancel:595535992199315466>":
                        await appendLog(f"User's account: No")
                        repeat = True
                    
                except clashroyale.NotFoundError as e:
                    repeat = True
                    await setupChannel.send("No player with this tag found, try again!")
                    await appendLog(f"Error occured: {str(e)}")
                except ValueError as e:
                    repeat = True
                    await setupChannel.send(f"**{str(e)}\nTry again or contact support in #support!**")
                    await appendLog(f"Error occured: {str(e)}")
                except clashroyale.RequestError as e:
                    repeat = True
                    await setupChannel.send(f"Clash Royale API is offline, please try again later! ({str(e)})")
                    await appendLog(f"Error occured: {str(e)}")
                except Exception as e:
                    repeat = True
                    await setupChannel.send("**Something went wrong, please contact support in #support or try again!**")
                    await appendLog(f"Error occured: {str(e)}")



            elif str(reaction.emoji) == "<:BrawlStars:595528113929060374>":
                await appendLog("Chosen game: Brawl Stars")
                await setupChannel.send(embed=discord.Embed(title="You chose Brawl Stars", description="Please tell me your tag!"))
                def checkmsgbs(m):
                    return m.channel == setupChannel and m.author == member
                tagMessage = await self.bot.wait_for('message', check=checkmsgbs)
                tag = tagMessage.content.lower().replace('O', '0')
                if tag.startswith("#"):
                    tag = tag.strip('#')

                #try:
                player = await self.bot.bsapi.get_player(tag)
                await setupChannel.send(f"BS account {player.name} found!")
                #except brawlstats.errors.NotFoundError as e:
                    #return await setupChannel.send("No player with this tag found, try again!")
                #except brawlstats.errors.RequestError as e:
                #    return await setupChannel.send(f"BS API is offline, please try again later! ({str(e)})")
                #except Exception as e:
                #    return await setupChannel.send("Something went wrong, this is unusual and shouldn't happen. Please message the bot to report this error.")
        
            elif str(reaction.emoji) == "<:nocancel:595535992199315466>":
                await appendLog("Chosen game: None of the above")
                text = "**Choose an option:**\n-------------------------------------\n<:Search:598803244512313355> **Just visiting**\n-------------------------------------\n<:HelpIcon:598803665989402624> **Talk to support**\n-------------------------------------\n<:GoBack:598803665771429904> **Go back to choosing a game**\n-------------------------------------"
                chooseOtherOption = await setupChannel.send(text)
                await chooseOtherOption.add_reaction("<:Search:598803244512313355>")
                await chooseOtherOption.add_reaction("<:HelpIcon:598803665989402624>")
                await chooseOtherOption.add_reaction("<:GoBack:598803665771429904>")

                def checkother(reaction, user):
                    return user == member and str(reaction.emoji) in ["<:Search:598803244512313355>", "<:HelpIcon:598803665989402624>", "<:GoBack:598803665771429904>"]
                reaction, _ = await self.bot.wait_for('reaction_add', check=checkother)

                if str(reaction.emoji) == "<:Search:598803244512313355>":
                    await appendLog("Chosen option: Just visiting")
                    await setupChannel.send("ADD: give guest role")
                elif str(reaction.emoji) == "<:HelpIcon:598803665989402624>":
                    await appendLog("Chosen option: Talk to support")
                    await setupChannel.send("ADD: redirect to Modmail")
                elif str(reaction.emoji) == "<:GoBack:598803665771429904>":
                    await appendLog("Chosen option: Go back to choosing game")
                    repeat = True

        await appendLog(f"**Finished**")
        await setupChannel.send(embed=discord.Embed(colour=discord.Colour.blue(), description="This channel will get deleted in 5 minutes!\n\nIf you have any questions or need help please send a personal message to <@590906101554348053>.".upper()))
        await asyncio.sleep(300)
        await setupChannel.delete(reason="Welcoming process finished.")
