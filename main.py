# OpenAIとやり取りするDiscord Bot

from dotenv import load_dotenv
from discord.ext import commands

import discord
import openai
import json
import os

# OpenAIの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# Discord Botの設定
intents = discord.Intents.default()
intents.typing = False  # typingを受け取らないように
intents.message_content = True
TOKEN = os.getenv("DISCORD_TOKEN")

# Botをインスタンス化
bot = commands.Bot(
    command_prefix="$", # $コマンド名　でコマンドを実行できるようになる
    case_insensitive=True, # コマンドの大文字小文字を区別しない ($hello も $Hello も同じ!)
    intents=intents # 権限を設定
)



@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

#@bot.event
#async def on_message(message):
#    if message.author == bot.user:
#        return
#
#    await message.channel.send('Hello!')

@bot.command(name='hello', description='挨拶を返します')
async def hello(ctx):
    await ctx.send('Hello!')


bot.run(TOKEN)