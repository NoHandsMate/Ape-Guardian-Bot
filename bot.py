import os
import discord
from Client.command_handler import bot
from Client.music_handler import Music
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot.add_cog(Music(bot))
bot.run(TOKEN)
