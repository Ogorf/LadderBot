import mysql.connector
import time


class LadderDB:
    def __init__(self, host: str, user: str, password: str, database:str):
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.mydb.cursor()

    def get_player_elo(self, player_tag: str):
        query = "SELECT U.Id, U.DiscordTag as Id, Rating FROM Users U inner join LadderElo L on U.Id = L.UserId " \
                "Where DiscordTag = '" + player_tag + "'"
        self.cursor.execute(query)

        results = self.cursor.fetchall()
        if len(results) == 0:
            return None, None
        else:
            return results[0][2], results[0][0]

    def update_player_elo(self, player_id, new_elo):
        query = "UPDATE LadderElo SET Rating = " + str(new_elo) + " WHERE UserId = " + str(player_id)
        self.cursor.execute(query)
        self.mydb.commit()

    def add_player(self, player: str, player_tag: str):
        query = "INSERT INTO Users (Username, PasswordHash, DiscordTag, Identificator, Confirmed, DateInserted) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (player, 0, player_tag, "", 1, time.strftime('%Y-%m-%d %H:%M:%S'))

        self.cursor.execute(query, values)
        self.mydb.commit()

        id = self.cursor.lastrowid

        query = "INSERT INTO LadderElo (UserId, Rating) VALUES (%s, %s)"
        values = (id, 1500)

        self.cursor.execute(query, values)
        self.mydb.commit()

    def get_player_tag(self, name: str):
        query = "SELECT DiscordTag FROM Users WHERE Username = '" + name + "' OR DiscordTag = '" + name + "'"
        self.cursor.execute(query)

        results = self.cursor.fetchall()
        if len(results) > 0:
            return results[0][0]
        else:
            return None

    def get_player_name(self, tag: str):
        query = "SELECT Username FROM Users WHERE DiscordTag = '" + tag + "'"
        self.cursor.execute(query)

        results = self.cursor.fetchall()

        if len(results) == 0:
            return None
        else:
            return results[0][0]

    def add_match_to_history(self, player1_id: int, player2_id: int, won: bool, map_name: str):
        query = "INSERT INTO MatchHistory (User1, User2, User1Won, DifficultySetting, MapName, DateReported) VALUES (%s,%s, %s, %s, %s, %s)"
        values = (player1_id, player2_id, won, 4, map_name, time.strftime('%Y-%m-%d %H:%M:%S'))

        self.cursor.execute(query, values)
        self.mydb.commit()

    def get_match_history(self, num_of_matches: int = 10):
        query = "SELECT U1.UserName as Usernam1, U2.UserName as Username2, User1Won, MapName FROM MatchHistory M " \
                "inner join Users U1 on User1 = U1.Id inner join Users U2 on User2 = U2.Id ORDER BY M.Id desc " \
                "Limit " + str(num_of_matches)

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return results

    def get_ratings(self):
        query = "SELECT Username, Rating FROM Users U inner join LadderElo E on U.Id = E.UserId ORDER BY Rating DESC"
        self.cursor.execute(query)

        results = self.cursor.fetchall()

        return results
