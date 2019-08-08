from .coaching import CoachingCog

async def setup(bot):
  cog = CoachingCog(bot)
  await cog.initialize()
  bot.add_cog(cog)
