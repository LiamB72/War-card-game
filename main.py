"""
Simulateur de jeu de 52 cartes
Liam BERGE TG1 | Started On: 21/10/2023 | Last Edit: 22/01/2024
Code Reworked on the 11/04/2024 | Last Edit: 11/05/2024
"""

import pickle
import socket
import sys
from functools import partial
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from PyQt6 import uic, QtGui
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

from scripts.menus import debugMenu, cardMenu
from scripts.players import Deck, Player
from scripts.utils import warningBox

class startMenu(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("data/UIs/startMenu.ui", self)
        self.setWindowIcon(QIcon("data/images/QTImages/startmenu.png"))
        self.setWindowTitle("War Card Game - Main Menu")
        self.setFixedSize(self.size())

        SENDER_NAME = socket.gethostname()
        self.SENDER_IP = socket.gethostbyname(SENDER_NAME)
        self.SENDER_PORT = 5000
        self.RECEIVER_IP = ""
        self.RECEIVER_PORT = 5000

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(0)
        self.sock.bind((self.SENDER_IP, self.SENDER_PORT))

        # self.debugMode_QCheck.hide()
        self.game_window = None
        self.gmChosen = "Target Score"
        self.targetScore = self.value_QSpin.value()

        self.start_QButton.clicked.connect(self.startGame)
        self.help_QButton.clicked.connect(self.helpWindow)
        self.scoreGM_QRatio.toggled.connect(self.TargetScoreSwitch)
        self.value_QSpin.valueChanged.connect(self.setValue)

    def setValue(self):
        self.targetScore = self.value_QSpin.value()

    def TargetScoreSwitch(self):
        self.value_QSpin.setEnabled(not self.value_QSpin.isEnabled())
        if not self.value_QSpin.isEnabled():
            self.targetScore = 103

    @staticmethod
    def helpWindow():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowIcon(QIcon("data/images/QTImages/information.png"))
        msg.setText(
            "Press \"Win\", then write : \"cmd\" finally to press the enter key. Once the command prompt window opened, write : "
            "\"ipconfig\", then press enter again. After searching for the IPv4 address, take note and give it to the other player."
            "\n(This IP should look like: 192.168.xxx.xxx . e.g 192.168.1.2)")
        msg.setWindowTitle("Help")
        msg.exec()

    def playerIP_empty(self):
        if self.ipPlayer_QLineEdit.text().strip() == "" or self.ipPlayer_QLineEdit.text().strip() == self.SENDER_IP:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowIcon(QIcon("data/images/QTImages/warning.png"))
            msg.setText("Please enter the IP address of the other player.")
            msg.setWindowTitle("Careful there!")
            msg.exec()
            return True
        return False

    # When pressing the start button!
    def startGame(self):
        self.RECEIVER_IP = self.ipPlayer_QLineEdit.text().strip()
        debugging = self.debugMode_QCheck.isChecked()
        values = {'sender': (self.SENDER_IP, self.SENDER_PORT),
                  'receiver': (self.RECEIVER_IP, self.RECEIVER_PORT),
                  'socket': self.sock,
                  'gamemode': (self.gmChosen, self.targetScore),
                  'debugging': debugging
                  }

        if not self.playerIP_empty():
            self.game_window = Game(values, 1 if self.P1_QRatio.isChecked() else 2)
            if self.game_window:
                self.game_window.show()
            self.close()


class Game(QMainWindow):

    def __init__(self, valuesDict: dict, player: int):
        super().__init__()

        # Starting variables
        self.player = player
        self.deckWindow = None
        self.debugMenu = None

        # Load the UI
        if self.player == 1:
            uic.loadUi("./data/UIs/cardGame-Player1.ui", self)
            self.setWindowTitle("War Game - Player 1")
        else:
            uic.loadUi("./data/UIs/cardGame-Player2.ui", self)
            self.setWindowTitle("War Game - Player 2")

        # Fixes the window
        self.setWindowIcon(QIcon("./data/images/QTImages/carte.png"))
        self.setFixedSize(self.size())
        self.show() # Then displays it.

        # Loads from the dictionnary the values associated to the ips for both sender and receiver.
        self.SENDER_IP, self.SENDER_PORT = valuesDict['sender']
        self.RECEIVER_IP, self.RECEIVER_PORT = valuesDict['receiver']

        self.sock = valuesDict['socket']
        self.debugging = valuesDict['debugging']
        if self.debugging:
            print("You've enter debug mode!")
            print("\n----------------------\n")
            print(f"Sender: {self.SENDER_IP}:{self.SENDER_PORT}")
            print(f"Receiver: {self.RECEIVER_IP}:{self.RECEIVER_PORT}")
            print("\n----------------------\n")

        # Creating a repeating clock that calls the processData function every 100ms.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.processData)
        self.timer.start(100)

        # Connect the buttons.
        self.cardVault_QButton.clicked.connect(self.showDeck)
        self.send_QButton.clicked.connect(partial(self.sendMessage, 1 if self.player == 1 else 2))
        if self.debugging and self.player == 1:
            self.seeDebugMenu_QButton.clicked.connect(self.seeDebugMenu)

        # Initialize the variables.
        self.currentRound = 1
        self.game_mode, self.targetScore = valuesDict['gamemode']
        self.gm_QLabel.setText(f"First to get : {self.targetScore} points")

        # Create the players using classes, so it's more efficient and easier to read.
        self.P1 = Player(1) # Init the player 1 class
        self.P2 = Player(2) # Init the player 2 class

        self.cards = None
        self.battle = 0

        # Displays the cards on the screen.
        self.changeCards(self.currentCardDisplayP1_QLabel, self.currentCardNameP1_QLabel, self.P1.currentCard)
        self.changeCards(self.currentCardDisplayP2_QLabel, self.currentCardNameP2_QLabel, self.P2.currentCard)


        # Creates the cards then shuffles them to associate them to the decks of both players.
        if self.player == 1:
            # Only player 1 can load the main deck to avoid double decks
            # and also to void confusion between the players, on whose deck right.

            # Init the cards to be distributed
            self.cards = Deck()
            for _ in range(2):
                self.cards.shuffleCards()
                # then shuffle them

            for _ in range(0, len(self.cards.deck) // 2):
                self.P1.deck.append(self.cards.takeCard())
                # Distributes the cards into P1's deck

            for _ in range(0, len(self.cards.deck)):
                self.P2.deck.append(self.cards.takeCard())
                # Distributes the rest of the cards into P2's deck

            # Prints a lot of values to help when debugging.
            if self.debugging:
                print(f"Player 1's Deck: {self.P1.deck}")
                print(f"Player 2's Deck: {self.P2.deck}")


            # Sends the variables to player 2.
            self.sock.connect((self.RECEIVER_IP, self.RECEIVER_PORT)) # Connect to the receiver's ip and port.
            data = ({"P2": (self.P2.deck, self.P2.waitingDeck, self.P2.battleDeck, self.P2.currentCard, self.P2.victoryCount, self.P2.playerNumber, self.P2.r),
                     "P1": (),
                     "cards": self.cards,
                     "targetScore": self.targetScore})
            if not self.debugging:
                self.P2.deck = [] # Clearing P2's deck from P1's knowledge to prove that P1 doesn't need to know P2's desk for this game to work.

            # For P2, P1 would send:
            # self.P1.r, self.P1.currentCard, self.P1.victoryCount

            # For P1, P2 would send:
            # self.P2.r, self.P2.currentCard, self.P2.victoryCount

            self.sock.send(pickle.dumps(data)) # sends the images hashed into bytes to player 2 for it to receive every value it requires.
            
            if not self.debugging:
                self.seeDebugMenu_QButton.hide()
                
    def seeDebugMenu(self):
        if self.debugMenu:
            self.debugMenu.close()
        
        self.debugMenu = debugMenu(self)
        self.debugMenu.show()
    
    def showDeck(self):
        """
        Shows your deck with another window.
        """
        if self.deckWindow:
            self.deckWindow.close()

        if self.player == 1:
            self.deckWindow = cardMenu(self, self.P1)
        elif self.player == 2:
            self.deckWindow = cardMenu(self, self.P2)
        if self.deckWindow:
            self.deckWindow.show()

    def processData(self):
        """
        Tries to get the images from the potential incoming images.
        Then it loads said data with the pickle module.
        Finally, it loads the images into the variables of each player correctly.
        """
        try:
            raw_data, server = self.sock.recvfrom(1024)
            if self.debugging: print("Data received from {}:{}\nMessage: {}\n".format(server[0], server[1], pickle.loads(raw_data)))
        
        except socket.error:
            raw_data = None

        if raw_data is not None:
            data = pickle.loads(raw_data) # Decodes the raw images (bytes) into readable images.

            if self.player == 2: # Checking for Player 2.
                if data["P1"] == (): # First time receiving the images to set the variables for P2
                    self.P2.deck = data["P2"][0]
                    self.P2.waitingDeck = data["P2"][1]
                    self.P2.battleDeck = data["P2"][2]
                    self.P2.currentCard = data["P2"][3]
                    self.P2.victoryCount = data["P2"][4]
                    self.P2.playerNumber = data["P2"][5]
                    self.P2.r = False
                    self.cards = data["cards"]
                    self.targetScore = data["targetScore"]
                    print("Data has been received!\n")
                    self.updateComponents()


                if data["P1"] != (): # The game has started and players are ready.
                    self.P1.r = data["P1"][0]
                    self.P1.currentCard = data["P1"][1]

            elif self.player == 1: # Checking for Player 1.
                if data["P1"] == ():
                    data = ({"P2": (self.P2.r , self.P2.currentCard, self.P2.victoryCount),
                             "P1": (self.P1.r, self.P1.currentCard, self.P1.victoryCount)})
                    if self.debugging: print("Data to player 2 has been received! Clearing the images received...\nCleared!\n")
                
                self.P2.r = data["P2"][0]
                self.P2.currentCard = data["P2"][1]
                    
            self.updateComponents()

    def updateComponents(self):
        if self.P1.r and self.P2.r:
            self.changeCards(self.currentCardDisplayP1_QLabel, self.currentCardNameP1_QLabel, self.P1.currentCard)
            self.changeCards(self.currentCardDisplayP2_QLabel, self.currentCardNameP2_QLabel, self.P2.currentCard)
            self.send_QButton.setEnabled(True)
            self.cardVault_QButton.setEnabled(True)
            self.P1.r = False
            self.P2.r = False
            self.gameLoop()

    def sendMessage(self, player):
        """
        Sends the message to the other player.
        """
        if player == 1:
            if self.P1.currentCard != (-1,-1) and self.P1.currentCard != (): # Make sure that the player has selected a card.
                self.P1.r = True
                self.send_QButton.setEnabled(False)
                self.cardVault_QButton.setEnabled(False)
                
                message = ({"P1": (self.P1.r, self.P1.currentCard),"P2": (self.P2.r, self.P2.currentCard)})
                self.updateComponents()

                if self.debugging: print(f"Message sent: {message}\nTo Receiver: {self.RECEIVER_IP}:{self.RECEIVER_PORT}\n")
                self.sock.sendto(pickle.dumps(message), (self.RECEIVER_IP, self.RECEIVER_PORT)) # Send the message to the other player.
            else:
                # If you forgot to select a card, it will display a warning.
                warningBox("Careful!", "Please select a card.", "./data/images/QTImages/warning.png")
                self.P1.r = False

        elif player == 2:
            # Same stuff here.
            if self.P2.currentCard != (-1,-1) and self.P2.currentCard != ():
                self.P2.r = True
                if not self.debugging and self.player == 2:
                    self.send_QButton.setEnabled(False)
                    self.cardVault_QButton.setEnabled(False)
                
                # Making sure that at least one play has been ready.
                message = ({"P1": (self.P1.r, self.P1.currentCard),"P2": (self.P2.r, self.P2.currentCard)})
                self.updateComponents()
    
                if self.debugging: print(f"Message sent: {message}\nTo Receiver: {self.RECEIVER_IP}:{self.RECEIVER_PORT}\n")
                self.sock.sendto(pickle.dumps(message), (self.RECEIVER_IP, self.RECEIVER_PORT)) # Send the message to the other player.
            else:
                warningBox("Careful!", "Please select a card.", "./data/images/QTImages/warning.png")
                self.P2.r = False
            
    def changeCards(self, display, name, currentCard: tuple):
        """
        Changes the cards displayed in the game.
        With the text that shows what card is being played.
        :param display: QLabel from the window
        :param name: QLabel from the window
        :param currentCard: The player's current card (e.g.: self.P1.currentCard)
        """
        if currentCard == (-1, -1) or currentCard == ():
            display.setPixmap(QtGui.QPixmap(f"./data/images/cards/54.png"))
            name.setText("None")
        else:
            display.setPixmap(QtGui.QPixmap(f"./data/images/cards/{self.cards.images[currentCard]}.png"))
            name.setText(self.cards.cardName(currentCard))

    def checkDecks(self):
        """
        Checks if the deck is less than five cards to put the won cards back into the playable deck.
        """
        if self.debugging and self.player == 1:
            if len(self.P1.deck) < 5:
                self.P1.deck.extend(self.P1.waitingDeck)
                self.P1.waitingDeck.clear()
                
            if len(self.P2.deck) < 5:
                self.P2.deck.extend(self.P2.waitingDeck)
                self.P2.waitingDeck.clear()
        
        elif self.player == 1:
            if len(self.P1.deck) < 5:
                self.P1.deck.extend(self.P1.waitingDeck)
                self.P1.waitingDeck.clear()
        else:
            if len(self.P2.deck) < 5:
                self.P2.deck.extend(self.P2.waitingDeck)
                self.P2.waitingDeck.clear()
    
    def gameLogic(self):
        roundWinner = ""
        if self.P1.currentCard[0] == self.P2.currentCard[0]:
    
            ##### If it's a draw #####
            self.battle += 2
            roundWinner = "No-one"
            
        if self.battle != 0:
            if self.player == 1:
                self.P1.battleDeck.append(self.P1.currentCard)
                self.P1.battleDeck.append(self.P2.currentCard)
                self.P1.deck.pop(self.P1.deck.index(self.P1.currentCard))
                self.P1.currentCard = ()
        
            if self.player == 2:
                self.P2.battleDeck.append(self.P1.currentCard)
                self.P2.battleDeck.append(self.P2.currentCard)
                self.P2.deck.pop(self.P2.deck.index(self.P2.currentCard))
                self.P2.currentCard = ()
                
            self.battle -= 1
                
        elif self.battle == 0:
            if self.P1.currentCard[0] > self.P2.currentCard[0]:
                roundWinner = "Player 1"
                self.changeDecks(self.P1, self.P2)

            elif self.P1.currentCard[0] < self.P2.currentCard[0]:
                roundWinner = "Player 2"
                self.changeDecks(self.P2, self.P1)
            
        return roundWinner
    
    def changeDecks(self, winner, loser):
        """
        Logic of the game loop.
        """
        print(winner.playerNumber, loser.playerNumber)
        winner.victoryCount += 1
        
        ############ WINNER ############
        
        if self.debugging and self.player == 1:
            winner.waitingDeck.append(winner.currentCard)
            winner.waitingDeck.append(loser.currentCard)
            winner.deck.pop(winner.deck.index(winner.currentCard))
            winner.currentCard = ()

            if len(winner.battleDeck) != 0:
                winner.waitingDeck.extend(winner.battleDeck)
                winner.battleDeck.clear()
                
            loser.deck.pop(loser.deck.index(loser.currentCard))
            loser.currentCard = ()
            
            if len(loser.battleDeck) != 0:
                loser.battleDeck.clear()
        
        elif self.player == 1 and winner.playerNumber == 1:
            
                
            # First we put the won cards in the waiting deck.
            winner.waitingDeck.append(winner.currentCard)
            winner.waitingDeck.append(loser.currentCard)
            
            # Then we remove the current played card from the deck of winner.
            winner.deck.pop(winner.deck.index(winner.currentCard))
            
            # Finally, we clear the current card, so it can avoid from being played again.
            winner.currentCard = ()
            
            
            # When we just won a draw, we put the battle decks in the deck of player 1.
            if len(winner.battleDeck) != 0:
                winner.waitingDeck.extend(winner.battleDeck)
                winner.battleDeck.clear()
                
                
                
        elif self.player == 2 and winner.playerNumber == 2:
                
            # First we put the won cards in the waiting deck.
            winner.waitingDeck.append(winner.currentCard)
            winner.waitingDeck.append(loser.currentCard)
            
            # Then, we remove the current played card from the deck of winner.
            winner.deck.pop(winner.deck.index(winner.currentCard))
            
            # Finally, we clear the current card, so it can avoid from being played again.
            winner.currentCard = ()
            
            
            # When we just won a draw, we put the battle decks in the deck of player 1.
            if len(winner.battleDeck) != 0:
                winner.waitingDeck.extend(winner.battleDeck)
                winner.battleDeck.clear()
                
        ###############################
        
        ############ NOT WINNER ############
            
        # First, we remove the current played card from the deck of the one losing.
        elif self.player == 2 and loser.playerNumber == 2:
            loser.deck.pop(loser.deck.index(loser.currentCard))
            
            # Then we check if the battle deck is not empty.
            if len(loser.battleDeck) != 0:
                
                # if it is, we clear it.
                loser.battleDeck.clear()
                
            # Finally, we clear the current card, so it can avoid from being played again.
            loser.currentCard = ()
            
        elif self.player == 1 and loser.playerNumber == 1:
            loser.deck.pop(loser.deck.index(loser.currentCard))
            
            # Then we check if the battle deck is not empty.
            if len(loser.battleDeck) != 0:
                
                # if it is, we clear it.
                loser.battleDeck.clear()
                
            # Finally, we clear the current card, so it can avoid from being played again.
            loser.currentCard = ()
            
        ###############################
        
    def gameLoop(self):
        self.currentRound += 1
        if self.P1.victoryCount < self.targetScore and self.P2.victoryCount < self.targetScore:
            roundWinner = self.gameLogic()
            self.currentWinner_QLabel.setText(f"Round N°{self.currentRound} | WINNER : {roundWinner}")
            self.victoryCountP1_QLabel.setText(f"Score : {self.P1.victoryCount}")
            self.victoryCountP2_QLabel.setText(f"Score : {self.P2.victoryCount}")
            self.checkDecks()
            
        if self.P1.victoryCount >= self.targetScore:
            self.currentWinner_QLabel.setText(f"The game is over. | Game Won by Player 1!!")
            self.send_QButton.hide()
            self.cardVault_QButton.hide()
            self.P1.r, self.P2.r = False, False
        elif self.P2.victoryCount >= self.targetScore:
            self.currentWinner_QLabel.setText(f"The game is over. | Game Won by Player 2!!")
            self.send_QButton.hide()
            self.cardVault_QButton.hide()
            self.P1.r, self.P2.r = False, False         

        

app = QApplication(sys.argv)
window = startMenu()
window.show()

app.exec()
