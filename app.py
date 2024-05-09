from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import requests
import os
app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# API URL
API_URL = "your_api_url_here"

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if msg == "你好友有誰":
        # 回覆訊息
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="才不告訴你哩 哩"))
    elif msg == "我們甚麼時候加好友的":
        # 呼叫 API
        response = requests.get(API_URL)
        data = response.json()
        join_time = data.get("join_time", "Unknown")
        # 回覆訊息
        reply_msg = f"您加入好友的時間是：{join_time}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))
    elif msg =="我是誰":
        profile = line_bot_api.get_profile(event.source.user_id)
        user_name = profile.display_name
        user_id=profile.user_id
        picture_url=profile.picture_url
        status_message=profile.status_message
        reply_message = (
            f"Hi, {user_name}, 你好!\n"
            f"你的 userID: {user_id}\n"
            f"照片网址: {picture_url}\n"
            f"状态讯息: {status_message}"
        )

        # 回覆訊息
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
    else:
        # 回覆訊息
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))


@handler.add(PostbackEvent)
def handle_postback(event):
    print(event.postback.data)

@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
