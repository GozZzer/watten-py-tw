import math
import random

from watten_py.tools.game import convert_to_readable


class CardBase:
    def __init__(self, card_id: int):
        """
        The Base Class of a Card to represent a Playing-Card

        :param card_id: The id of the card
        """
        self.card_id: int = card_id

    def __int__(self):
        # Returns the id of the given card
        return int(self.card_id)

    def __repr__(self):
        # Returns the representation of the given card
        color, name = convert_to_readable(int(self))
        return f"<CardBase color={color}, name={name}>"

    def __eq__(self, other):
        # Checks if a card has the same color as another one
        if isinstance(other, CardBase):
            if math.floor(int(self) / 8) == math.floor(int(other) / 8):
                return True
            else:
                return False
        elif isinstance(other, int):
            if math.floor(self.card_id / 8) == math.floor(other / 8):
                return True
            else:
                return False
        else:
            raise NotImplementedError

    def __gt__(self, other):
        if isinstance(other, CardBase):
            if other == self:
                if (int(self) % 8) > (int(other) % 8):
                    return True
                else:
                    return False
            return False
        else:
            raise NotImplementedError

    def __lt__(self, other):
        if isinstance(other, CardBase):
            if other == self:
                if (int(self) % 8) < (int(other) % 8):
                    return True
                else:
                    return False
            return False
        else:
            raise NotImplementedError


class CardDek:
    def __init__(self, cards: list[CardBase]):
        """
        Create a new deck of Cards

        :param cards: The list of cards a Dek includes
        """
        self.cards: list = cards

    def __repr__(self):
        return f"<CardDek cards=len({len(self.cards)})>"

    def __iter__(self):
        return self.cards

    def __getitem__(self, item):
        return self.cards[item]

    def __len__(self):
        return len(self.cards)

    def deal_top_card(self, cards=1):
        """
        Return an amount of cards and delete them from the deck

        :param cards: The amount of cards
        :return: The selected cards
        """
        tc = self.cards[:cards]
        self.cards = self.cards[cards:]
        return tc

    @staticmethod
    def mix(cards: list[CardBase]) -> list[CardBase]:
        """
        Mix a deck of cards

        :param cards: The dek of cards to mix
        :return: The mixed dek
        """
        random.shuffle(cards)
        return cards

    @classmethod
    def get_mixed_dek(cls):
        """
        Returns mixed Card Dek

        :return: CardDek object with mixed cards
        """
        return cls(cards=cls.mix([CardBase(i) for i in range(33)]))