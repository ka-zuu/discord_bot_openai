# OpenAIとやり取りするDiscord Bot

from dotenv import load_dotenv
from discord.ext import commands

import discord
import openai
import json
import os

load_dotenv()

# OpenAIの設定
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL=os.getenv("OPENAI_MODEL")
PROMPT = os.getenv("OPENAI_PROMPT")

# Discord Botの設定
intents = discord.Intents.default()
intents.typing = False  # typingを受け取らないように
intents.message_content = True
TOKEN = os.getenv("DISCORD_TOKEN")

# Botをインスタンス化
bot = commands.Bot(
    command_prefix="$",  # $コマンド名　でコマンドを実行できるようになる
    case_insensitive=True,  # コマンドの大文字小文字を区別しない ($hello も $Hello も同じ!)
    intents=intents,  # 権限を設定
)


# ログインしたらターミナルにログイン通知が表示される
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


# Botにメンションをした場合、OpenAIに問い合わせる
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        # メンションされたメッセージを取得
        msg = message.content.replace(f"<@!{bot.user.id}>", "").strip()

        # OpenAIに問い合わせ
        conversations = [{"role": "system", "content": PROMPT}, {"role": "user", "content": msg}]
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=conversations,
            max_tokens=2048,
            temperature=0.8,
        )

        # OpenAIの応答を送信
        await message.reply(response.choices[0]["message"]["content"].strip())



bot.run(TOKEN)
