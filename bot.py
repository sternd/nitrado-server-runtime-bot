# bot.py
import os

import discord
from dotenv import load_dotenv
import json
from datetime import datetime
from DiscordRequests import DiscordRequests
from NitradoRequests import NitradoRequests

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
BOT_CLIENT_ID = os.getenv('BOT_CLIENT_ID')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# Handler for AWS Lambda to run the application
def handler(event, context):
    discord_requests = DiscordRequests({"auth_token": TOKEN, "bot_client_id": BOT_CLIENT_ID})
    nitrado_requests = NitradoRequests()

    if event == "initial-connection":
        discord_requests.intialConnection()
        return {
            'message': "Successfully initialized connection"
        }

    with open('nitrapi_account_config.json') as json_file:
        nitrapi_account_config = json.load(json_file)

    nitrapi_config = json.loads(nitrapi_account_config)

    gameserver_runtimes = {}
    for account in nitrapi_config['nitrado_accounts']:
        auth_token = account["auth_token"]

        services = nitrado_requests.getServices(auth_token)

        if "data" not in services:
            continue

        if "services" not in services["data"]:
            continue

        gameserver_runtimes.update(parseRuntimeForServices(services["data"]["services"], account["gameservers"]))

    colour = getColorByRuntimes(gameserver_runtimes)

    embed = createEmbed(gameserver_runtimes)

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
        boost_code = ""
        role_id = ""

        for gameserver in gameservers:
            if service["id"] == int(gameserver["gameserver_id"]):
                if not gameserver["enabled"]:
                    break
                gameserver_name = gameserver["gameserver_name"]
                boost_code = gameserver["boost_code"]
                role_id = gameserver["role_id"]

        if gameserver_name == "":
            continue

        if service["suspending_in"] is None:
            continue

        gameserver_runtimes[gameserver_name] = {
            "runtime": service["suspending_in"],
            "boost_code": boost_code,
            "role_id": role_id
        }

    return gameserver_runtimes


def createEmbed(gameserver_runtimes):

    embed = discord.Embed(title="Aftermath Server Runtimes",
                          url="https://github.com/sternd/nitrado-server-runtime-bot",
                          description="As we don’t require any payment system to play on the Aftermath cluster it is still an expensive venture to keep the cluster up and running. Any donations are greatly appreciated! All boosts can be done through the Nitrado app on your Xbox and PC. \n**This channel will be updated daily.**")

    server_icon = os.getenv('SERVER_ICON')

    embed.set_thumbnail(
        url=server_icon)
    embed.set_footer(text="Updated",
                     icon_url=server_icon)

    for key in gameserver_runtimes:
        embed = addGameserverRuntimeToEmbed(embed, key, gameserver_runtimes[key]['runtime'], gameserver_runtimes[key]['boost_code'], gameserver_runtimes[key]["role_id"])

    return embed


def addGameserverRuntimeToEmbed(embed, server_name, runtime, boost_code, role_id):
    formatted_message = 'Remaining Time: **' + convertSecondsToDays(runtime) + "**\n" + f'Boost Code: **{boost_code}**'

    if role_id == "":
        gameserver_identifier = f'{server_name}\n'
    else:
        gameserver_identifier = f'<@&{role_id}>\n'

    embed.add_field(name='\u200b', value=f'{gameserver_identifier}' + formatted_message, inline=False)
    return embed

def convertSecondsToDays(seconds):
    day_in_seconds = 86400
    days_boosted = round(seconds / day_in_seconds, 1)

    day_text = 'day'
    if days_boosted >= 2:
        day_text = 'days'

    return f'{days_boosted} {day_text}'


def getColorByRuntimes(gameserver_runtimes):
    lowest_runtime = None

    for key in gameserver_runtimes:
        if lowest_runtime is None:
            lowest_runtime = gameserver_runtimes[key]["runtime"]
        elif gameserver_runtimes[key]["runtime"] < lowest_runtime:
            lowest_runtime = gameserver_runtimes[key]["runtime"]

    color = None

    if lowest_runtime is None or lowest_runtime < 5:
        color = discord.Colour(0xd0021b)
    elif lowest_runtime < 15:
        color = discord.Color(0xf5a623)
    else:
        color = discord.Color(0x7ed321)

    return color


# FOR TESTING
# handler(None, None)
# handler('initial-connection', None)
