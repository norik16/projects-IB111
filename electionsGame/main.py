import math
import matplotlib.pyplot as plt
import random
import copy

random.seed()

change = 1 / 2


class Party:
    """Generic political party class"""

    def __init__(self, name: str, color: str, selfesteem: int, plunder: float,
                 money: int = 0, promises: int = 100, karma: int = 75,
                 start: int = 0):
        self.name = name
        self.color = color
        self.selfesteam = selfesteem
        self.plunder = plunder
        self.promises = promises
        self.karma = karma
        self.start = start
        self.money = money

        self.done_promises = promises - selfesteem
        self.rounds = 0
        self.last_parliament = 1  # last percentage in parliament
        self.rounds_nip = 0  # how many rounds not in parliament
        self.t_rounds_ip = 1  # total num. of rounds in parliament

    def rule(self, parliament):
        """Evaluate ruling of the party based on promises a plundering"""

        print(self.name, " : Rulez!")
        self.rounds_nip = 0
        self.t_rounds_ip += 1

        # After getting into the parliament everything promised by selfesteam
        # becomes real promise
        self.promises = self.selfesteam

        if self.rounds >= self.start:
            self.money += self.plunder * parliament * 2
            self.done_promises = (1 - self.plunder) * parliament * 2
            self.karma += \
                (math.sqrt(
                    max(self.done_promises *
                        (100 + self.done_promises - self.promises), 0)
                    / 2) - 60) / 10

            # Enclose karma between 0 and 100
            if self.karma <= 0:
                self.karma = 0
            elif self.karma > 100:
                self.karma = 100

            self.last_parliament = parliament

            return self.done_promises

        return 0

    def get_votes(self):
        """
            Get votes based on karma and selfesteem
            (etc. promises for the future)
        """

        self.rounds += 1

        if self.rounds >= self.start:
            print(self.get_name(), " >> karma", self.karma,
                  " >> done_promises", self.done_promises, "  >> plunder ",
                  self.plunder)

            # Another method:
            # return (self.done_promises + self.selfesteam) * self.karma * math.exp(
            #     -(self.last_parliament / 60) ** 3)
            return self.selfesteam * self.karma \
                   * math.exp(- (self.last_parliament / 60) ** 3)
            # / (1 + self._last_parliament/2)

        return 0

    def not_in_parliament(self):
        """
            What should the party do while not being in parliament
        """

        print(self.name + " : Not in parliament")
        if self.rounds < self.start:
            return
        self.karma += 1  # Slowly regain karma
        self.done_promises = 0
        self.last_parliament = 0
        self.rounds_nip += 1
        return

    def get_money(self):
        return self.money

    def get_name(self):
        return self.name

    def get_color(self):
        return self.color


class Smart(Party):
    """
        Steadily increases plundering if being parliament,
        decreases otherwise
    """

    def rule(self, parliament):
        super().rule(parliament)

        self.plunder += 0.1

    def not_in_parliament(self):
        super().not_in_parliament()

        self.plunder -= 0.1
        if self.plunder < 0:
            self.plunder = 0
        # if self.rounds_nip > random.randint(3, 5):
        #     self.karma = 1


class SmarterBinary(Party):
    """
        This party has a goal (percentage of parliament)
        and starts plundering only while above it
    """

    def __init__(self, name: str, color: str, selfesteem: int, plunder: float,
                 money: int = 0, promises: int = 100, karma: int = 75,
                 start: int = 0, goal: int = 50):

        super().__init__(name, color, selfesteem, plunder, money, promises,
                         karma, start)

        self.state = 0  # 0 = growing, 1 = eating
        self.goal = goal

    def rule(self, parliament):
        if parliament < self.goal:
            self.state = 0
        else:
            self.state = 1

        if self.state == 0:
            self.plunder = 0
        else:
            self.plunder += 0.1 * change
            if self.plunder > 1:
                self.plunder = 1

        super().rule(parliament)


class SmarterLinear(Party):
    """
        This party has a goal (percentage of parliament)
        and is plundering in proportion to % needed to achieving it
    """

    def __init__(self, name: str, color: str, selfesteem: int, plunder: float,
                 money: int = 0, promises: int = 100, karma: int = 75,
                 start: int = 0, goal: int = 50):

        super().__init__(name, color, selfesteem, plunder, money, promises,
                         karma, start)

        self.state = 0  # 0 = growing, 1 = eating
        self.goal = goal

    def rule(self, parliament):
        self.plunder = (parliament - self.goal) / 25 * change
        if self.plunder > 1:
            self.plunder = 1
        if self.plunder < 0:
            self.plunder = 0

        super().rule(parliament)


