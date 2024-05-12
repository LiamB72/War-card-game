from random import shuffle


class Deck(object):

    def __init__(self):
        self.deck = []
        self.cardValue = [2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King", "Ace"]
        self.cardColour = ["Clubs", "Diamonds", "Heart", "Spade"]
        for iColor in range(len(self.cardColour)):
            for iValue in range(len(self.cardValue)):
                self.deck.append((iValue, iColor))

        self.images = {(0, 0): "01", (1, 0): "02", (2, 0): "03", (3, 0): "04", (4, 0): "05", (5, 0): "06", (6, 0): "07",
                       (7, 0): "08", (8, 0): "09", (9, 0): "10", (10, 0): "11", (11, 0): "12", (12, 0): "00",
                       (0, 1): "14", (1, 1): "15", (2, 1): "16", (3, 1): "17", (4, 1): "18", (5, 1): "19", (6, 1): "20",
                       (7, 1): "21", (8, 1): "22", (9, 1): "23", (10, 1): "24", (11, 1): "25", (12, 1): "13",
                       (0, 2): "27", (1, 2): "28", (2, 2): "29", (3, 2): "30", (4, 2): "31", (5, 2): "32", (6, 2): "33",
                       (7, 2): "34", (8, 2): "35", (9, 2): "36", (10, 2): "37", (11, 2): "38", (12, 2): "26",
                       (0, 3): "40", (1, 3): "41", (2, 3): "42", (3, 3): "43", (4, 3): "44", (5, 3): "45", (6, 3): "46",
                       (7, 3): "47", (8, 3): "48", (9, 3): "49", (10, 3): "50", (11, 3): "51", (12, 3): "39"}

        self.defaultCard = "54"

    def cardName(self, a0):
        return f"{self.cardValue[a0[0]]} of {self.cardColour[a0[1]]}"

    def shuffleCards(self):
        shuffle(self.deck)

    def takeCard(self):
        cardTaken = None
        if self.deck:
            cardTaken = self.deck[0]
            del (self.deck[0])
        else:
            print("No more card left in the deck!")

        return cardTaken


class Player:

    def __init__(self, playerNumber: int):
        self.deck = []
        self.waitingDeck = []
        self.battleDeck = []
        self.currentCard = (-1, -1)
        self.victoryCount = 0
        self.playerNumber = playerNumber
        self.r = False