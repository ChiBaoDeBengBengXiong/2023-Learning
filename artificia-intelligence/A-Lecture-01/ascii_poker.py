class Card(object):

    card_values = {
        'A': 14,  # value of the ace is high until it needs to be low
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '10': 10,
        'J': 11,
        'Q': 12,
        'K': 13
    }

    def __init__(self, suit, rank):
        """
        :param suit: The face of the card, e.g. Spade or Diamond
        :param rank: The value of the card, e.g 3 or King
        """
        self.rank = rank
        self.suit = suit.capitalize()

        if rank == 'T': rank = '10'

        self.points = Card.card_values[rank]
        # self.points = self.card_values[rank]


def ascii_version_of_card(*cards, hideen=False, return_string=True):
    """
    Instead of a boring text version of the card we render an ASCII image of the card.
    :param cards: One or more card objects
    :param return_string: By default we return the string version of the card, but the dealer hide the 1st card and we
    keep it as a list so that the dealer can add a hidden card in front of the list
    """
    # we will use this to prints the appropriate icons for each card
    suits_name = ['Spades', 'Diamonds', 'Hearts', 'Clubs']
    suits_symbols = ['♠', '♦️', '❤️', '♣']

    # create an empty list of list, each sublist is a line
    lines = [[] for i in range(9)]

    for index, card in enumerate(cards):
        # "King" should be "K" and "10" should still be "10"

        rank = card.rank
        space = ' '

        if suits_name.index(card.suit) == 1:
            suit_space = '  '
        elif suits_name.index(card.suit) == 2:
            suit_space = '  '
        else:
            suit_space = '   '

        if card.points < 10: space = ' '

        # if card.points >= 10:  # ten is the only one who's rank is 2 char long
        #     space = ''  # if we write "10" on the card that line will be 1 char to long
        # else:
        #     space = ' '  # no "10", we use a blank space to will the void

        # get the cards suit in two steps
        suit = suits_name.index(card.suit)
        suit = suits_symbols[suit]

        # add the individual card on a line by line basis

        if hideen:
            rank, suit = "*", "*"
            space, suit_space = ' ', '   '

        middle = '│    {}   │'.format(suit)

        lines[0].append('┌─────────┐')
        lines[1].append('│{}{}       │'.format(rank, space))  # use two {} one for char, one for space or char
        lines[2].append('│         │')
        lines[3].append('│         │')
        lines[4].append('|    {}{} |'.format(suit, suit_space))
        lines[5].append('│         │')
        lines[6].append('│         │')
        lines[7].append('│       {}{}│'.format(space, rank))
        lines[8].append('└─────────┘')

    result = []
    for index, line in enumerate(lines):
        result.append(''.join(lines[index]))

    # hidden cards do not use string
    if return_string:
        return '\n'.join(result)
    else:
        return result


def ascii_version_of_hidden_card(*cards, hidden_num=1):
    """
    Essentially the dealers method of print ascii cards. This method hides the first card, shows it flipped over
    :param cards: A list of card objects, the first will be hidden
    :return: A string, the nice ascii version of cards
    """
    # a flipper over card. # This is a list of lists instead of a list of string becuase appending to a list is better then adding a string
    lines = [
        ['┌─────────┐'], ['│░░░░░░░░░│'], ['│░░░░░░░░░│'], ['│░░░░░░░░░│'], ['│░░░░░░░░░│'], ['│░░░░░░░░░│'], ['│░░░░░░░░░│'], ['│░░░░░░░░░│'], ['└─────────┘']
    ] * hidden_num

    # store the non-flipped over card after the one that is flipped over
    cards_except_first = ascii_version_of_card(*cards[hidden_num:], return_string=False)
    for index, line in enumerate(cards_except_first):
        lines[index].append(line)

    # make each line into a single list
    for index, line in enumerate(lines):
        lines[index] = ''.join(line)

    # convert the list into a single string
    return '\n'.join(lines)


def print_by_hand_list(hand_list, hidden=False):
    cards = [Card(suit, point) for suit, point in hand_list]

    return ascii_version_of_card(*cards, hideen=hidden)


if __name__ == '__main__':
    # TEST CASES
    test_card_1 = Card('Diamonds', '4')
    test_card_2 = Card('Clubs', 'A')
    test_card_3 = Card('Spades', 'J')
    test_card_4 = Card('Hearts', '10')

    print(ascii_version_of_card(test_card_1, test_card_2, test_card_3, test_card_4))
    print(ascii_version_of_hidden_card(test_card_1, test_card_2, test_card_3, test_card_4, hidden_num=4))
