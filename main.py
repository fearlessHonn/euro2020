import itertools
import pandas as pd
import numpy as np

parameters = ["Games", "Wins", "Draws", "Losses", "Goals", "Conceded goals", "Goal difference", "Points"]


class Group:
    def __init__(self, a, b, c, d):
        self.team_a = a
        self.team_b = b
        self.team_c = c
        self.team_d = d

        self.teams = [self.team_a, self.team_b, self.team_c, self.team_d]
        self.games = {i: "-:-" for i in self.combinations()}
        self.remaining = []
        self.remaining_games()

        self.table = pd.DataFrame([[0 for i in range(8)] for i in range(4)], index=self.teams, columns=parameters)

    def combinations(self):
        return list(itertools.combinations(self.teams, 2))

    def remaining_games(self, teams=None):
        teams = self.teams if teams is None else teams
        self.remaining = []
        for game, result in self.games.items():
            if result == "-:-" and game[0] in teams or game[1] in teams:
                self.remaining.append(game)

        return self.remaining

    def get_table(self):
        self.read_results()
        results = [[0 for i in range(8)] for i in range(4)]
        for game, result in self.games.items():
            if result != "-:-":
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

    def enter_results(self):
        for game in self.remaining_games():
            result = input(f"Result for {game[0]} vs {game[1]}:")
            self.games[game] = result

    def read_results(self, inp="results.txt"):
        with open(inp, "r") as results:
            results = results.read().replace("vs ", "").split("\n")
            results = [result.split(":") for result in results]
            results = {(result[0].split()[0], result[0].split()[1]): f"{result[1]}:{result[2]}" for result in results}

            self.games = {game: result if game not in results.keys() else results[game] for game, result in self.games.items()}

    def sort_table(self):
        self.get_table()
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
                except KeyError:
                    team1, team2 = teams[same[1]], teams[same[0]]
                res = self.games[(team1, team2)]
                if res != "-:-":
                    g1 = int(list(res)[0])
                    g2 = int(list(res)[2])
                    td = g1 - g2

                    if td > 0:  # Teams A wins
                        pass

                    elif td == 0:  # Draw
                        print("direct comparison is a draw!")
                        self.check_goal_difference(same[0], same[1])

                    elif td < 0:  # Teams B wins
                        self.swap_rows(same[0])

                else:
                    print("Havent played each other yet!")
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
            print("same goal difference")
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


groups = [Group("Turkey", "Italy", "Wales", "Switzerland"),
          Group("Denmark", "Finland", "Belgium", "Russia"),
          Group("Netherlands", "Ukraine", "Austria", "North-Macedonia"),
          Group("England", "Croatia", "Scotland", "Czech-Republic"),
          Group("Spain", "Sweden", "Poland", "Slovakia"),
          Group("Hungary", "Portugal", "France", "Germany")]

for group in groups:
    group.get_table()
    group.sort_table()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, "expand_frame_repr", False):
        print(group.table)

for group in groups[1:]:
    groups[0].table = groups[0].table.append(group.table)

groups[0].table.to_excel("output.xlsx")