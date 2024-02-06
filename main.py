from fastapi import FastAPI, Request, HTTPException

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

from fastapi.responses import FileResponse

from gmail import Gmail
import os

# Line Bot config
accessToken = os.environ.get('LINE_ACCESS_TOKEN')
secret = os.environ.get('LINE_CHANNEL_SECRET')

app = FastAPI()

line_bot_api = LineBotApi(accessToken)
handler = WebhookHandler(secret)
   
@app.post("/")
async def echoBot(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameters")
    return "OK"

@handler.add(MessageEvent, message=(TextMessage))
def handling_message(event):
    replyToken = event.reply_token
    # messages = event.message.text
    messages = ""
    
    if "如何使用" in event.message.text :
        messages = """請依照下列步驟發送裝置驗證請求：
1. 打開 Netflix
2. 確認自己在『您的裝置尚未設為此帳戶的同戶裝置』頁面
3. 點選下方『暫時收看』
4. 點選本聊天室的『取得驗證碼』按鈕"""
        echoMessages = TextSendMessage(text=messages)
        line_bot_api.reply_message(reply_token=replyToken, messages=echoMessages)
        return False
    
    if "取得驗證碼" in event.message.text :
        messages = Gmail().get_url()

        if len(messages) > 0:
            notice_message = """
請依照下列步驟取得裝置驗證：
1. 點選上方網址
2. 輸入薛的 Netflix 帳密進行驗證
3. Enjoy your Netflix :)"""
            messages = f"{messages}{notice_message}"

        else:
            messages = '目前尚未收到驗證請求，請點選『如何使用』查看如何驗證裝置。'
            
        echoMessages = TextSendMessage(text=messages)
        line_bot_api.reply_message(reply_token=replyToken, messages=echoMessages)
        return False