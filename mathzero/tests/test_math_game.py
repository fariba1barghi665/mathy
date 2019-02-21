from ..math_game import MathGame
from ..environment_state import MathEnvironmentState, MathAgentState
from ..util import is_terminal_reward


def test_math_game_init():
    game = MathGame()
    assert game is not None
    state, complexity = game.get_initial_state()
    # Kind of arbitrary, ensure there's more than one term
    assert complexity >= 1
    assert state is not None
    # Assert about the structure a bit
    assert state.agent is not None
    assert state.width > 0


def test_math_game_win_conditions():

    expectations = [
        ("4x^2", True),
        ("100y * x + 2", True),
        ("10y * 10x + 2", False),
        ("10y + 1000y * (y * z)", False),
        ("4 * (5y + 2)", False),
        ("2", True),
        ("4x * 2", False),
        ("4x * 2x", False),
        ("4x + 2x", False),
        ("4 + 2", False),
        ("3x + 2y + 7", True),
        ("3x^2 + 2x + 7", True),
        ("3x^2 + 2x^2 + 7", False),
    ]

    # Valid solutions but out of scope so they aren't counted as wins.
    #
    # This works because the problem sets exclude this type of > 2 term
    # polynomial expressions
    out_of_scope_valid = []

    game = MathGame()
    for text, is_win in expectations + out_of_scope_valid:
        env_state = MathEnvironmentState(problem=text)
        reward = game.get_state_reward(env_state)
        assert text == text and is_terminal_reward(reward) == int(is_win)
