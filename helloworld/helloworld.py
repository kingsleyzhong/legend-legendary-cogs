from redbot.core import commands

class HWCog(commands.Cog):
  """Hello World test cog"""

  @commands.command()
  async def helloworld(self, ctx):
    """Prints hello world"""
    await ctx.send("Hello World")

  @commands.command()
  async def ripgupta(self, ctx, count, *, message):
    """Put in a sizeable number and put a message afterward"""
    int(count)
    gupta = 468209010978455552
    channel = 617525238392946699
    mloop = 0
    int(mloop)    
    while mloop > count:
      await channel.send("{} {}".format(gupta.mention, message))
      int(mloop)
      mloop = mloop + 1
  
