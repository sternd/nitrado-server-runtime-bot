import requests
from requests.exceptions import HTTPError, Timeout
import discord


# Helper class to send Discord API requests
class DiscordRequests:
    DISCORD_BASE_URL = "https://discordapp.com/api/v7"
    DISCORD_MESSAGE_HISTORY = "/channels/:channel_id/messages"
    DISCORD_CREATE_MESSAGE = "/channels/:channel_id/messages"
    DISCORD_EDIT_MESSAGE = "/channels/:channel_id/messages/:message_id"

    TOKEN = None
    BOT_CLIENT_ID = None

    def __init__(self, config):
        if 'auth_token' not in config or config['token'] is None:
            raise Exception('Missing Discord Token')
        elif 'bot_client_id' not in config or config['bot_client_id'] is None:
            raise Exception('Missing Bot Client ID')

        self.TOKEN = config['token']
        self.BOT_CLIENT_ID = config['bot_client_id']

    # Send a Discord API request
    def sendDiscordRequest(self, action, url, params=None):
        # Do request here

        auth_token = f'Bot {self.TOKEN}'

        try:
            if action == 'GET':
                response = requests.get(url, timeout=15, headers={"Authorization": auth_token})
            elif action == 'POST':
                response = requests.post(url, timeout=10, headers={"Authorization": auth_token}, json=params)
            elif action == 'PATCH':
                response = requests.patch(url, timeout=10, headers={"Authorization": auth_token}, json=params)
            else:
                raise Exception(f'Attempting to send request with unknown action: {action}')

            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred for {id}: {http_err}')
        except Timeout as timeout:
            print(f'HTTP timeout occurred for {id}: {timeout}')
        except Exception as err:
            print(f'Other error occurred for {id}: {err}')
        else:
            return response.json()

        return None

    # Get message ID of most recent message sent by bot
    def getLastMessageByBot(self, channel_id):
        # Make request for message history
        # Parse message ID
        url = self.DISCORD_BASE_URL + self.DISCORD_MESSAGE_HISTORY.replace(':channel_id', channel_id, 1)

        response = self.sendDiscordRequest('GET', url)

        if response is None:
            return None

        for message in response:
            if message["author"]["id"] != self.BOT_CLIENT_ID:
                continue

            return message

        return None

    # Edit an existing Rich Embed message
    def editMessage(self, channel_id, message_id, data):
        # Make request to edit message
        url = self.DISCORD_BASE_URL + self.DISCORD_EDIT_MESSAGE.replace(':channel_id', channel_id, 1).replace(
            ':message_id', message_id, 1)

        response = self.sendDiscordRequest('PATCH', url, data)

        if response is None:
            return None

        return response

    # Create a new Rich Embed message
    def createMessage(self, channel_id, data):
        # Make request to edit message
        url = self.DISCORD_BASE_URL + self.DISCORD_CREATE_MESSAGE.replace(':channel_id', channel_id, 1)

        response = self.sendDiscordRequest('POST', url, data)

        if response is None:
            return None

        return response

    # Create an initial connection to Discord to allow future messages
    # Only needs to be called once per Discord server
    def intialConnection(self):
        client = discord.Client()

        @client.event
        async def on_ready():
            print('Closing connection')
            await client.close()
            return None

        client.run(self.TOKEN)
