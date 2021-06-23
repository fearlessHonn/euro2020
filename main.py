import itertools
import pandas as pd
import numpy as np

parameters = ["Games", "Wins", "Draws", "Losses", "Goals", "Conceded goals", "Goal difference", "Points"]
games = dict()


def read_results(inp="results.txt"):
    global games
    with open(inp, "r") as results:
        results = results.read().replace("vs ", "").split("\n")
        results = [result.split(":") for result in results]
        results = {(result[0].split()[0], result[0].split()[1]): f"{result[1]}:{result[2]}" for result in results}

        games = results.copy()

        return games


class Group:
    def __init__(self, teams, inp=None):
        self.first, self.second, self.third, self.fourth = None, None, None, None
        self.third_params = None

        self.teams = teams
        self.remaining = []
        self.remaining_games()

        if inp is None:
            self.table = pd.DataFrame([[0 for i in range(8)] for i in range(4)], index=self.teams, columns=parameters)
        else:
            self.table = inp

    def remaining_games(self, teams=None):
        global games
        teams = self.teams if teams is None else teams
        self.remaining = []
        for game, result in games.items():
            if result == "-:-" and (game[0] in teams or game[1] in teams):
                self.remaining.append(game)

        return self.remaining

    def get_table(self):
        global games
        results = [[0 for i in range(8)] for i in range(4)]
        for game, result in games.items():
            if result != "-:-" and (game[0] in self.teams or game[1] in self.teams):
                g1 = int(list(result)[0])
                g2 = int(list(result)[2])
                td = g1 - g2

                results[self.teams.index(game[0])][0] += 1  # Updating Games
                results[self.teams.index(game[1])][0] += 1

                results[self.teams.index(game[0])][6] += td  # Updating goal difference
                results[self.teams.index(game[1])][6] -= td

                results[self.teams.index(game[0])][4] += g1  # Updating goals
                results[self.teams.index(game[1])][4] += g2

                results[self.teams.index(game[0])][5] += g2  # Updating conceded goals
                results[self.teams.index(game[1])][5] += g1

                if td > 0:  # Teams A wins
                    results[self.teams.index(game[0])][1] += 1
                    results[self.teams.index(game[1])][3] += 1

                    results[self.teams.index(game[0])][7] += 3

                if td == 0:
                    results[self.teams.index(game[0])][2] += 1
                    results[self.teams.index(game[1])][2] += 1

                    results[self.teams.index(game[0])][7] += 1
                    results[self.teams.index(game[1])][7] += 1

                if td < 0:  # Teams A wins
                    results[self.teams.index(game[1])][1] += 1
                    results[self.teams.index(game[0])][3] += 1

                    results[self.teams.index(game[1])][7] += 3

        self.table = pd.DataFrame(results, index=self.teams, columns=parameters)
        return self.table

    def sort_table(self):
        global games
        self.table = self.table.sort_values(by="Points", ascending=False)
        points = [i[7] for i in self.table.values]
        sames = []
        for i, val in enumerate(points):
            if points.count(val) > 1:
                sames.append([i for i, a in enumerate(points) if a == val])

        if sames:
            sames = [s for i, s in enumerate(sames) if s not in sames[i + 1:]]
            teams = list(self.table.index.values)
            for same in sames:
                try:
                    team1, team2 = teams[same[0]], teams[same[1]]
                    res = games[(team1, team2)]
                except KeyError:
                    try:
                        team1, team2 = teams[same[1]], teams[same[0]]
                        res = games[(team1, team2)]
                    except KeyError:
                        res = "-:-"
                        self.check_goal_difference(same[0], same[1])
                if res != "-:-":
                    g1 = int(list(res)[0])
                    g2 = int(list(res)[2])
                    td = g1 - g2

                    if td > 0:  # Teams A wins
                        pass

                    elif td == 0:  # Draw
                        self.check_goal_difference(same[0], same[1])

                    elif td < 0:  # Teams B wins
                        self.swap_rows(same[0])

                else:
                    self.check_goal_difference(same[0], same[1])

        return self.table

    def swap_rows(self, index):
        rows = list(self.table.index)
        rows = rows[:index] + [rows[index + 1]] + [rows[index]] + rows[index + 2:]
        self.table.index = rows

        row1, row2 = list(self.table.iloc[index]), list(self.table.iloc[index + 1])
        self.table.iloc[index], self.table.iloc[index + 1] = row2, row1

    def check_goal_difference(self, team_index_1, team_index_2):
        goal_differences = [i[6] for i in self.table.values]
        goal_difference_team1 = goal_differences[team_index_1]
        goal_difference_team2 = goal_differences[team_index_2]
        if goal_difference_team1 > goal_difference_team2:
            pass

        elif goal_difference_team1 == goal_difference_team2:
            self.check_total_goals(team_index_1, team_index_2)

        elif goal_difference_team1 < goal_difference_team2:
            self.swap_rows(team_index_1)

    def check_total_goals(self, team_index_1, team_index_2):
        goals = [i[4] for i in self.table.values]
        goals_team1 = goals[team_index_1]
        goals_team2 = goals[team_index_2]
        if goals_team1 > goals_team2:
            pass

        elif goals_team1 == goals_team2:
            raise NotImplementedError("Can't decide which team is better")

        elif goals_team1 < goals_team2:
            self.swap_rows(team_index_1)

    def placements(self):
        i = self.table.index
        self.first, self.second, self.third, self.fourth = i[0], i[1], i[2], i[3]
        self.third_params = self.table.iloc[2]


groups = [Group(teams=["Turkey", "Italy", "Wales", "Switzerland"]),
          Group(teams=["Denmark", "Finland", "Belgium", "Russia"]),
          Group(teams=["Netherlands", "Ukraine", "Austria", "North-Macedonia"]),
          Group(teams=["England", "Croatia", "Scotland", "Czech-Republic"]),
          Group(teams=["Spain", "Sweden", "Poland", "Slovakia"]),
          Group(teams=["Hungary", "Portugal", "France", "Germany"])]


def calculate_groups():
    global games
    thirds = []
    thirds_params = []
    direct_qualification = []
    for group in groups:
        group.games = games
        group.get_table()
        group.sort_table()

        group.placements()
        thirds.append(group.third)
        thirds_params.append(group.third_params)
        direct_qualification.append(group.first)
        direct_qualification.append(group.second)

    input = pd.DataFrame(thirds_params, index=thirds, columns=parameters)
    group_of_thirds = Group(teams=thirds, inp=input)
    group_of_thirds.sort_table()

    best_thirds = [group_of_thirds.first, group_of_thirds.second, group_of_thirds.third, group_of_thirds.fourth]

    qualified = direct_qualification + best_thirds


def is_qualified(country):
    return country in qualified


def generate_possible_results(r=6):
    possible_results = [f"{a}:{b}" for a in range(r) for b in range(r)]
    return possible_results


def is_qualification_possible(country):
    global games
    remaining_games = [i for sub in [g.remaining_games() for g in groups] for i in sub]
    print(remaining_games)
    for game in remaining_games:
        for result in generate_possible_results():
            games[game] = result


generate_possible_results()
is_qualification_possible("a")

if __name__ == "__main__":
    read_results()
    calculate_groups()
