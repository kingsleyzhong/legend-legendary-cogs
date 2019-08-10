import discord
from redbot.core import commands
from redbot.core import Config, checks



STUDENT_ROLES = []
COACH_ROLES = []

class CoachingCog(commands.Cog):
  """Coaching Request Cog"""
  
  def __init__(self, bot):
    self.bot = bot
  
  @commands.command()
  async def setcoachrole(self, ctx):
    await ctx.send("What roles are coaches:")
  
  @commands.has_any_role(*STUDENT_ROLES)
  @commands.command(pass_context=True)
  async def coachreq(self, ctx):
    
    
    student = ctx.message.author
    await ctx.send("Let's move to DM")
    await student.send("Lets start! You can stop anytime by typing \"stop\". ")
    
    msg_coaches = ("**Coaching Request:** \n"
                   "**Discord Name:** {}\n"
                   "**IGN:** {} \n"
                   "**Archetype / Deck to learn:** {}\n"
                   "**Timezone:** {} \n"
                   "**Time Avaliable:** {} \n"
                   "**Additional Information** {} \n"
                   "**Player Profile:**")

    
    @commands.command()
    async def coachreview(self, ctx):
      author = cta.message.author
      await ctx.send("Please check your DM's")
      await author.send("Welcome to coaching review")
    
             
                   
