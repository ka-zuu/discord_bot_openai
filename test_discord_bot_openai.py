import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# テスト対象のモジュールをインポートします
from .discord_bot_openai import create_response


@pytest.mark.asyncio
@patch("openai.ChatCompletion.create", new_callable=AsyncMock)
async def test_create_response(mock_openai):
    # メッセージとチャンネル、ボットのユーザーを模擬化します
    mock_message = MagicMock()
    mock_channel = AsyncMock()
    mock_bot_user = MagicMock()

    # メッセージの参照をNoneに設定し、参照メッセージの取得をスキップします
    mock_message.reference = None
    # メッセージの内容を設定します
    mock_message.content = "Hello, world!"
    # メッセージがチャンネルから来たものであると設定します
    mock_message.channel = mock_channel
    # メッセージの送信者がボットでないことを設定します
    mock_message.author = MagicMock()
    mock_message.author.__eq__.side_effect = lambda x: x != mock_bot_user

    # OpenAI APIのレスポンスを模擬化します
    mock_openai.return_value.choices = [{"message": {"content": "Hi, there!"}}]

    response = await create_response(mock_message)

    # レスポンスが期待通りであることを確認します
    assert response == "Hi, there!"

    # OpenAI APIが正しい引数で呼び出されたことを確認します
    mock_openai.assert_called_once_with(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": "Hello, world!"},
        ],
        max_tokens=2048,
        temperature=0.8,
    )


@pytest.mark.asyncio
@patch("openai.ChatCompletion.create", new_callable=AsyncMock)
async def test_create_response_with_one_reference(mock_openai):
    # メッセージとチャンネル、ボットのユーザーを模擬化します
    mock_message = MagicMock()
    mock_channel = AsyncMock()
    mock_bot_user = MagicMock()

    # 参照メッセージを作成します
    mock_ref_message = MagicMock()
    mock_ref_message.content = "This is a referenced message!"
    mock_ref_message.reference = None  # 参照メッセージは他のメッセージを参照していません
    mock_ref_message.author = MagicMock()
    mock_ref_message.author.__eq__.side_effect = lambda x: x != mock_bot_user

    # メッセージが参照メッセージを参照していることを設定します
    mock_message.reference = MagicMock()
    mock_message.reference.message_id = 123
    mock_channel.fetch_message.return_value = mock_ref_message
    mock_message.content = "Hello, world!"
    mock_message.channel = mock_channel
    mock_message.author = MagicMock()
    mock_message.author.__eq__.side_effect = lambda x: x != mock_bot_user

    # OpenAI APIのレスポンスを模擬化します
    mock_openai.return_value.choices = [{"message": {"content": "Hi, there!"}}]

    response = await create_response(mock_message)

    assert response == "Hi, there!"

    mock_openai.assert_called_once_with(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": "This is a referenced message!"},
            {"role": "user", "content": "Hello, world!"},
        ],
        max_tokens=2048,
        temperature=0.8,
    )


@pytest.mark.asyncio
@patch("openai.ChatCompletion.create", new_callable=AsyncMock)
async def test_create_response_with_two_references(mock_openai):
    # メッセージとチャンネル、ボットのユーザーを模擬化します
    mock_message = MagicMock()
    mock_channel = AsyncMock()
    mock_bot_user = MagicMock()

    # 参照メッセージを2つ作成します
    mock_ref_message1 = MagicMock()
    mock_ref_message1.content = "This is the first referenced message!"
    mock_ref_message1.reference = MagicMock()  # このメッセージは他のメッセージを参照しています
    mock_ref_message1.reference.message_id = 456
    mock_ref_message1.author = MagicMock()
    mock_ref_message1.author.__eq__.side_effect = lambda x: x != mock_bot_user

    mock_ref_message2 = MagicMock()
    mock_ref_message2.content = "This is the second referenced message!"
    mock_ref_message2.reference = None  # このメッセージは他のメッセージを参照していません
    mock_ref_message2.author = MagicMock()
    mock_ref_message2.author.__eq__.side_effect = lambda x: x != mock_bot_user

    # fetch_messageの戻り値を設定します
    mock_channel.fetch_message.side_effect = [mock_ref_message1, mock_ref_message2]

    # メッセージが参照メッセージを参照していることを設定します
    mock_message.reference = MagicMock()
    mock_message.reference.message_id = 123
    mock_message.content = "Hello, world!"
    mock_message.channel = mock_channel
    mock_message.author = MagicMock()
    mock_message.author.__eq__.side_effect = lambda x: x != mock_bot_user

    # OpenAI APIのレスポンスを模擬化します
    mock_openai.return_value.choices = [{"message": {"content": "Hi, there!"}}]

    response = await create_response(mock_message)

    assert response == "Hi, there!"

    mock_openai.assert_called_once_with(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": "This is the second referenced message!"},
            {"role": "user", "content": "This is the first referenced message!"},
            {"role": "user", "content": "Hello, world!"},
        ],
        max_tokens=2048,
        temperature=0.8,
    )
