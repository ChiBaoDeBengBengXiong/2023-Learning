from blackjack_pk import BlackJack2PeoplePK, Judge
import random
from icecream import ic
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import pickle
from tqdm import tqdm

action_name = {
    0: "STICK",
    1: "HIT"
}


QTable_1 = defaultdict(lambda: [0, 0])
QTable_2 = defaultdict(lambda: [0, 0])

QTables = [QTable_1, QTable_2]

state_action_value = defaultdict(lambda : [0, 0])


def random_policy(state, _s, q_tables=None):
    return 0
    # return random.choice(range(2))


def policy(state, _s, q_tables, eps=.1):

    q_table = q_tables[_s % 2]

    if random.random() < eps or len(set(q_table[state])) == 1:
        # if random epsilon or state all action's value are same
        return random.choice(range(len(q_table[state])))
    else:
        return np.argmax(q_table[state])


def train_one_episode(agent_1_name, agent_2_name, policy_1=None, policy_2=None, evaluate=False):
    agent1, agent2 = BlackJack2PeoplePK(agent_1_name), BlackJack2PeoplePK(agent_2_name)

    agent_policies = {
        agent1: policy_1,
        agent2: policy_2
    }

    agents = [agent1, agent2]
    random.shuffle(agents)
    first, second = agents

    judge = Judge(agent1, agent2)

    distributor = judge.give_new_hand()
    first.reset(c1=next(distributor), c2=next(distributor))
    second.reset(c1=next(distributor), c2=next(distributor))

    step = 0
    # reward == 1, means first agent win; reward == -1, mean second agent win;
    # reward == 0, mean draw or continue

    trajectory = []
    card_sums = []

    while True:
        # print(f'step == {step}')
        global QTable

        cur_agent = agents[step % len(agents)]
        state = cur_agent.obs()

        action = agent_policies[cur_agent](state, _s=step, q_tables=QTables)
        # action1 = random.choice(agent1.action_space)
        assert not cur_agent.is_bust(), cur_agent.player_cards

        new_card = next(distributor) if action == 1 else None
        opponent = list(set(agents) - {cur_agent})[0]
        cur_agent.step(action, opponent.last_action, new_card)

        if cur_agent.is_bust():
            reward = (-1) ** (step + 1)
            # if step == 0; cur bust, then reward is -1, mean second one wins
            # if step == 1; cur bust, then reward is +1, mean first one wins
            # first bust, second win; second bust, first win
            done = True
        elif action == opponent.last_action == 0:
            # 1 -> first agent win; 2 --> second agent win
            reward_occasion_map = {
                (cur_agent, 0): 1,
                (cur_agent, 1): -1,
                (opponent, 0): -1,
                (opponent, 1): 1,
            }

            if cur_agent.card_sum == opponent.card_sum: reward = 0
            else:
                bigger = cur_agent if cur_agent.card_sum > opponent.card_sum else opponent
                reward = reward_occasion_map[(bigger, step % 2)]
            done = True
        else:
            reward = -0.1 * ((-1)**(step+1))
            done = False

        log = False

        if log:
            ic(cur_agent.name)
            ic(cur_agent.player_cards)

        judge.render(log=log)

        trajectory.append( (state, step, action, reward) )

        if done:
            winner = None
            card_sums.append(cur_agent.card_sum)
            if reward == 1:  winner = first
            elif reward == -1: winner = second

            if log:
                if winner: print(winner)
                else: print('平局')
            break

        step += 1

    if not evaluate:
        return trajectory, card_sums
    else:
        return winner


def train(episode=10):
    trajectories_lengths = []
    final_sums = []
    evaluate_span = 1000
    evaluate_win_rate = []
    random_first_win_rate = []
    random_second_win_rate = []

    for i in tqdm(range(episode)):
        trajectory, final_sum = train_one_episode(
            'Agent-1',
            "Agent-2",
            policy_1=policy,
            policy_2=policy,
        )

        gamma = 0.99
        G = 0
        # print(f'trajectory length: {len(trajectory)}')

        trajectories_lengths.append(len(trajectory))
        final_sums.append(final_sum)

        visited = set()

        for (state, step, a, r) in trajectory[::-1]:
            G += r + gamma * G
            if (state, step % 2) not in visited:
                state_action_value[(state, a, step % 2)][0] += 1
                state_action_value[(state, a, step % 2)][1] += G
                visited.add((state, step % 2))

        global QTables

        for (state, a, role), (_time, _totel) in state_action_value.items():
            goal = _totel / _time
            goal = goal * ((-1) ** role)

            QTables[role][state][a] = goal

        if i % evaluate_span == 0:
            evaluate_time = 1000

            win_time = 0
            random_first_win = 0
            random_second_win = 0

            for e in range(evaluate_time):
                trained, _random = 'trained', 'random'

                _random_t, _random_2 = 'random_t', 'random_2'

                policy_map = {
                    trained: policy,
                    _random: random_policy,
                }
                test_agents = [trained, _random]
                random.shuffle(test_agents)

                _first, _second = test_agents

                _winner = train_one_episode(
                    agent_1_name=_first,
                    agent_2_name=_second,
                    policy_1=policy_map[_first],
                    policy_2=policy_map[_second],
                    evaluate=True
                )

                random_winner = train_one_episode(
                    agent_1_name=_random_t,
                    agent_2_name=_random_2,
                    policy_1=random_policy,
                    policy_2=random_policy,
                    evaluate=True
                )

                if _winner and _winner.name == trained: win_time += 1
                if random_winner and random_winner.name == _random_t: random_first_win += 1
                if random_winner and random_winner.name == _random_2: random_second_win += 1

            evaluate_win_rate.append(win_time / evaluate_time)
            random_first_win_rate.append(random_first_win / evaluate_time)
            random_second_win_rate.append(random_second_win / evaluate_time)

    average_span_len = [
        np.mean(trajectories_lengths[i: i + 20]) for i in range(0, len(trajectories_lengths), 20)
    ]

    average_span_final_sums = [
        np.mean(final_sums[i: i + 20]) for i in range(0, len(final_sums), 20)
    ]

    reward_span = 10

    # plt.plot(average_span_len)
    # plt.plot(average_span_final_sums)
    plt.plot(evaluate_win_rate, color='r')
    plt.plot(random_first_win_rate, color='g')
    plt.plot(random_second_win_rate, color='b')

    with open(f'black-pk-train-{episode}.pkl', 'wb') as f:
        pickle.dump([dict(q) for q in QTables], f)

    plt.show()


if __name__ == '__main__':
    train(100000)
