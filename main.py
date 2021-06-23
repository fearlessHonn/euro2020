import pandas as pd
import itertools

parameters = ["Games", "Wins", "Draws", "Losses", "Goals", "Conceded goals", "Goal difference", "Points", "Team"]
games = dict()
groups = []


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

        if inp is None:
            self.table = [[0 for i in range(9)] for i in range(4)]
            for i, team in enumerate(teams):
                self.table[i][8] = team
        else:
            self.table = inp

    def get_table(self):
        global games
        for game, result in games.items():
            if result != "-:-" and (game[0] in self.teams or game[1] in self.teams):
                g1 = int(list(result)[0])
                g2 = int(list(result)[2])
                td = g1 - g2

                team_index1 = self.teams.index(game[0])
                team_index2 = self.teams.index(game[1])

                self.table[team_index1][0] += 1  # Updating Games
                self.table[team_index2][0] += 1

                self.table[team_index1][6] += td  # Updating goal difference
                self.table[team_index2][6] -= td

                self.table[team_index1][4] += g1  # Updating goals
                self.table[team_index2][4] += g2

                self.table[team_index1][5] += g2  # Updating conceded goals
                self.table[team_index2][5] += g1

                if td > 0:  # Teams A wins
                    self.table[team_index1][1] += 1
                    self.table[team_index2][3] += 1

                    self.table[team_index1][7] += 3

                if td == 0:
                    self.table[team_index1][2] += 1
                    self.table[team_index2][2] += 1

                    self.table[team_index1][7] += 1
                    self.table[team_index2][7] += 1

                if td < 0:  # Teams A wins
                    self.table[team_index1][1] += 1
                    self.table[team_index1][3] += 1

                    self.table[team_index2][7] += 3

        return self.table

    def sort_table(self):
        global games
        self.table = sorted(self.table, key=lambda x: x[-2], reverse=True)
        self.teams = [i[8] for i in self.table]
        points = [i[7] for i in self.table]
        sames = []
        for i, val in enumerate(points):
            if points.count(val) > 1:
                sames.append([i for i, a in enumerate(points) if a == val])

        if sames:
            sames = [s for i, s in enumerate(sames) if s not in sames[i + 1:]]
            teams = self.teams
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
        rows = self.table
        self.table = rows[:index] + [rows[index + 1]] + [rows[index]] + rows[index + 2:]

        teams = self.teams
        self.teams = teams[:index] + [teams[index + 1]] + [teams[index]] + teams[index + 2:]

    def check_goal_difference(self, team_index_1, team_index_2):
        goal_differences = [i[6] for i in self.table]
        goal_difference_team1 = goal_differences[team_index_1]
        goal_difference_team2 = goal_differences[team_index_2]
        if goal_difference_team1 > goal_difference_team2:
            pass

        elif goal_difference_team1 == goal_difference_team2:
            self.check_total_goals(team_index_1, team_index_2)

        elif goal_difference_team1 < goal_difference_team2:
            self.swap_rows(team_index_1)

    def check_total_goals(self, team_index_1, team_index_2):
        goals = [i[4] for i in self.table]
        goals_team1 = goals[team_index_1]
        goals_team2 = goals[team_index_2]
        if goals_team1 > goals_team2:
            pass

        elif goals_team1 == goals_team2:
            print(NotImplementedError("Can't decide which team is better"))

        elif goals_team1 < goals_team2:
            self.swap_rows(team_index_1)

    def placements(self):
        i = self.teams = [i[8] for i in self.table]
        self.first, self.second, self.third, self.fourth = i[0], i[1], i[2], i[3]
        self.third_params = self.table[2]


def init_groups():
    global groups
    groups = [Group(teams=["Turkey", "Italy", "Wales", "Switzerland"]),
              Group(teams=["Denmark", "Finland", "Belgium", "Russia"]),
              Group(teams=["Netherlands", "Ukraine", "Austria", "North-Macedonia"]),
              Group(teams=["England", "Croatia", "Scotland", "Czech-Republic"]),
              Group(teams=["Spain", "Sweden", "Poland", "Slovakia"]),
              Group(teams=["Hungary", "Portugal", "France", "Germany"])]


def calculate_groups():
    global games
    init_groups()
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

    input = thirds_params
    group_of_thirds = Group(teams=thirds, inp=input)
    group_of_thirds.sort_table()

    group_of_thirds.placements()
    best_thirds = [group_of_thirds.first, group_of_thirds.second, group_of_thirds.third, group_of_thirds.fourth]

    return direct_qualification + best_thirds


def generate_possible_results(r=6):
    possible_results = [f"{a}:{b}" for a in range(r) for b in range(r)]
    return possible_results


def is_qualification_possible(country, depth):
    global games
    remaining_games = [game for game, result in games.items() if result == "-:-"]
    possible_qualifications = []
    combinations = list(itertools.product(generate_possible_results(depth), repeat=len(remaining_games)))
    for c, combination in enumerate(combinations):
        print(f"Combination {c + 1} of {len(combinations)}: {combination}")
        for i, game in enumerate(remaining_games):
            games[game] = combination[i]
        if country in calculate_groups():
            possible_qualifications.append(combination)

    if possible_qualifications:
        print(possible_qualifications)
        print(
            f"Qualification for {country} is possible.")
    else:
        print(f"Qualification for {country} isn't possible")


if __name__ == "__main__":
    init_groups()
    read_results()
    calculate_groups()
    print("\n".join([f'{pd.DataFrame(g.table, index=g.teams, columns=parameters)}, {g.first}, {g.second}, {g.third}, {g.fourth}' for g in groups]))

    generate_possible_results()
    country = "Hungary"
    possible_qualifications = is_qualification_possible(country, 4)

