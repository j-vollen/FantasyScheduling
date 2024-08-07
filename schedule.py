import cvxpy as cp
from itertools import combinations
import numpy as np
import random


# flatten list of lists via list comprehension
def flatten(t):
    return [item for sublist in t for item in sublist]


# pop random item from list
def pop_random(lst):
    idx = random.randrange(0, len(lst))
    return lst.pop(idx)

## DEFINE SCRIPT INPUTS
# teams and number of games, respectively
numTeams, numWeeks = 10, 14
rivalry_week = 12
rivalry_week2 = 1
# users names, rivalry matchups, and map from users to teams if needed
users = np.array(["kevin", "jeremy", "robert", "miller", "simon", "joe", "greg", "justin", "sam", "chris"])
rivalries = [("jeremy", "greg"), ("kevin", "joe"), ("miller", "justin"), ("sam", "chris"), ("robert", "simon")]
divisions = {
    # First division
    "kevin": 1, "miller": 1, "jeremy": 1, "simon": 1, "sam": 1,
    # Second division
    "greg": 2, "chris": 2, "justin": 2, "robert": 2, "joe": 2}

# create out-of-division (OOD) matchups that play twice; use rivalries if ood, otherwise just pick randomly
ood_extra = [rivalry for rivalry in rivalries if divisions[rivalry[0]] != divisions[rivalry[1]]]
remaining_teams = flatten([[rivalry[0], rivalry[1]] for rivalry in rivalries if rivalry not in ood_extra])
remaining_div1 = [team for team in remaining_teams if divisions[team]==1]
remaining_div2 = [team for team in remaining_teams if divisions[team]==2]
while ( len(remaining_div1) > 1 and len(remaining_div2) > 1 ) :
    rand1 = pop_random(remaining_div1)
    rand2 = pop_random(remaining_div2)
    tup = (rand1, rand2)
    ood_extra.append(tup)

user_team_map = {"kevin": "Historic Shi Tpa Town", 
                "chris": "Chef John",
                "justin": "Bottom Bitches", 
                "robert": "Ferrari Cake",
                "greg": "The Jagaloons",
                "simon": "The Slim Reapers",
                "joe": "Kenneth Walker Sr",
                "jeremy": "a pimp named slickback",
                "sam": "Guy Fieri",
                "miller": "Bobby Flay"}


# DEFINE DECISION VARIABLES
# dictionary with tuples (i,j) as keys and array of 14 cp variables as values
games = {key: cp.Variable(numWeeks, boolean=True) for key in combinations(users, 2)}

# CONSTRAINTS
# 1: one game per team per week
one_game_constraints = []
for user in users:
    # for each team, pick out the matchups they're involved in
    matchups = {key: value for key, value in games.items()
                if key[0] == user or key[1] == user}
    # sum of all matchups must be equal to 1 for each individual week, thus we get numWeeks constraints
    new_constraints = [cp.sum([value[week] for key, value in matchups.items()]) == 1
                       for week in range(numWeeks)]
    one_game_constraints.extend(new_constraints)

# 2: rivals must play each other in selected rivalry week;
# note this will have bugs if the rivalry tuples are not in the lexicographic order of 'users' list
rivalry_constraints = [games[rivalry][rivalry_week-1] == 1 for rivalry in rivalries]
# added a second rivalry week. This didn't work last year.. I think it has to do with the number of rivalries are divisional
rivalry_constraints2 = [games[rivalry][rivalry_week2-1] == 1 for rivalry in rivalries]

# 3: game spacing constraints
# maximum one game between any matchup of two teams in 3-week span
spacing_constraints = [schedule[week]+schedule[week+1]+schedule[week+2]+schedule[week+3] <= 1
                       for week in range(numWeeks-3) # looping over weeks
                       for schedule in games.values()] # looping over matchups' schedules

# 4: division constraints
# in-division play twice total; out-of-division play once total except for those "extra" out-of-division matchups
# made this an inequality, otherwise cvxpy says infeasible (even tho it is satisfied by equality in the solution)
division_constraints = \
    [cp.sum(weeks) >= 1 + (divisions[matchup[0]] == divisions[matchup[1]]) + (matchup in ood_extra)
     for matchup, weeks in games.items()]

constraints = flatten([one_game_constraints, rivalry_constraints, rivalry_constraints2, spacing_constraints, division_constraints])

# SOLVE
# create problem, objective function is trivial
scheduling_problem = \
    cp.Problem(cp.Maximize(0),
               constraints)
scheduling_problem.solve(solver='GLPK_MI', verbose=True)

# debugging
# total_ct = 0
# for matchup, schedule in games.items():
#     count = np.sum([schedule[week].value for week in range(numWeeks)])
#     print(str(matchup) + ': ' + str(np.sum([schedule[week].value for week in range(numWeeks)])) + '\n')
#     total_ct += count
# print(str(total_ct) + '\n')

# WRITE
f = open('result.txt', 'r+')
f.seek(0)
f.truncate()
for week in range(numWeeks):
    f.writelines(['Week ', str(week+1), ' Matchups:\n'])
    for matchup, schedule in games.items():
        if schedule[week].value == 1:
            matchup_str = [user_team_map[matchup[0]], ' vs. ',
                   user_team_map[matchup[1]], '\n']
            f.writelines(matchup_str)
    f.write('\n')
f.close()

# To-dos:
# since there is no unique solution, add functionality so we can set a seed and get a different solution