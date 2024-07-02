import socket
import threading
import json

from scripts.players import Player, Deck
from random import randint


class Server:

    def __init__(self, ip):
        self.FORMAT = "utf-8"
        self.host, self.port = socket.gethostbyname(socket.gethostname()), 5000
        self.host, self.port = ip, 5000
        endpoint = (self.host, self.port)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(endpoint)
        self.connections = {}

        self.P1 = Player(1)
        self.P2 = Player(2)
        self.battle = 0

        self.debugMode = True

        self.gameDeck = Deck()
        for i in range(randint(2, 10)):
            self.gameDeck.shuffleCards()

        for i in range(len(self.gameDeck.deck) // 2):
            if i % 2 == 0:
                self.P1.deck.append(self.gameDeck.deck[i])
            else:
                self.P2.deck.append(self.gameDeck.deck[i])

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")

        if self.connections == {} or (conn in self.connections.values() and self.connections["P2"] is not None):
            self.connections["P1"] = conn
            if not self.debugMode:
                tempDictionary = json.dumps({"playerID": 1,
                                             "playerDeck": self.P1.deck,
                                             "playerCurrentCard": self.P1.currentCard,
                                             "playerReady": self.P1.r,
                                             "playerVictoryCount": self.P1.victoryCount,
                                             "playerBattleDeck": self.P1.battleDeck,
                                             "playerWaitingDeck": self.P1.waitingDeck,
                                             "player2Ready": self.P2.r,
                                             "player2VictoryCount": self.P2.victoryCount,
                                             "gameMode": 15,
                                             "debugMode": self.debugMode})
            else:
                tempDictionary = json.dumps({"playerID": 1,
                                             "playerDeck": self.P1.deck,
                                             "playerCurrentCard": self.P1.currentCard,
                                             "playerReady": self.P1.r,
                                             "playerVictoryCount": self.P1.victoryCount,
                                             "playerBattleDeck": self.P1.battleDeck,
                                             "playerWaitingDeck": self.P1.waitingDeck,
                                             "player2Deck": self.P2.deck,
                                             "player2CurrentCard": self.P2.currentCard,
                                             "player2Ready": self.P2.r,
                                             "player2VictoryCount": self.P2.victoryCount,
                                             "player2BattleDeck": self.P2.battleDeck,
                                             "player2WaitingDeck": self.P2.waitingDeck,
                                             "gameMode": 15,
                                             "debugMode": self.debugMode})
            self.connections["P1"].send(f"auth{tempDictionary}".encode(self.FORMAT))
            print("Player 1 is connected")

        elif not (conn in self.connections.values()) and self.connections != {}:
            self.connections["P2"] = conn
            tempDictionary = json.dumps({"playerID": 2,
                                         "playerDeck": self.P2.deck,
                                         "playerCurrentCard": self.P2.currentCard,
                                         "playerReady": self.P2.r,
                                         "playerVictoryCount": self.P2.victoryCount,
                                         "playerBattleDeck": self.P2.battleDeck,
                                         "playerWaitingDeck": self.P2.waitingDeck,
                                         "player2Ready": self.P1.r,
                                         "player2VictoryCount": self.P1.victoryCount,
                                         "gameMode": 15,
                                         "debugMode": self.debugMode})
            self.connections["P2"].send(f"auth{tempDictionary}".encode(self.FORMAT))
            print("Player 2 is connected")

        connected = True
        while connected:
            try:
                # Get the message
                msg = conn.recv(1024).decode(self.FORMAT)
                print(f"[{addr}] {msg}")

                if msg == "quit":
                    conn.send("quit".encode(self.FORMAT))
                    connected = False

                if msg[:4] == "data":
                    data = json.loads(msg[4:])
                    for i, v in self.connections.items():
                        if v == conn:
                            if i == "P1":
                                self.P1.r = data["P1"][0]
                                self.P1.currentCard = tuple(data["P1"][1])
                                print(self.P1.currentCard)
                            elif i == "P2":
                                self.P2.r = data["P2"][0]
                                self.P2.currentCard = tuple(data["P2"][1])
                                print(self.P2.currentCard)

                        v.send(msg.encode(self.FORMAT))  # Send the message

                    self.checkDecks()
                    if self.P1.r and self.P2.r:
                        roundWinner = self.gameLogic()
                        print(roundWinner)
                        if roundWinner != "":
                            results = {}
                            for v in self.connections.values():
                                results = json.dumps({"roundWinner": roundWinner,
                                                      "player1Deck": self.P1.deck,
                                                      "player1Victory": self.P1.victoryCount,
                                                      "player1CurrentCard": self.P1.currentCard,
                                                      "player2Deck": self.P2.deck,
                                                      "player2Victory": self.P2.victoryCount,
                                                      "player2CurrentCard": self.P2.currentCard})
                                print(results)
                                v.send(f"resu{results}".encode(self.FORMAT))
                                print("results sent")
                            self.P1.currentCard = (-1, -1)
                            self.P1.r = False
                            self.P2.currentCard = (-1, -1)
                            self.P2.r = False
                            print("cards reset")


            except socket.error as err:
                print(f"[ERROR] {err}")
                connected = False

        if self.connections != {}:
            for i, v in self.connections.items():
                if v == conn:
                    del self.connections[i]

                    if i == "P1":
                        self.P1.IP = None
                    elif i == "P2":
                        self.P2.IP = None
                    break

        conn.close()
        print(f"[CONNECTION CLOSED] {addr} disconnected.")
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

    def checkDecks(self):
        """
        Checks if the deck is less than five cards to put the won cards back into the playable deck.
        """
        if len(self.P1.deck) < 5:
            self.P1.deck.extend(self.P1.waitingDeck)
            self.P1.waitingDeck.clear()

        if len(self.P2.deck) < 5:
            self.P2.deck.extend(self.P2.waitingDeck)
            self.P2.waitingDeck.clear()

    def gameLogic(self):
        roundWinner = ""
        if self.P1.currentCard[0] == self.P2.currentCard[0]:
            self.battle += 2
            roundWinner = "No-one"

        if self.battle != 0:
            self.P1.battleDeck.append(self.P1.currentCard)
            self.P1.battleDeck.append(self.P2.currentCard)
            self.P1.deck.remove(self.P1.currentCard)
            self.P1.currentCard = ()

            self.P2.battleDeck.append(self.P1.currentCard)
            self.P2.battleDeck.append(self.P2.currentCard)
            self.P2.deck.remove(self.P2.currentCard)
            self.P2.currentCard = ()
            self.battle -= 1

        elif self.battle == 0:
            if self.P1.currentCard[0] > self.P2.currentCard[0]:
                roundWinner = "Player 1"
                changeDecks(self.P1, self.P2)

            elif self.P1.currentCard[0] < self.P2.currentCard[0]:
                roundWinner = "Player 2"
                changeDecks(self.P2, self.P1)

        return roundWinner

    def start(self):
        print("[STARTING] server is starting...")
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.host}:{self.port}")
        while True:
            conn, addr = self.server.accept()
            threadClient = threading.Thread(target=self.handle_client, args=(conn, addr))
            threadClient.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def changeDecks(winner, loser):
    """
    Logic of the game loop.
    """
    print(winner.playerNumber, loser.playerNumber)
    winner.victoryCount += 1

    winner.waitingDeck.append(winner.currentCard)
    winner.waitingDeck.append(loser.currentCard)
    winner.deck.remove(winner.currentCard)

    if len(winner.battleDeck) != 0:
        winner.waitingDeck.extend(winner.battleDeck)
        winner.battleDeck.clear()

    loser.deck.remove(loser.currentCard)

    if len(loser.battleDeck) != 0:
        loser.battleDeck.clear()


ipAsk = input("Enter IP: ")
server = Server(ipAsk)
server.start()
