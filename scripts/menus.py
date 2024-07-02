from PyQt6 import uic
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from scripts.utils import warningBox
from random import randint
from scripts.players import Deck


class cardMenu(QWidget):

    def __init__(self, superWindow, player):

        super().__init__()

        self.gameWindow = superWindow
        self.player = player
        self.deck = self.player.deck
        self.debug = self.gameWindow.debugging

        self.setWindowTitle(f"War Card Game - Your Deck - Remaining Cards: {len(self.deck)} - Amount in the waiting deck: {len(self.player.waitingDeck)}")
        self.setWindowIcon(QIcon("data/images/QTImages/safe.png"))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea()
        self.setGeometry(200, 200, 700, 250)
        self.setFixedSize(700, 250)

        widget = QWidget()
        widget_layout = QHBoxLayout()
        widget.setLayout(widget_layout)

        # Creates a dynamic window of every card in the player's deck.
        if len(self.deck) != 0:
            for i in range(0, len(self.deck)):
                button = QPushButton()
                button.my_data = self.deck[i]
                button.clicked.connect(self.button_clicked)

                pixmap = QPixmap(f"data/images/cards/{self.gameWindow.deckGame.images[self.deck[i]]}.png")
                button.setIcon(QIcon(pixmap))
                button.setIconSize(pixmap.size())
                button.setMaximumSize(145, 196)
                button.setMinimumSize(145, 196)
                widget_layout.addWidget(button)
                widget_layout.addStretch(1)

            self.scroll_area.setWidget(widget)
            self.layout.addWidget(self.scroll_area)

    def button_clicked(self):
        sender = self.sender()
        if hasattr(sender, 'my_data'):
            if self.player.playerNumber == 1:
                self.player.currentCard = sender.my_data
                self.gameWindow.changeCards(self.gameWindow.currentCardDisplayP1_QLabel,self.gameWindow.currentCardNameP1_QLabel, self.gameWindow.client.P1.currentCard)

            elif self.player.playerNumber == 2:
                self.player.currentCard = sender.my_data
                self.gameWindow.changeCards(self.gameWindow.currentCardDisplayP2_QLabel,self.gameWindow.currentCardNameP2_QLabel, self.gameWindow.client.P2.currentCard)

        self.close()


class debugMenu(QWidget):

    def __init__(self, gameWindow):
        super().__init__()
        uic.loadUi("data/UIs/debugMenu.ui", self)
        self.setWindowTitle("War Card Game - Debug Menu")
        self.setWindowIcon(QIcon("data/images/QTImages/debug.png"))
        self.setFixedSize(self.size())
        self.gameWindow = gameWindow

        self.giveScoreButton.clicked.connect(self.debugScoreAdd)
        self.playRRoundButton.clicked.connect(self.playRRound)
        self.playRoundButton.clicked.connect(self.playRound)
        self.seeP1DeckButton.clicked.connect(self.seeP1Deck)
        self.seeP2DeckButton.clicked.connect(self.seeP2Deck)
        self.sendP2CardButton.clicked.connect(self.sendP2Card)
        self.playersDeckButton.clicked.connect(self.seePlayersDeck)
        self.playersBattleDeckButton.clicked.connect(self.seePlayersBattleDeck)
        self.playersWaitingDeckButton.clicked.connect(self.seePlayersWaitingDeck)

    def seePlayersDeck(self):
        print(f"\n----\nPlayer 1 Deck: {self.gameWindow.client.P1.deck}\nPlayer 2 Deck: {self.gameWindow.client.P2.deck}\n----\n")

    def seePlayersBattleDeck(self):
        print(
            f"\n----\nPlayer 1 Battle Deck: {self.gameWindow.client.P1.battleDeck}\nPlayer 2 Battle Deck: {self.gameWindow.client.P2.battleDeck}\n----\n")

    def seePlayersWaitingDeck(self):
        print(
            f"\n----\nPlayer 1 Waiting Deck: {self.gameWindow.client.P1.waitingDeck}\nPlayer 2 Waiting Deck: {self.gameWindow.client.P2.waitingDeck}\n----\n")

    def debugScoreAdd(self):
        score_to_add = self.giveScoreBox.value()
        playerToGiveTo = self.playerBox.currentText()
        if playerToGiveTo == 'Player 1':
            self.gameWindow.client.P1.victoryCount += score_to_add
            print(self.gameWindow.client.P1.victoryCount)
        else:
            self.gameWindow.client.P2.victoryCount += score_to_add
            print(self.gameWindow.client.P2.victoryCount)

    def sendP2Card(self):
        self.gameWindow.sendMessage(2)

    def playRRound(self):
        lenDeck1 = len(self.gameWindow.client.P1.deck)
        self.gameWindow.client.P1.currentCard = self.gameWindow.client.P1.deck[randint(0, lenDeck1 - 1)]
        self.gameWindow.changeCards(self.gameWindow.currentCardDisplayP1_QLabel,
                                    self.gameWindow.currentCardNameP1_QLabel, self.gameWindow.client.P1.currentCard)
        self.gameWindow.sendMessage(1)

        lenDeck2 = len(self.gameWindow.client.P2.deck)
        self.gameWindow.client.P2.currentCard = self.gameWindow.client.P2.deck[randint(0, lenDeck2 - 1)]
        self.gameWindow.changeCards(self.gameWindow.currentCardDisplayP2_QLabel,
                                    self.gameWindow.currentCardNameP2_QLabel, self.gameWindow.client.P2.currentCard)
        self.gameWindow.sendMessage(2)

    def playRound(self):
        self.gameWindow.client.P1.r = True
        self.gameWindow.sendMessage(1)
        self.gameWindow.client.P2.r = True
        self.gameWindow.sendMessage(2)

    def seeP1Deck(self):
        if self.gameWindow.deckWindow:
            self.gameWindow.deckWindow.close()

        self.gameWindow.deckWindow = cardMenu(self.gameWindow, self.gameWindow.client.P1)
        self.gameWindow.deckWindow.show()

    def seeP2Deck(self):
        if self.gameWindow.deckWindow:
            self.gameWindow.deckWindow.close()

        self.gameWindow.deckWindow = cardMenu(self.gameWindow, self.gameWindow.client.P2)
        self.gameWindow.deckWindow.show()

