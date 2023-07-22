import pytest
from unittest.mock import Mock, call


# 返信がない場合のテスト
@pytest.mark.asyncio
async def test_create_response_no_reference():
    # テスト用のメッセージを作成（参照メッセージはありません）
    mock_message = Mock()
    mock_message.content = "Test message"
    mock_message.reference = None

    # テスト用のbotを作成
    bot = Mock()
    bot.user = "Bot user"

    # OpenAI APIのmockを作成
    openai.ChatCompletion.create = Mock()
    openai.ChatCompletion.create.return_value = {
        "choices": [{"message": {"content": "Response from OpenAI"}}]
    }

    # テスト対象関数を呼び出し
    response = await your_module.create_response(mock_message)

    # 戻り値の確認
    assert response == "Response from OpenAI"

    # fetch_messageが呼ばれていないことを確認
    mock_message.channel.fetch_message.assert_not_called()

    # OpenAI APIが正しいパラメータで呼び出されたことを確認
    openai.ChatCompletion.create.assert_called_once_with(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": "Test message"},
        ],
        max_tokens=2048,
        temperature=0.8,
    )


# 返信が1回ある場合のテスト
@pytest.mark.asyncio
async def test_create_response_with_one_reference():
    # 参照メッセージとそれに対する返信を作成
    mock_referenced_message = Mock()
    mock_referenced_message.content = "Referenced message"
    mock_message = Mock()
    mock_message.content = "Test message"
    mock_message.reference = Mock()
    mock_message.reference.resolved = mock_referenced_message

    # テスト用のbotを作成
    bot = Mock()
    bot.user = "Bot user"

    # OpenAI APIのmockを作成
    openai.ChatCompletion.create = Mock()
    openai.ChatCompletion.create.return_value = {
        "choices": [{"message": {"content": "Response from OpenAI"}}]
    }

    # テスト対象関数を呼び出し
    response = await your_module.create_response(mock_message)

    # 戻り値の確認
    assert response == "Response from OpenAI"

    # OpenAI APIが正しいパラメータで呼び出されたことを確認
    openai.ChatCompletion.create.assert_called_once_with(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": "Referenced message"},
            {"role": "assistant", "content": "Test message"},
        ],
        max_tokens=2048,
        temperature=0.8,
    )


# 返信が2回ある場合のテスト
@pytest.mark.asyncio
async def test_create_response_with_two_references():
    # 参照メッセージとそれに対する返信を作成
    mock_referenced_message1 = Mock()
    mock_referenced_message1.content = "First referenced message"
    mock_referenced_message2 = Mock()
    mock_referenced_message2.content = "Second referenced message"

    mock_message = Mock()
    mock_message.content = "Test message"
    mock_message.reference = Mock()
    mock_message.reference.resolved = mock_referenced_message2

    # テスト用のbotを作成
    bot = Mock()
    bot.user = "Bot user"

    # OpenAI APIのmockを作成
    openai.ChatCompletion.create = Mock()
    openai.ChatCompletion.create.return_value = {
        "choices": [{"message": {"content": "Response from OpenAI"}}]
    }

    # fetch_messageをモック化して、最初の参照メッセージを返すように設定
    mock_message.channel.fetch_message = Mock(return_value=mock_referenced_message1)

    # テスト対象関数を呼び出し
    response = await your_module.create_response(mock_message)

    # 戻り値の確認
    assert response == "Response from OpenAI"

    # fetch_messageが正しいパラメータで呼び出されたことを確認
    mock_message.channel.fetch_message.assert_called_once_with(
        mock_referenced_message2.reference.message_id
    )

    # OpenAI APIが正しいパラメータで呼び出されたことを確認
    openai.ChatCompletion.create.assert_called_once_with(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": "First referenced message"},
            {"role": "assistant", "content": "Second referenced message"},
            {"role": "user", "content": "Test message"},
        ],
        max_tokens=2048,
        temperature=0.8,
    )
