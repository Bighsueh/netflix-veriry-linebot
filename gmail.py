import os.path
import base64
import re
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Gmail():
    def list_latest_messages(self, service, user_id='me', days_back=7):
        try:
            # Calculate the date 'days_back' days ago
            cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
            cutoff_date_str = cutoff_date.strftime("%Y/%m/%d")

            # Build a query string to get emails after the specified date
            query = f"after:{cutoff_date_str}"
            
            response = service.users().messages().list(userId=user_id, q=query).execute()
            messages = response.get('messages', [])
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')

    def get_message(self, service, user_id='me', message_id=''):
        try:
            message = service.users().messages().get(userId=user_id, id=message_id).execute()
            return message
        except HttpError as error:
            print(f'An error occurred: {error}')

    def get_url(self):
        # Define the required scopes
        SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

        # Load credentials from file if available
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If credentials are not valid or don't exist, initiate the authentication flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=creds)
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

        except HttpError as error:
            print(f"An error occurred: {error}")

        # List the latest messages and process each one
        list_latest_messages = self.list_latest_messages(service)
            
        for message in list_latest_messages:
            message_details = self.get_message(service, message_id=message['id'])
            
            current_snippet = message_details.get('snippet')
            
            if "Netflix" in current_snippet and "碼" in current_snippet:
                break
                
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()

        # Extract information from the email body
        for p in msg["payload"]["parts"]:
            if p["mimeType"] in ["text/plain", "text/html"]:
                html_content = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8")

                access_code_match = re.search(r'nftoken=([^&]+)', html_content)
                message_guid_match = re.search(r'messageGuid=([^\]]+)', html_content)

                if access_code_match and message_guid_match:
                    access_code = access_code_match.group(1)
                    message_guid = message_guid_match.group(1)

                    # print("存取碼:", access_code)
                    # print("訊息GUID:", message_guid)
                    
                    return f"https://www.netflix.com/account/travel/verify?nftoken={access_code}&messageGuid={message_guid}"
            break
        
        return ''