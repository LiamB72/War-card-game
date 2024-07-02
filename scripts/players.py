from random import shuffle
import socket
import threading
import sys
from time import sleep
import json
from random import randint


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


class Client:

    def __init__(self, serverAdd: str):
        self.roundWinner = None
        self.receive_thread = None
        self.player = None
        self.data = None
        self.resultReceived = False
        self.FORMAT = "utf-8"
        self.host, self.port = serverAdd, 5000
        endpoint = (self.host, self.port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(endpoint)

        self.gamemode = None
        self.debugMode = False

        self.P1 = Player(1)
        self.P2 = Player(2)

    def send(self, message_input):
        msg = f"data{message_input}".encode(self.FORMAT)
        self.sock.send(msg)

    def receive(self):
        while True:
            rawData = self.sock.recv(1024).decode(self.FORMAT)
            if rawData == "quit":
                break

            self.parseData(rawData)

    def parseData(self, rawData):
        if rawData[:4] in ["auth", "data", "resu"]:
            self.data = json.loads(rawData[4:])
            print(self.data)

            if rawData[:4] == "auth":

                if self.data['debugMode']:
                    self.debugMode = True

                if self.data['playerID'] == 1:
                    self.player = 1
                    self.P1.deck = self.data['playerDeck']
                    self.P1.r = self.data['playerReady']
                    self.P1.currentCard = tuple(self.data['playerCurrentCard'])
                    self.P1.victoryCount = self.data['playerVictoryCount']
                    self.P1.battleDeck = self.data['playerBattleDeck']
                    self.P1.waitingDeck = self.data['playerWaitingDeck']
                    self.P2.r = self.data['player2Ready']
                    self.P2.victoryCount = self.data['player2VictoryCount']

                    if self.debugMode:
                        self.P2.deck = self.data['player2Deck']

                        for i in range(len(self.P2.deck)):
                            self.P2.deck[i] = tuple(self.P2.deck[i])

                elif self.data['playerID'] == 2:
                    self.player = 2
                    self.P2.deck = self.data['playerDeck']
                    self.P2.r = self.data['playerReady']
                    self.P2.currentCard = tuple(self.data['playerCurrentCard'])
                    self.P2.victoryCount = self.data['playerVictoryCount']
                    self.P2.battleDeck = self.data['playerBattleDeck']
                    self.P2.waitingDeck = self.data['playerWaitingDeck']
                    self.P1.r = self.data['player2Ready']
                    self.P1.victoryCount = self.data['player2VictoryCount']


                self.gamemode = self.data['gameMode']
                self.tupleCards()
                if self.debugMode:
                    print("Data Parsed.")

            elif rawData[:4] == "data":
                if self.player == 2:
                    self.P1.r = self.data['P1'][0]
                    self.P1.currentCard = tuple(self.data['P1'][1])
                else:
                    self.P2.r = self.data['P2'][0]
                    self.P2.currentCard = tuple(self.data['P2'][1])
                print("Data Received.")

            elif rawData[:4] == "resu":

                if self.player == 1:
                    self.P1.deck = self.data['player1Deck']
                    print(f"Player1 : {self.P1.deck}\ndataP1:{self.data['player1Deck']}\n")

                elif self.player == 2:
                    self.P2.deck = self.data['player2Deck']
                    print(f"Player2 : {self.P2.deck}\ndataP2:{self.data['player2Deck']}\n")

                self.P1.currentCard = tuple(self.data['player1CurrentCard'])
                self.P2.currentCard = tuple(self.data['player2CurrentCard'])
                print(self.P1.currentCard, self.P2.currentCard)
                self.roundWinner = self.data['roundWinner']
                print(f"Round Winner : {self.roundWinner}\n")
                self.P1.victoryCount = self.data['player1Victory']
                self.P2.victoryCount = self.data['player2Victory']
                print(self.P1.victoryCount, self.P2.victoryCount)
                self.resultReceived = True
                self.tupleCards()
                print("Results Received.")
        else:
            print(rawData)

    def tupleCards(self):
        if self.player == 1:
            for i in range(len(self.P1.deck)):
                self.P1.deck[i] = tuple(self.P1.deck[i])
            for i in range(len(self.P1.battleDeck)):
                if len(self.P1.battleDeck) != 0:
                    self.P1.battleDeck[i] = tuple(self.P1.battleDeck[i])
            for i in range(len(self.P1.waitingDeck)):
                if len(self.P1.waitingDeck) != 0:
                    self.P1.waitingDeck[i] = tuple(self.P1.waitingDeck[i])

        elif self.player == 2:
            for i in range(len(self.P2.deck)):
                self.P2.deck[i] = tuple(self.P2.deck[i])
            for i in range(len(self.P2.battleDeck)):
                if len(self.P2.battleDeck) != 0:
                    self.P2.battleDeck[i] = tuple(self.P2.battleDeck[i])
            for i in range(len(self.P2.waitingDeck)):
                if len(self.P2.waitingDeck) != 0:
                    self.P2.waitingDeck[i] = tuple(self.P2.waitingDeck[i])

    def start(self):
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def stop(self):
        self.receive_thread.join()
        print(f"[CLIENT] Disconnected from {self.host}:{self.port}.")
        self.sock.close()
        print(f"[CLIENT] Closed Connection. Initializing Exit...")
        sys.exit()