def run_the_state(parties, number_of_elections, results):
    votes = {}

    # create dictionary of all parties
    for party in parties:
        votes[party.get_name()] = 0

    for it in range(number_of_elections):
        print("Iteration " + str(it))
        print("------------------------")
        preTotalVotes = 0
        totalVotes = 0

        # Get votes for each party
        for party in parties:
            votes[party.get_name()] = party.get_votes()
            # print(party.get_name() + " got " + str(votes[party.get_name()]) + " out of " + str(totalVotes))

        # Count total number of votes
        for party in parties:
            preTotalVotes += votes[party.get_name()]

        # Check if at least some voters came to the election
        if preTotalVotes <= 0:
            for party in parties:
                # results[party.get_name()].append(0)
                party.not_in_parliament()
            continue

        # Decide if party should be in parliament
        for party in parties:
            print(party.get_name()
                  + ": " + str(votes[party.get_name()] / preTotalVotes * 100)
                  + "   |   " + str(votes[party.get_name()]))

            if votes[party.get_name()] / preTotalVotes * 100 <= 5:
                votes[party.get_name()] = 0
                party.not_in_parliament()
            else:
                totalVotes += votes[party.get_name()]

        # Check if at least one party got to parliament, so the code handles
        # even swarms of parties
        if totalVotes <= 0:
            for party in parties:
                # results[party.get_name()].append(0)
                party.not_in_parliament()
                party.not_in_parliament()
            continue

        # Let each party in parliament rule with their seats
        for party in parties:
            vote = votes[party.get_name()]
            # results[party.get_name()].append(vote / totalVotes * 100)
            if votes[party.get_name()] != 0:
                party.rule(vote / totalVotes * 100)

    # Get avg money earned per election
    for party in parties:
        results[party.get_name()].append(party.get_money()/number_of_elections)

    return results


def output(number_of_elections, parties):
    """
        Money per election for different time periods

        number_of_elections : int
        parties : {name: money}
    """

    p = {}
    results = {}

    lengths = [x for x in range(2, 100)]  # timeperiods to test
    # lengths = [2, 4]  # timeperiods to test


    for party in parties:
        results[party.get_name()] = []

    for length in lengths:
        c_parties = copy.deepcopy(parties)
        results = run_the_state(c_parties, length, results)

        # for party in parties:
        #     print()
        #     print()
        #     print("Money:")
        #     print("------------------------")
        #     for party in parties:
        #         print(party.get_name() + ": " + str(
        #             party.get_money()) + ' MKč while being ' + str(
        #             party.t_rounds_ip) +
        #               ' times elected -> efficiency  ' + str(
        #             party.get_money() / party.t_rounds_ip))

    for party in parties:  # y = money per year, x = number of years
        plt.plot([i for i in lengths],
                 results[party.get_name()], party.get_color())

    plt.axis([0, max(lengths), 0, 100])
    plt.show()


# TODO: put into fcions


# name, color, selfesteem, plunder, money, promises, karma, start

# big fight, cycling after hudereds
parties1 = [
    Smart("ODS", 'b', 5, 0.2, 0, 60, 50),
    Smart("ČSSD", 'r', 42, 0.3854, 0, 60, 40),
    Smart("KDU-ČSL", 'y', 5, 0.2, 0, 50, 20),
    Smart("ANO", 'black', 30, 0.50, 0, 100, 70, 60),
    Smart("Ja", 'grey', 50, 0, 0, 10, 50, 80),
    SmarterBinary("Nein", 'pink', 50, 0.5, 0, 10, 50, 90), ]

# two blocked smarter strategies
parties2 = [
    Smart("ODS", 'b', 5, 0.2, 0, 60, 50),
    SmarterBinary("ČSSD", 'r', 5, 0.2, 0, 60, 50, 0, 75),
    SmarterLinear("KDU-ČSL", 'y', 5, 0.2, 0, 60, 50, 0, 75), ]

# two smarter strategies outsmarting the smart one
parties3 = [
    Smart("ODS", 'b', 5, 0.2, 0, 60, 50),
    SmarterBinary("ČSSD", 'r', 5, 0.2, 0, 60, 50, 0, 30),
    SmarterLinear("KDU-ČSL", 'y', 5, 0.2, 0, 60, 50, 0, 30), ]

p = []

for i in range(1, 100):
    parties = []
    parties.append(Smart("ODS", 'b', 5, i / 100, 0, 60, 50))
    parties.append(SmarterBinary("ČSSD", 'r', 5, 0.5, 0, 60, 50, 0, i))
    parties.append(SmarterLinear("KDU-ČSL", 'y', 5, 0.5, 0, 60, 50, 0, i))

#     p.append(parties)
#
# for parties in p:
#     for party in parties:
#         if party.goal:
#             party.name += ' ' + party.goal
#         else:
#             party.name += ' ' + party.plunder
#
# for parties in p:
#     mn = []
#     for i in range(5, 200):
#         mn.append(i, run_the_state(parties, i))

# Party("ANO", 'black', 30, 0.50, 0, 100, 100, 60),
# Party("Ja", 'grey', 2, 0.50, 0, 100, 100, 60),

number_of_years = 200

output(100, parties1)


# runTheState(parties1, number_of_years)
