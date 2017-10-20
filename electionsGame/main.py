import math
import matplotlib.pyplot as plt
import random

random.seed()

class Party:
    """Generic political party class"""

    def __init__(self, name: str, color: str, selfesteem: int, plunder: float,
                 money: int = 0, promises: int = 100, karma: int = 75, start: int = 0):
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
        self.last_parliament = 1
        self.rounds_nip = 0
        self.t_rounds_ip = 1

    def rule(self, parliament):
        print(self.name, " : Rulez!")
        self.rounds_nip = 0
        self.t_rounds_ip += 1

        if self.rounds >= self.start:
            self.money += self.plunder*parliament*2
            self.done_promises = (1-self.plunder) * parliament*2
            self.karma += (math.sqrt(max(self.done_promises*(100 + self.done_promises - self.promises), 0) / 2) - 60) /10
            if self.karma <= 0:
                self.karma = 0
            elif self.karma > 100:
                self.karma = 100
            self.last_parliament = parliament
            return self.done_promises

        return 0

    def get_votes(self):
        self.rounds += 1

        if self.rounds >= self.start:
            print(self.get_name(), " >> karma", self.karma, " >> done_promises", self.done_promises, "  >> plunder ", self.plunder)
            return (self.done_promises + self.selfesteam) * self.karma * math.exp(-((self.last_parliament)/(60))**(3))
            # / (1 + self._last_parliament/2)

        return 0

    def not_in_parliament(self):
        print(self.name + " : Not in parliament")
        if self.rounds < self.start:
            return
        self.done_promises = 0
        self.last_parliament = 0
        return

    def get_money(self):
        return self.money

    def get_name(self):
        return self.name

    def get_color(self):
        return self.color


class Smart(Party):
    def rule(self, parliament):
        super().rule(parliament)

        self.plunder += 0.1

    def not_in_parliament(self):
        super().not_in_parliament()

        self.rounds_nip += 1
        self.plunder -= 0.1
        if self.plunder < 0:
            self.plunder = 0
        if self.rounds_nip > random.randint(3, 5):
            self.karma = 1

class Smarter(Party):
    def __init__(self, name: str, color: str, selfesteem: int, plunder: float,
                 money: int = 0, promises: int = 100, karma: int = 75, start: int = 0):

        super().__init__(name, color, selfesteem, plunder, money, promises, karma, start)

        self.state = 0 #0 = growing, 1 = eating

    def rule(self, parliament):
        if parliament < 50:
            self.state = 0
        else:
            self.state = 1

        if self.state == 0:
            self.plunder = 0
        else:
            self.plunder += 0.1

        super().rule(parliament)

    pass


# name, color, selfesteem, plunder, money, promises, karma, start
parties = [
    Smart("ODS", 'b', 5, 0.2, 0, 60, 50),
    Smart("ČSSD", 'r', 42, 0.3854, 0, 60, 40),
    Smart("KDU-ČSL", 'y', 5, 0.2, 0, 50, 20),
    Smart("ANO", 'black', 30, 0.50, 0, 100, 70, 60),
    Smart("Ja", 'grey', 50, 0, 0, 10, 50, 80),
    Smarter("Nein", 'pink', 50, 0.5, 0, 10, 50, 90), ]

#Party("ANO", 'black', 30, 0.50, 0, 100, 100, 60),
#Party("Ja", 'grey', 2, 0.50, 0, 100, 100, 60),

results = {}
votes = {}

# create dictionary of all parties
for party in parties:
    results[party.get_name()] = []
    votes[party.get_name()] = 0

number_of_years = 140

for it in range(number_of_years):
    print("Iteration " + str(it))
    print("------------------------")
    preTotalVotes = 0
    totalVotes = 0

    for party in parties:
        votes[party.get_name()] = party.get_votes()
        #print(party.get_name() + " got " + str(votes[party.get_name()]) + " out of " + str(totalVotes))

    for party in parties:
        preTotalVotes += votes[party.get_name()]

    if preTotalVotes <= 0:
        for party in parties:
            results[party.get_name()].append(0)
            party.not_in_parliament()
        continue

    for party in parties:
        print(party.get_name() + ": " + str(votes[party.get_name()]/preTotalVotes * 100) + "   |   " + str(votes[party.get_name()]))
        if votes[party.get_name()]/preTotalVotes * 100 <= 5:
            votes[party.get_name()] = 0
            party.not_in_parliament()
        else:
            totalVotes += votes[party.get_name()]

    if totalVotes <= 0:
        for party in parties:
            results[party.get_name()].append(0)
            party.not_in_parliament()
        continue

    for party in parties:
        vote = votes[party.get_name()]
        results[party.get_name()].append(vote/totalVotes * 100)
        #print(party.get_name() + ": " + str(vote/totalVotes * 100))
        if votes[party.get_name()] != 0:
            party.rule(vote/totalVotes * 100)

    print()
    print()

print("Money:")
print("------------------------")
for party in parties:
    print(party.get_name() + ": " + str(party.get_money()) + ' MKč while being ' + str(party.t_rounds_ip) +
          ' times elected -> efficiency  ' + str(party.get_money()/party.t_rounds_ip))


for party in parties:
    plt.plot([i for i in range(number_of_years)], results[party.get_name()], party.get_color())

plt.axis([0, number_of_years, 0, 100])
plt.show()
