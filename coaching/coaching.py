import discord
from redbot.core import commands
from redbot.core import Config, checks



STUDENT_ROLES = []
COACH_ROLES = []

class CoachingCog(commands.cog):
  """Coaching Request Cog"""
  
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command()
  async def setcoachrole(self, ctx):
    await ctx.send("What roles are coaches:")
  
  
  @commands.command(pass_context=True)
  async def coachreq(self, ctx):
    
    student = ctx.message.author
    
    msg_coaches = ("**Coaching Request:** \n"
                   "**Discord Name:** {}\n"
                   "**IGN:** {} \n"
                   "**Archetype / Deck to learn:** {}\n"
                   "**Timezone:** {} \n"
                   "**Time Avaliable:** {} \n"
                   "**Additional Information** {} \n"
                   "**Player Profile:**)
    
             
                   
