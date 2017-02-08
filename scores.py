"""
This file contains implementation of different score functions
"""
import math

from isolation import isolation


def score_aggressive_diff(game, player):
    """Heuristic function with difference between active player's legal moves and opponent player's legal moves.
     Modified to be more aggressive (1x for own moves, 2x for opposite moves)

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """
    assert isinstance(game, isolation.Board)

    return float(len(game.get_legal_moves(player)) - 2 * len(game.get_legal_moves(game.get_opponent(player))))


def score_safe_diff(game, player):
    """Heuristic function with difference between active player's legal moves and opponent player's legal moves.
     Modified to be less aggressive (2x for own moves, 1x for opposite moves)

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """

    assert isinstance(game, isolation.Board)

    return float(2 * len(game.get_legal_moves(player)) - len(game.get_legal_moves(game.get_opponent(player))))


def score_sq_distance_to_center(game, player):
    """Heuristic function based on assumption that be closer to center is better

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """

    assert isinstance(game, isolation.Board)

    active_location = game.get_player_location(player)
    opponent_location = game.get_player_location(game.get_opponent(player))

    # get center of a game board
    x_center = game.height / 2
    y_center = game.width / 2

    active_sq_dist_to_center = (active_location[0] - x_center) ** 2 + (active_location[1] - y_center) ** 2

    opp_sq_dist_to_center = (opponent_location[0] - x_center) ** 2 + (opponent_location[1] - y_center) ** 2

    active_sq_dist_to_center = max(0.5, active_sq_dist_to_center)
    opp_sq_dist_to_center = max(0.5, opp_sq_dist_to_center)

    # Far opponent from center - better for us. We are closer to the center - better for us
    score = opp_sq_dist_to_center / active_sq_dist_to_center

    return score


def score_center_plus_safe_diff(game, player):
    """Composite heuristic function based on `score_safe_diff` and `score_distance_to_center`,
    forces to maximise both scores by multiplying

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """

    return score_safe_diff(game, player) + math.sqrt(score_sq_distance_to_center(game, player))
