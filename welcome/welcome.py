import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import pagify
import clashroyale
import brawlstats
import asyncio

class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.crconfig = Config.get_conf(None, identifier=2512325, cog_name="ClashRoyaleCog")
        self.bsconfig = Config.get_conf(None, identifier=5245652, cog_name="BrawlStarsCog")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 440960893916807188 and not member.bot:
            await self.do_setup(member)

    async def initialize(self):
        crapikey = await self.bot.db.api_tokens.get_raw("crapi", default={"api_key": None})
        if crapikey["api_key"] is None:
            raise ValueError("The Clash Royale API key has not been set. Use [p]set api crapi api_key,YOURAPIKEY")
        self.crapi = clashroyale.OfficialAPI(crapikey["api_key"], is_async=True)
        
        bsapikey = await self.bot.db.api_tokens.get_raw("bsapi", default={"api_key": None})
        if bsapikey["api_key"] is None:
            raise ValueError("The Brawl Stars API key has not been set. Use [p]set api bsapi api_key,YOURAPIKEY")
        self.bsapi = brawlstats.Client(bsapikey["api_key"], is_async=True)
            
    @commands.guild_only()
    @commands.command(hidden=True)
    async def setup(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author
        await self.do_setup(member)

    async def do_setup(self, member):
        welcomeCategory = discord.utils.get(member.guild.categories, id=598437481775497216)
        overwrites = {member.guild.default_role: discord.PermissionOverwrite(read_messages=False), member: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True)}
        setupChannel = await member.guild.create_text_channel(member.name, category=welcomeCategory, overwrites=overwrites, topic=f"Welcoming channel for {member.display_name} ({member.id})" , reason=f"Channel created for {member.display_name} role setup.")
        welcomeLog = self.bot.get_channel(598437710868512798)
        logMessages = []
        logMessages.append(await welcomeLog.send(f"--------------------\n__**{member.display_name}:**__"))
        async def appendLog(txt):
            count = 0
            for page in pagify(txt):
                if len(logMessages) < count+1:
                     logMessages[count] = await welcomeLog.send(page)
                else:
                    await logMessages[count].edit(content=f"{logMessages[count].content}\n{page}")
                count += 1
        try:
            roleNewcomer = member.guild.get_role(597767307397169173)
            roleMemberDivider = member.guild.get_role(597769836097044480)
            roleSubscriptionDivider = member.guild.get_role(597807441698226197)
            await member.add_roles(roleNewcomer, roleMemberDivider, roleSubscriptionDivider)
            await appendLog(f"Assigned roles: {roleNewcomer.name}, Member Divider, Subscription Divider")
        except discord.Forbidden:
            await appendLog(f":exclamation:Couldn't change roles of this user. ({roleNewcomer.name}, Member Divider, Subscription Divider)")

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

        showCR = True
        showBS = True
        repeat = True
        while repeat:
            repeat = False
            text = "**Choose a game in which you would like to join us:**\n---------------------------\n<:ClashRoyale:595528714138288148> **Clash Royale**\n---------------------------\n<:BrawlStars:595528113929060374> **Brawl Stars**\n---------------------------\n<:nocancel:595535992199315466> **None of the above**\n---------------------------"
            chooseGameMessage = await setupChannel.send(text)
            if showCR:
                await chooseGameMessage.add_reaction("<:ClashRoyale:595528714138288148>")
            if showBS:
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
                            await appendLog(f":exclamation:Couldn't change nickname of this user. ({nick[:31]})")

                        await self.crconfig.user(member).tag.set(tag)
                        await appendLog("Saved tag: Clash Royale")

                        try:
                            roleVerifiedMember = member.guild.get_role(597768235324145666)
                            roleCRMember = member.guild.get_role(440982993327357963)
                            await member.add_roles(roleVerifiedMember, roleCRMember)
                            await appendLog(f"Assigned roles: {roleVerifiedMember.name}, {roleCRMember.name}")
                        except discord.Forbidden:
                            await appendLog(f":exclamation:Couldn't change roles of this user. ({roleVerifiedMember.name}, {roleCRMember.name})")

                        #CHECK FOR LA CLAN
                        
                        await setupChannel.send("You account has been saved!\n\n**WHAT TO DO NEXT?**\n\nPlease go to <#534426447868198922> to open up the channels of your choice and personalize your experience.\n\nCheck out <#440974277894864906> for bot use and <#488321784781996032> to help navigate the site.\n\nLet us know if you need anything by sending a personal message to <@590906101554348053>.\n\n**Thank you, and enjoy your stay!**\n*- Legendary Alliance Community*")
                        if showCR and showBS:
                            saveOtherGame = await setupChannel.send(embed=discord.Embed(colour=discord.Colour.blue(), description="Would you like to save Brawl Stars account as well?"))
                            await saveOtherGame.add_reaction("<:yesconfirm:595535992329601034>")
                            await saveOtherGame.add_reaction("<:nocancel:595535992199315466>")
                            def ocheck(reaction, user):
                                return user == member and str(reaction.emoji) in ["<:yesconfirm:595535992329601034>", "<:nocancel:595535992199315466>"]
                            try:
                                reaction, _ = await self.bot.wait_for('reaction_add', check=ocheck, timeout=600)
                            except asyncio.TimeoutError:
                                repeat = False
                                
                            if str(reaction.emoji) == "<:yesconfirm:595535992329601034>":
                                await appendLog("Save other game: Yes")
                                repeat = True
                                showCR = False
                            elif str(reaction.emoji) == "<:nocancel:595535992199315466>":
                                await appendLog("Save other game: No")
                                repeat = False
                        else:
                            repeat = False
                        
                    elif str(reaction.emoji) == "<:nocancel:595535992199315466>":
                        await appendLog(f"User's account: No")
                        repeat = True
                    
                except clashroyale.NotFoundError as e:
                    repeat = True
                    await setupChannel.send("No player with this tag found, try again!")
                    await appendLog(f":exclamation:Error occured: {str(e)}")
                except ValueError as e:
                    repeat = True
                    await setupChannel.send(f"**{str(e)}\nTry again or send a personal message to <@590906101554348053>!**")
                    await appendLog(f":exclamation:Error occured: {str(e)}")
                except clashroyale.RequestError as e:
                    repeat = True
                    await setupChannel.send(f"Clash Royale API is offline, please try again later! ({str(e)})")
                    await appendLog(f":exclamation:Error occured: {str(e)}")
                except Exception as e:
                    repeat = True
                    await setupChannel.send("**Something went wrong, please send a personal message to <@590906101554348053> or try again!**")
                    await appendLog(f":exclamation:Error occured: {str(e)}")


            elif str(reaction.emoji) == "<:BrawlStars:595528113929060374>":
                await appendLog("Chosen game: Brawl Stars")
                sendTagEmbed = discord.Embed(title="Please tell me your Brawl Stars tag!", colour = discord.Colour.blue())
                sendTagEmbed.set_image(url="https://i.imgur.com/trjFkYP.png")
                await setupChannel.send(embed=sendTagEmbed)
                def checkmsgbs(m):
                    return m.channel == setupChannel and m.author == member
                tagMessage = await self.bot.wait_for('message', check=checkmsgbs)
                tag = tagMessage.content.lower().replace('O', '0')
                if tag.startswith("#"):
                    tag = tag.strip('#')

                try:
                    player = await self.bsapi.get_player(tag)
                    await appendLog(f"BS account found: {player.name}")
                    playerEmbed = discord.Embed(color=discord.Colour.blue())
                    playerEmbed.set_author(name=f"{player.name}", icon_url="https://i.imgur.com/40U8PnF.png")
                    playerEmbed.add_field(name="Trophies", value=f"<:bstrophy:552558722770141204>{player.trophies}")
                    if player.club is not None:
                        playerEmbed.add_field(name="Club", value=f"<:bsband:600741378497970177>{player.club.name}")
                        playerEmbed.add_field(name="Role", value=f"<:bs_role:600748317940645918>{player.club.role.capitalize()}")
                    else:
                        playerEmbed.add_field(name="Club", value="None")
                        
                    playerEmbed.add_field(name="Is this your account? (Choose reaction)", value="<:yesconfirm:595535992329601034> Yes\t<:nocancel:595535992199315466> No", inline=False)
                    confirmMessage = await setupChannel.send(f"**Brawl Stars** account with tag **#{tag.upper()}** found:", embed=playerEmbed)
                    await confirmMessage.add_reaction("<:yesconfirm:595535992329601034>")
                    await confirmMessage.add_reaction("<:nocancel:595535992199315466>")
                    def ccheck(reaction, user):
                        return user == member and str(reaction.emoji) in ["<:yesconfirm:595535992329601034>", "<:nocancel:595535992199315466>"]

                    reaction, _ = await self.bot.wait_for('reaction_add', check=ccheck)

                    if str(reaction.emoji) == "<:yesconfirm:595535992329601034>":
                        await appendLog(f"User's account: Yes")
                        nick=f"{player.name} | {player.club.name}" if player.club is not None else f"{player.name}"
                        try:
                            await member.edit(nick=nick[:31])
                            await appendLog(f"Nickname changed: {nick[:31]}")
                        except discord.Forbidden:
                            await appendLog(f":exclamation:Couldn't change nickname of this user. ({nick[:31]})")

                        await self.bsconfig.user(member).tag.set(tag)
                        await appendLog("Saved tag: Brawl Stars")

                        try:
                            roleVerifiedMember = member.guild.get_role(597768235324145666)
                            roleBSMember = member.guild.get_role(524418759260241930)
                            await member.add_roles(roleVerifiedMember, roleBSMember)
                            await appendLog(f"Assigned roles: {roleVerifiedMember.name}, {roleBSMember.name}")
                        except discord.Forbidden:
                            await appendLog(f":exclamation:Couldn't change roles of this user. ({roleVerifiedMember.name}, {roleBSMember.name})")

                        #CHECK FOR LA CLUB
                        
                        await setupChannel.send("You account has been saved!\n\n**WHAT TO DO NEXT?**\n\nCheck out <#440974277894864906> for bot use and <#488321784781996032> to help navigate the site.\n\nLet us know if you need anything by sending a personal message to <@590906101554348053>.\n\n**Thank you, and enjoy your stay!**\n*- Legendary Alliance Community*")
                        if showCR and showBS:
                            saveOtherGame = await setupChannel.send(embed=discord.Embed(colour=discord.Colour.blue(), description="Would you like to save Clash Royale account as well?"))
                            await saveOtherGame.add_reaction("<:yesconfirm:595535992329601034>")
                            await saveOtherGame.add_reaction("<:nocancel:595535992199315466>")
                            def otcheck(reaction, user):
                                return user == member and str(reaction.emoji) in ["<:yesconfirm:595535992329601034>", "<:nocancel:595535992199315466>"]
                            try:
                                reaction, _ = await self.bot.wait_for('reaction_add', check=otcheck, timeout=600)
                            except asyncio.TimeoutError:
                                repeat = False
                            if str(reaction.emoji) == "<:yesconfirm:595535992329601034>":
                                await appendLog("Save other game: Yes")
                                repeat = True
                                showBS = False
                            elif str(reaction.emoji) == "<:nocancel:595535992199315466>":
                                await appendLog("Save other game: No")
                                repeat = False
                        else:
                            repeat = False
                        
                    elif str(reaction.emoji) == "<:nocancel:595535992199315466>":
                        await appendLog(f"User's account: No")
                        repeat = True
                
                except brawlstats.errors.NotFoundError as e:
                    repeat = True
                    await setupChannel.send("No player with this tag found, try again!")
                    await appendLog(f":exclamation:Error occured: {str(e)}")
                except brawlstats.errors.RequestError as e:
                    repeat = True
                    await setupChannel.send(f"Brawl Stars API is offline, please try again later! ({str(e)})")
                    await appendLog(f":exclamation:Error occured: {str(e)}")
                except Exception as e:
                    repeat = True
                    await setupChannel.send("**Something went wrong, please send a personal message to <@590906101554348053> or try again!**")
                    await appendLog(f":exclamation:Error occured: {str(e)}")
                    
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
                    
                    visitorConfirmation = await setupChannel.send("Are you sure you want to join this server as a **visitor**? Connecting your Discord account to a Supercell game grants you unique features and access to personalized game content.")
                    await visitorConfirmation.add_reaction("<:yesconfirm:595535992329601034>")
                    await visitorConfirmation.add_reaction("<:nocancel:595535992199315466>")
                    def vcheck(reaction, user):
                        return user == member and str(reaction.emoji) in ["<:yesconfirm:595535992329601034>", "<:nocancel:595535992199315466>"]
                    reaction, _ = await self.bot.wait_for('reaction_add', check=vcheck)
                    if str(reaction.emoji) == "<:yesconfirm:595535992329601034>":
                        try:
                            roleVisitor = member.guild.get_role(472632693461614593)
                            await member.add_roles(roleVisitor)
                            await appendLog(f"Assigned roles: {roleVisitor.name}")
                        except discord.Forbidden:
                            await appendLog(f":exclamation:Couldn't change roles of this user. ({roleVisitor.name})")
                            repeat = False
                        await setupChannel.send("You have been given access to our general channels as a visitor. If you like to gain member - exclusive - access you can always restart the setup-procedure by doing `/setup`.\n\nWe hope you enjoy your stay here. If you might have any questions or require support don't refrain on sending <@590906101554348053> a DM and our staff will be with you shortly!\n\n**Thank you, and enjoy your stay!**\n*- Legendary Alliance*")
                        
                    elif str(reaction.emoji) == "<:nocancel:595535992199315466>":
                        repeat = True
                        
                elif str(reaction.emoji) == "<:HelpIcon:598803665989402624>":
                    await appendLog("Chosen option: Talk to support")
                    await setupChannel.send("You have stated that you require support, please send a DM to <@590906101554348053> and state the problem you require support for. Once received our staff will be with you shortly!")
                    await asyncio.sleep(5)
                    repeat = True
                    
                elif str(reaction.emoji) == "<:GoBack:598803665771429904>":
                    await appendLog("Chosen option: Go back to choosing game")
                    repeat = True
        try:
            await member.remove_roles(roleNewcomer)
            await appendLog(f"Removed roles: {roleNewcomer.name}")
        except discord.Forbidden:
            await appendLog(f":exclamation:Couldn't remove roles of this user. ({roleNewcomer.name})")
        
        await appendLog(f"**Finished**")
        await setupChannel.send(embed=discord.Embed(colour=discord.Colour.blue(), description="This channel will get deleted in 15 minutes!\n\nIf you have any questions or need help please send a personal message to <@590906101554348053>.".upper()))
        await asyncio.sleep(900)
        await setupChannel.delete(reason="Welcoming process finished.")
