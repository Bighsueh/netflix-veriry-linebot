## 透過 Gmail 自動抓取 Netflix 新裝置驗證碼, base on FastAPI, LineBotSDK, GmailAPI

需要在專案根目錄增加以下檔案
1. credentials.json
2. token.json
3. .env

參考網址：[ithome](https://ithelp.ithome.com.tw/m/articles/10282837)
其中1. 2. 需要從 GCP [授權網站](https://console.cloud.google.com/home/dashboard?project=gmail-api-333504) 獲取
而3. 依照.env.example 複製而來，並從 Line Developer 網頁取得 linebot的 channel secret 以及 access_token