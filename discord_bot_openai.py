#!/usr/bin/env python3

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
MODEL = os.getenv("OPENAI_MODEL")
PROMPT = os.getenv("OPENAI_PROMPT")

# Discord Botの設定
intents = discord.Intents.default()
intents.typing = False  # typingを受け取らないように
intents.message_content = True
TOKEN = os.getenv("DISCORD_TOKEN")

# Botをインスタンス化
bot = commands.Bot(
    command_prefix="$",  # $コマンド名　でコマンドを実行できるようになる
    case_insensitive=True,  # コマンドの大文字小文字を区別しない
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
        response = await create_response(message)
        await message.reply(response)


async def create_response(message):
    # 会話履歴を初期化
    conversations = [{"role": "system", "content": PROMPT}]
    # メッセージを会話履歴に追加
    conversations.insert(1, {"role": "user", "content": message.content})

    # メッセージが返信か再帰的に確認し、返信元のメッセージをすべて会話履歴に追加
    while message.reference:
        message = await message.channel.fetch_message(message.reference.message_id)
        # 返信がBotの場合はrole:assistant、ユーザーの場合はrole:userとして会話履歴に追加
        if message.author == bot.user:
            conversations.insert(1, {"role": "assistant", "content": message.content})
        else:
            conversations.insert(1, {"role": "user", "content": message.content})

    # 会話履歴の最初にPromptを追加
    conversations.insert(0, {"role": "system", "content": PROMPT})

    # OpenAIに問い合わせ
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=conversations,
        max_tokens=2048,
        temperature=0.8,
    )

    return response.choices[0]["message"]["content"]


bot.run(TOKEN)
