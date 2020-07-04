import cvxpy as cp
from itertools import combinations
import numpy as np

# teams and number of games, respectively
numTeams, numWeeks = 10, 13
rivalry_week = 11
# users names, rivalry matchups, and map from users to teams if needed
users = np.array(["kevin", "jeremy", "robert", "miller", "simon", "joe", "greg", "justin", "sam", "chris"])
rivalries = np.array([("kevin", "jeremy"), ("robert", "miller"), ("simon", "joe"), ("greg", "justin"), ("sam", "chris")])
user_team_map = {"kevin": "Professor Teabag", "chris": "1503 Sequoia Trail",
                 "justin": "bottom bitches", "robert": "Bulgogi", "greg": "Burrito House",
                 "simon": "Champ", "joe": "Hareem Kunt", "jeremy": "Hike School",
                 "sam": "Pepper Brooks", "miller": "Salmon Sisters"}


## DEFINE DECISION VARIABLES
# a decision variable for each unique matchup possibility in each week
# games[i][j][k] indicates whether team i plays team j in week k
# games = [[[cp.Variable(boolean=True) for i in range(n)] for j in range(n)] for k in range(m)]
# dictionary with tuples (i,j) as keys and array of 13 cp variables as values
games = {key: cp.Variable(numWeeks, boolean=True) for key in combinations(users, 2)}

## CONSTRAINTS
# 1: one game per team per week
one_game_constraints = np.empty((0,numTeams*numWeeks))
for user in users:
    # for each team, pick out the matchups they're involved in
    matchups = {key: value for (key, value) in games if key[0] == user | key[1] == user}
    # sum of all matchups must be equal to 1 for each individual week, thus we get numWeeks constraints
    new_constraints = [np.sum([value[week] for key,value in matchups]) == 1 for week in range(numWeeks)]
    one_game_constraints = np.append(one_game_constraints, [new_constraints], axis=0)

# 2: rivals must play each other in selected rivalry week
rivalry_constraints = [games[rivalry][rivalry_week] == 1 for rivalry in rivalries]


# create problem, objective function is trivial
#scheduling_problem = cp.Problem(cp.Maximize(0), [self_play_constraints, spacing_constraints, rivalry_constraints, division_constraints])