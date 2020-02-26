# bot.py
import os

import discord
from dotenv import load_dotenv
import json
from datetime import datetime
from DiscordRequests import DiscordRequests
from NitradeoRequests import NitradoRequests

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_CLIENT_ID = os.getenv('BOT_CLIENT_ID')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# Handler for AWS Lambda to run the application
def handler(event, context):
    discord_requests = DiscordRequests({"token": TOKEN, "bot_client_id": BOT_CLIENT_ID})

    if event == "initial-connection":
        discord_requests.intialConnection()
        return {
            'message': "Successfully initialized connection"
        }

    with open('nitrapi_account_config.json') as json_file:
        nitrapi_account_config = json.load(json_file)

    with open('gameserver_colors.json') as json_file:
        gameserver_colors = json.load(json_file)

    nitrapi_config = json.loads(nitrapi_account_config)

    gameserver_runtimes = {}
    for account in nitrapi_config['nitrado_accounts']:
        auth_token = account["auth_token"]

        services = NitradoRequests.getServices(auth_token)

        gameserver_runtimes.update(parseRuntimeForServices(services, account["gameservers"]))

    embed = createEmbed(gameserver_runtimes)

    colour = discord.Colour(0x7ed321)

    embed.__setattr__('timestamp', datetime.utcnow())
    embed.__setattr__('colour', colour)

    dict_embed = embed.to_dict()

    last_message = discord_requests.getLastMessageByBot(CHANNEL_ID)

    if last_message is None:
        discord_requests.createMessage(CHANNEL_ID, {"embed": dict_embed})
    else:
        discord_requests.editMessage(CHANNEL_ID, last_message["id"], {"embed": dict_embed})

    return {
        'message': "Success"
    }


def parseRuntimeForServices(services, gameservers):
    if services is None:
        return []

    gameserver_runtimes = {}
    for service in services:
        gameserver_name = ""
        for gameserver in gameservers:
            if service["id"] == gameserver["gameserver_id"]:
                if not gameserver["enabled"]:
                    break
                gameserver_name = gameserver["gameserver_name"]

        if gameserver_name == "":
            continue

        if service["suspending_in"] is None:
            continue

        gameserver_runtimes[gameserver_name] = {
            "runtime": service["suspending_in"],
            "boost_code": gameserver["boost_code"]
        }

    return gameserver_runtimes


def createEmbed(gameserver_runtimes):

    embed = discord.Embed(title="Valkyrie Server Runtimes", colour=discord.Colour(0xf8e71c),
                          url="https://github.com/sternd/nitrado-server-runtime-bot",
                          description="A visualization of the remaining server runtimes. This channel will be updated daily.")

    server_icon = os.getenv('SERVER_ICON')

    embed.set_thumbnail(
        url=server_icon)
    embed.set_footer(text="Updated",
                     icon_url=server_icon)

    for key in gameserver_runtimes:
        embed = addGameserverRuntimeToEmbed(embed, key, gameserver_runtimes[key]['runtime'], gameserver_runtimes[key]['boost_code'])

    return embed


def addGameserverRuntimeToEmbed(embed, server_name, runtime, boost_code):
    formatted_message = 'Remaining Time: ' + convertSecondsToDays(runtime) + "\n" + f'Boost Code: {boost_code}'
    embed.add_field(name='**' + server_name + '**', value=formatted_message, inline=True)
    return embed

def convertSecondsToDays(seconds):
    day_in_seconds = 86400
    days_boosted = round(seconds / day_in_seconds, 1)

    day_text = 'day'
    if days_boosted >= 2:
        day_text = 'days'

    return f'{days_boosted} {day_text}'

# FOR TESTING
# handler(None, None)
# handler('initial-connection', None)
# handler('slow-mode', None)
