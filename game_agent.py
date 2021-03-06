"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
from operator import itemgetter

from isolation import isolation
from scores import *


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


NO_MOVE = (-1, -1)


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    assert isinstance(game, isolation.Board)
    # use selected heuristic here
    utility = game.utility(player)
    if not utility == 0:
        return utility

    # Implementations of different scores could be find in ``scores.py```
    return score_center_plus_safe_diff(game, player)


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        # Return if there are no legal moves
        if not legal_moves:
            return NO_MOVE

        # opening book
        if not game.get_player_location(game.active_player):
            legal_moves = game.get_legal_moves()
            move = (game.height // 2, game.width // 2)
            if move in legal_moves:
                return move
            # it's a second turn - should be fine to put just near in the center
            move = (move[0] - 1, move[1])
            if move in legal_moves:
                return move

        last_completed_search = None
        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            if self.search_depth > 0:
                for depth in range(1, self.search_depth + 1):
                    last_completed_search = getattr(self, self.method)(game, depth)
            else:
                depth = 1
                results = []
                while True:
                    last_completed_search = getattr(self, self.method)(game, depth)
                    results.append(last_completed_search)
                    depth += 1

        except Timeout:
            # TODO Handle any actions required at timeout, if necessary
            pass
        return last_completed_search[1]

    def terminal_score(self, game, maximizing_player):
        """Implement a function that returns score of the current game state for a maximizing player
        immediately without making any board permutations.
        It's a Utility function from AIMA

        :param game: isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state
        :param maximizing_player: bool
            Flag indicating whether the current search depth and active player corresponds to a
            maximizing layer (True) or a minimizing layer (False)
        :return: float
            score function value for the current game state
        """
        active_player = game.active_player
        # we calculate score/utilization function for maximizing player, not for an active one
        player_to_compute_terminal_score = active_player if maximizing_player else game.get_opponent(active_player)
        return self.score(game, player_to_compute_terminal_score)
                                 
    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """

        assert isinstance(game, isolation.Board)

        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        active_player = game.active_player
        select_func = max if maximizing_player else min

        legal_moves = game.get_legal_moves(active_player)
        if not legal_moves:
            return 0, NO_MOVE

        if depth > 0:
            # select max or min score depends on `maximizing_player`
            best_move = select_func(
                # we call minimax for each possible move from legal moves, make tuples of
                # <score from minimax, related move>, move from minimax result is not used
                [(self.minimax(game.forecast_move(move), depth - 1, not maximizing_player)[0], move)
                 for move in game.get_legal_moves(active_player)],
                key=itemgetter(0))
            return best_move
        else:
            return self.terminal_score(game, maximizing_player), NO_MOVE

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        assert isinstance(game, isolation.Board)

        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        active_player = game.active_player

        legal_moves = game.get_legal_moves(active_player)
        if not legal_moves:
            return 0, NO_MOVE

        if depth > 0:
            legal_moves = game.get_legal_moves(active_player)
            parent_value = float("-inf") if maximizing_player else float("+inf")
            for move in legal_moves:
                move_value = self.alphabeta(game.forecast_move(move), depth - 1, alpha, beta, not maximizing_player)[0]
                if maximizing_player:
                    # Max-Value from AIMA
                    if move_value > parent_value:
                        parent_value = move_value
                        best_move = move
                    if move_value >= beta:
                        return move_value, move
                    alpha = max(alpha, parent_value)
                else:
                    # Min-Value from AIMA
                    if move_value < parent_value:
                        parent_value = move_value
                        best_move = move
                    if parent_value <= alpha:
                        return move_value, move
                    beta = min(beta, parent_value)
            return parent_value, best_move
        else:
            return self.terminal_score(game, maximizing_player), NO_MOVE
