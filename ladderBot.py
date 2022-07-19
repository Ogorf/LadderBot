import os
import discord
import ladderdb
import ladderManager
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.environ['TOKEN']

intents = discord.Intents(messages=True, members=True, guilds=True, guild_messages=True)
discord_client = discord.Client(intents=intents)

DbAddress = os.environ['DBADDRESS']
DbUser = os.environ['DBUSER']
DbPassword = os.environ['DBPASSWORD']
DbDatabase = os.environ['DBDATABASE']

db = ladderdb.LadderDB(DbAddress, DbUser, DbPassword, DbDatabase)
manager = ladderManager.LadderManager(discord_client, db)

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    parsed, command, won, player1, player2, game_map = manager.parse_message(message)

    if not parsed:
        return

    if command == "report":
        await manager.execute_reported_game(won, player1, player2, game_map, message)

    if command == "ratings":
        await manager.print_ratings(message)

    if command == "history":
        await manager.print_match_history(10, message)


discord_client.run(TOKEN)
