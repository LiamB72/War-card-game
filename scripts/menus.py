from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea


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