# Discord Bot for Nitrado Server Runtimes

A simple Discord bot that retrieves the server runtimes for Nitrado servers and posts them to Discord.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.txt

```bash
pip3 install --target ./package -r requirements.txt
PYTHONPATH="PATH_TO_PACKAGE_FOLDER:$PYTHONPATH"
export PYTHONPATH
```

Create copy of "nitrapi_account_config_template.json" as "nitrapi_account_config.json".
Then add the auth_tokens for each of the Nitrado accounts into the config.

Create a copy of ".env_template" as ".env".
Add the values for: DISCORD_TOKEN, DISCORD_GUILD, and DISCORD_CHANNEL

## Usage
Make sure to uncomment the last line in bot.py to run locally.

```bash
python3 bot.py
```

## Lambda Deployment

```bash
cd project_root
cd ./package
zip -r9 ${OLDPWD}/nitrado-server-runtime-bot.zip .
cd ..
zip -g nitrado-server-runtime-bot.zip bot.py
zip -g nitrado-server-runtime-bot.zip nitrapi_account_config.json
zip -g nitrado-server-runtime-bot.zip DiscordRequests.py
zip -g nitrado-server-runtime-bot.zip NitradoRequests.py
aws lambda update-function-code --function-name nitrado-server-runtime-bot --zip-file fileb://nitrado-server-runtime-bot.zip
```

## Known Issues

## Contributing
Pull requests are welcome to the "master" branch. For major changes, please open an issue first to discuss what you would like to change.

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)