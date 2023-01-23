from itertools import product
from ascii_poker import print_by_hand_list
from cryptography.fernet import Fernet
from collections import deque
import random
from icecream import ic
from functools import reduce

color = ['Diamonds', 'Clubs', 'Spades', 'Hearts']
numbers = 'A23456789TJQK'


def char_to_num(c):
    global numbers

    if c in 'JQK': return 10
    else:
        return numbers.find(c) + 1


def usable_ace(hand):  # Does this hand have a usable ace?
    Ns = [char_to_num(n) for c, n in hand]
    return 1 in Ns and sum(Ns) + 10 <= 21


def sum_hand(hand):  # Return current hand total
    Ns = [char_to_num(n) for c, n in hand]

    if usable_ace(hand):
        return sum(Ns) + 10
    return sum(Ns)


def is_bust(hand):  # Is this hand a bust?
    # ic(hand)
    return sum_hand(hand) > 21


class BlackJack2PeoplePK:

    def __init__(self, name=None):
        self.action_space = [0, 1]
        self.observation_space = [list(range(31)), [0, 1], [0, 1]]
        self.memory_length = 2
        # current player's sum, opponent's action, with_ace
        self.player_cards = []
        self.opponent_cards = []
        self.state = [None, None, None]
        self.name = name
        self.opponent_actions = deque([-1] * self.memory_length, maxlen=3)  # -1 is for Non, 1 for hit, 0 for stick
        self.last_action = -1

    def __record_opponent_action(self, opponent_action):
        self.opponent_actions.append(opponent_action)

    @property
    def card_sum(self):
        return sum_hand(self.player_cards)

    def is_full(self):
        return self.card_sum == 21

    def is_bust(self):
        return is_bust(self.player_cards)

    def step(self, action, opponent_last_action, new_card=None):  # self's action
        assert action in self.action_space

        self.last_action = action
        self.__record_opponent_action(opponent_last_action)

        if action:  # action == 1, hit
            assert new_card is not None

            self.player_cards.append(new_card)

        return self.__get_obs()

    def __get_obs(self):
        return sum_hand(self.player_cards), tuple(self.opponent_actions), usable_ace(self.player_cards)

    def obs(self):
        obs_one_row = []
        _sum, _opponent_action, ace = self.__get_obs()
        obs_one_row.append(_sum)
        obs_one_row += list(_opponent_action)
        obs_one_row.append(ace)

        return tuple(obs_one_row)

    def reset(self, c1, c2):
        self.player_cards = [c1, c2]
        self.opponent_actions = [-1] * self.memory_length

        return self.__get_obs(), {}


class Judge:

    global color, numbers
    COLOR = color
    NUMBER = numbers

    def __init__(self, agent_1: BlackJack2PeoplePK, agent_2: BlackJack2PeoplePK):
        KEY = Fernet.generate_key()
        self.fernet = Fernet(KEY)
        self.encoded_strings = []
        self.agent_1 = agent_1
        self.agent_2 = agent_2
        self.all_cards = list(product(Judge.COLOR, Judge.NUMBER))
        random.shuffle(self.all_cards)

    @staticmethod
    def card_str(card):
        return '-'.join(card)

    def encode(self, card):
        self.encoded_strings = [self.fernet.encrypt(Judge.card_str(c).encode()) for c in self.agent_2.player_cards]

        return self.encoded_strings

    def decode(self):
        return [
            self.fernet.decrypt(s).decode() for s in self.encoded_strings
        ]

    def give_new_hand(self):
        for n in self.all_cards:
            yield n

    def render(self, log=False):
        for i, card in enumerate(self.agent_1.player_cards):
            if log:
                print(f'{self.agent_1.name}: {i+1}-card, : {self.card_str(card)}')

        player_1 = print_by_hand_list(self.agent_1.player_cards)

        for i, card in enumerate(self.agent_2.player_cards):
            secret = self.encode(card)
            if log:
                print(f'{self.agent_2.name}: {i+1}-card, : {secret}')

        player_2 = print_by_hand_list(self.agent_2.player_cards, hidden=True)

        return player_1, player_2


if __name__ == '__main__':
    agent1, agent2 = BlackJack2PeoplePK("Minquan"), BlackJack2PeoplePK("robot")
    judeger = Judge(agent1, agent2)

    distributor = judeger.give_new_hand()

    agent1.reset(next(distributor), next(distributor))
    agent2.reset(next(distributor), next(distributor))

    while True:
        # Agent-1
        action1 = random.choice(agent1.action_space)

        if action1 == 1:
            new_card = next(distributor)
        else:
            new_card = None

        state1, reward1, terimiated_1, _, _ = agent1.step(action1, agent2, new_card)

        player_cards, opponent_actions, useable_ace = state1

        # Agent-2

        action2 = random.choice(agent2.action_space)

        if action2 == 1:
            new_card = next(distributor)
        else:
            new_card = None

        state2, reward2, terimiated_2, _, _ = agent2.step(action2, agent1, new_card)

        player_cards, opponent_actions, useable_ace = state2

        p1, p2 = judeger.render()

        print(p1)
        print(p2)

        if terimiated_1 or terimiated_2:
            print('Done')
            break