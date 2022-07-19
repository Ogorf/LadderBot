import discord
import ladderdb
import ladderMath


class LadderManager:
    def __init__(self, discord_client, db):
        self.discord_client = discord_client
        self.db = db

    def update_elo(self, player1_tag: str, player2_tag: str, won):
        player1_elo, player1_id = self.db.get_player_elo(player1_tag)
        player2_elo, player2_id = self.db.get_player_elo(player2_tag)

        if player1_elo is None or player2_elo is None:
            return None, None

        player1_elo, player2_elo = ladderMath.calculate_new_elo(player1_elo, player2_elo, won)

        self.db.update_player_elo(player1_id, player1_elo)
        self.db.update_player_elo(player2_id, player2_elo)

        return player1_elo, player2_elo, player1_id, player2_id

    def verify_player(self, name: str, message):
        tag = self.db.get_player_tag(name)

        if tag is not None:
            return tag, True, True

        guild = self.discord_client.get_guild(message.guild.id)
        member = guild.get_member_named(name)
        if member is None:
            return "", False, False
        else:
            return member.name + "#" + member.discriminator, True, False

    def parse_message(self, message: str):
        parsed = False
        won = False
        player2 = ""
        game_map = ""
        command = "report"

        words = message.content.split()

        if len(words) >= 6:
            if words[0] == "I":
                parsed = True
                # if words[1] == "won":
                #    won = True
                if words[1] == "lost":
                    won = False
                else:
                    parsed = False

                if words[4] != "on":
                    parsed = False

                if parsed:
                    player2 = words[3]
                    game_map = words[5]
                    for i in range(6, len(words)):
                        game_map += " " + words[i]
        else:
            if len(words) == 1:
                if words[0] == "!ratings":
                    command = "ratings"
                    parsed = True
                elif words[0] == "!history":
                    command = "history"
                    parsed = True

        player1 = message.author

        return parsed, command, won, player1, player2, game_map

    async def print_ratings(self, message):
        ratings = self.db.get_ratings()

        ratings_message = ""
        first_line = True

        for row in ratings:
            if not first_line:
                ratings_message += "\n"

            ratings_message += row[0] + ' ' + str(row[1])
            first_line = False

        await message.channel.send(ratings_message)

    async def print_match_history(self, num_of_matches: int, message):
        match_history = self.db.get_match_history(num_of_matches)

        history_message = ""
        first_line = True
        result = "won"

        for row in match_history:
            if not first_line:
                history_message += "\n"

            if row[2]:
                result = "won"
            else:
                result = "lost"

            history_message += row[0] + " " + result + " " + row[1] + " " + row[3]
            first_line = False

        await message.channel.send(history_message)

    async def execute_reported_game(self, won: bool, player1: str, player2: str, game_map: str, message):
        player2_tag, verified, registered = self.verify_player(player2, message)

        if not verified:
            return

        if message.author.name == player2_tag or message.author.name == player2:
            await message.channel.send("ERROR: The winning player is the losing player")
            return

        if not registered:
            self.db.add_player(player2, player2_tag)

        player1_tag, verified, registered = self.verify_player(str(player1), message)
        if not registered:
            self.db.add_player(player1.name, player1.name + "#" + player1.discriminator)

        player1_elo, player2_elo, player1_id, player2_id = self.update_elo(str(player1), player2_tag, won)

        self.db.add_match_to_history(player2_id, player1_id, not won, game_map)
        player2_name = self.db.get_player_name(player2_tag)

        reply_message = player1.name + " has a new rating of " + str(round(player1_elo)) + ", and " \
                        + player2_name + " has a new rating of " + str(round(player2_elo))

        await message.channel.send(reply_message)