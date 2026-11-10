import random
class Card:
    #Two parameters, color/number
    def __init__(self, colour, number):
        self.colour = colour
        self.number = number

    def __str__(self):
        return f"{self.colour} {self.number}"

    def __repr__(self):
        return str(self)

#whole deck of card
class Deck:
    def __init__(self):
        self.colours = ["red", "green", "yellow", "black", "blue"]
        self.numbers = [1,2,3,4,5,6,7,8,9]
        self.cards = []
        self.deck_of_card()

#Generate a complete deck of cards
    def deck_of_card(self):
        #List all possible permutations and combinations and add them to the card list
        for colour in self.colours:
            for number in self.numbers:
                self.cards.append(Card(colour, number))
                self.cards.append(Card(colour, number))

    #Shuffle the deck of cards.
    def shuffle(self):
        random.shuffle(self.cards)

    #draw cards
    def draw(self,count=1):
        card_drawn = []
        # loop to choose the number of cards drawn
        for _ in range(count):
            if not self.cards:
                break
            card_drawn.append(self.cards.pop(0))
        return card_drawn
