import requests
import json
import os
from datetime import datetime
# pip install python-dotenv
from dotenv import load_dotenv

class FacebookPoster():
    """Creates a Post and publishes it to a Facebook page."""

    def __init__(self, app_name, app_id, user_id, user_access_token, app_secret):
        """Generates all necessary IDs and tokens necessary for posting."""

        load_dotenv()

        # The name of the App
        self.app_name = os.getenv("APP_NAME")
        # App ID can be found in the Meta Developers Dashboard
        self.app_id = os.getenv("APP_ID")
        # https://www.wikihow.com/Find-a-User-ID-on-Facebook
        self.user_id = os.getenv("USER_ID")
        # To get the App Secret, go here: https://developers.facebook.com/apps
        # Select the desired app
        # On the left panel, go to Settings -> Basic
        # The App Secret is available there
        self.app_secret = os.getenv("APP_SECRET")

        # Necessary steps:
        # - Get a short-lived user access token
        #       Can be done through the GraphQL
        # Valid for one day
        self.user_access_token = os.getenv("USER_ACCESS_TOKEN")

        # - Get the Long-lived User Access Token
        #       Is valid for 60 days
        self.long_access_token = self.get_long_lived_user_access_token()


    def make_get_request(self, url):
        """Makes a GET request and returns a formatted response content."""

        response = requests.get(url)
        content = json.loads(response.content)

        return content

    def get_long_lived_user_access_token(self):
        """Gets he long lived user access token. Valid for 60 days."""

        storage_file = 'storage_long_token.txt'
        current_date = datetime.now().date()


        # Checks if there is a previously stored long-lived access token and
        # the date at which it was generated.
        # If the access token is still valid, it's returned.
        # If it isn't, a new one is generated and subsequently stored.
        if os.path.exists(storage_file) and os.path.getsize(storage_file) > 0:
            with open(storage_file, "r") as file:
                date_token = file.readline().strip()
                access_token = file.readline().strip()
            
            parsed_date = datetime.strptime(date_token, "%Y-%m-%d").date()

            date_difference = (parsed_date - current_date).days

            is_within_59_days = date_difference >= -59

            if is_within_59_days:
                return access_token

        url = f"https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={self.app_id}&client_secret={self.app_secret}&fb_exchange_token={self.user_access_token}"

        content = self.make_get_request(url)

        # Writes the new long-lived access token to the storage file.
        # If the file doesn't exist, it creates it.
        # The date is written in the format YYYY-MM-DD.
        with open(storage_file, "a+") as file:
            current_date_str = current_date.strftime("%Y-%m-%d")
            file.write(current_date_str + "\n")
            file.write(content['access_token'] + "\n")

        return content['access_token']

if __name__ == '__main__':
    fb_poster = FacebookPoster()