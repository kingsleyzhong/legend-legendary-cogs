from .coaching import CoachingCog

async def setup(bot):
  cog = CoachingCog(bot)
  bot.add_cog(cog)
