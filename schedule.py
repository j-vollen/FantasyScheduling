import cvxpy as cp
from itertools import combinations
import numpy as np

## DEFINE SCRIPT INPUTS
# teams and number of games, respectively
numTeams, numWeeks = 10, 13
rivalry_week = 11
# users names, rivalry matchups, and map from users to teams if needed
users = np.array(["kevin", "jeremy", "robert", "miller", "simon", "joe", "greg", "justin", "sam", "chris"])
rivalries = [("kevin", "jeremy"), ("robert", "miller"), ("simon", "joe"), ("greg", "justin"), ("sam", "chris")]
divisions = {
    # First division
    "kevin": 1, "robert": 1, "joe": 1, "sam": 1, "chris": 1,
    # Second division
    "jeremy": 2, "miller": 2, "simon": 2, "justin": 2, "greg": 2}
user_team_map = {"kevin": "Professor Teabag", "chris": "1503 Sequoia Trail",
                 "justin": "bottom bitches", "robert": "Bulgogi", "greg": "Burrito House",
                 "simon": "Champ", "joe": "Hareem Kunt", "jeremy": "Hike School",
                 "sam": "Pepper Brooks", "miller": "Salmon Sisters"}


# DEFINE DECISION VARIABLES
# dictionary with tuples (i,j) as keys and array of 13 cp variables as values
games = {key: cp.Variable(numWeeks, boolean=True) for key in combinations(users, 2)}

# CONSTRAINTS
# 1: one game per team per week
#one_game_constraints = np.empty((0,numTeams*numWeeks))
one_game_constraints = []
for user in users:
    # for each team, pick out the matchups they're involved in
    matchups = {key: value for (key, value) in games
                if key[0] == user or key[1] == user}
    # sum of all matchups must be equal to 1 for each individual week, thus we get numWeeks constraints
    new_constraints = [cp.sum([value[week] for key, value in matchups]) == 1
                       for week in range(numWeeks)]
    one_game_constraints.extend(new_constraints)

# 2: rivals must play each other in selected rivalry week
rivalry_constraints = [games[rivalry][rivalry_week-1] == 1 for rivalry in rivalries]

# 3: game spacing constraints(teams should not play twice in any consecutive group of 3 weeks
# maximum one game between any matchup of two teams in 3-week span
spacing_constraints = [schedule[week]+schedule[week+1]+schedule[week+2] <= 1
                       for week in range(numWeeks-2) # looping over weeks
                       for schedule in games.values()] # looping over matchups' schedules

# 4: division constraints (in-division play twice total; out-of-division play once total)
division_constraints = \
    [cp.sum(weeks) == 1 + (divisions[matchup[0]] == divisions[matchup[1]])
     for matchup, weeks in games.items()]

constraint_lists = [rivalry_constraints, spacing_constraints, division_constraints]
constraints = [c for sublist in constraint_lists for c in sublist]

# SOLVE
# create problem, objective function is trivial
scheduling_problem = \
    cp.Problem(cp.Maximize(0),
               constraints)
scheduling_problem.solve(solver='GLPK_MI')


# WRITE
f = open('result.txt', 'r+')
for week in range(numWeeks):
    f.writelines(['Week ', str(week+1), ' Matchups:\n'])
    for matchup, schedule in games.items():
        if schedule[week].value == 1:
            matchup_str = [user_team_map[matchup[0]], ' vs. ',
                   user_team_map[matchup[1]], '\n']
            f.writelines(matchup_str)
    f.write('\n')
f.close()