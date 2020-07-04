import cvxpy as cp
import numpy as np

# users names, rivalry matchups, and map from users to teams if needed
users = np.array(["kevin", "jeremy", "robert", "miller", "simon", "joe", "greg", "justin", "sam", "chris"])
rivalries = [("kevin", "jeremy"), ("robert", "miller"), ("simon", "joe"), ("greg", "justin"), ("sam", "chris")]
user_team_map = {"kevin": "Professor Teabag", "chris": "1503 Sequoia Trail",
                 "justin": "bottom bitches", "robert": "Bulgogi", "greg": "Burrito House",
                 "simon": "Champ", "joe": "Hareem Kunt", "jeremy": "Hike School",
                 "sam": "Pepper Brooks", "miller": "Salmon Sisters"}
# teams and number of games, respectively
n, m = 10, 13

# a decision variable for each unique matchup possibility in each week
# games[i][j][k] indicates whether team i plays team j in week k
games = [[[cp.Variable(boolean=True) for i in range(n)] for j in range(n)] for k in range(m)]
# no team can play itself in any week
self_play_constraints = [games[i][i][k] == 0 for i in range(n) for k in range(m)]
#

# create problem, objective function is trivial
#scheduling_problem = cp.Problem(cp.Maximize(0), [self_play_constraints, spacing_constraints, rivalry_constraints, division_constraints])