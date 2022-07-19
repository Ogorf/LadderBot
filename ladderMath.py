def expected_score(player_rating: float, opponent_rating: float) -> float:
    """returns expected score, which is also the probabilty of winning"""

    exp_score = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))

    return exp_score


def new_ratings(rating_winner: float, rating_loser: float, K: float = 40):
    """calculates and returns ratings based on basic elo formula"""

    exp_score_winner = expected_score(rating_winner, rating_loser)
    rating_change = K * (1 - exp_score_winner)

    return rating_winner + rating_change, rating_loser - rating_change

def calculate_new_elo(player1_elo: float, player2_elo: float, won) -> float:
    if won:
        player1_elo, player2_elo = new_ratings(player1_elo, player2_elo)
    else:
        player2_elo, player1_elo = new_ratings(player2_elo, player1_elo)

    return player1_elo, player2_elo
