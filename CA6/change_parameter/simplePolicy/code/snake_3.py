from cube import Cube
from constants import *
from utility import *

import random
import numpy as np


class Snake_3:
    body = []
    turns = {}
    snake_counter = 0

    def __init__(self, color, pos, file_name=None):
        self.color = color
        self.pos = pos
        self.head = Cube(pos, color=color)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1
        self.state_space_size = (ROWS, ROWS, ROWS, ROWS)
        self.action_space_size = 4
        self.snake_number = Snake_3.snake_counter
        Snake_3.snake_counter += 1

        self.epsilon = 0.1

        if file_name:
            try:
                self.q_table = np.load(file_name)
                # print(f"Snake {self.snake_number}: Loaded Q-table from {file_name}")
                self.epsilon = 0.1
            except:
                self.q_table = np.zeros(self.state_space_size + (self.action_space_size,))
                # print(f"Snake {self.snake_number}: Q-table file not found. Initializing new Q-table for {color}.")
                self.epsilon = 1
        else:
            self.q_table = np.zeros(self.state_space_size + (self.action_space_size,))
            # print(f"Snake {self.snake_number}: Initializing new Q-table for {color}.")
            self.epsilon = 1

        self.lr = 0.2
        self.discount_factor = 0.95
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.1

    def get_state(self, snack):
        return (self.head.pos[0], self.head.pos[1], snack.pos[0], snack.pos[1])

    def get_optimal_policy(self, state):
        x, y, snack_x, snack_y = state
        q_values = self.q_table[state]

        max_q_value = np.max(q_values)
        actions_with_max_q_value = [i for i in range(len(q_values)) if q_values[i] == max_q_value]

        return actions_with_max_q_value[0]

    def make_action(self, state):
        chance = random.random()
        if chance < self.epsilon:
            action = random.randint(0, 3)
        else:
            action = self.get_optimal_policy(state)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        return action

    def update_q_table(self, state, action, next_state, reward):
        def is_valid(state_):
            flag = True
            for x in state_:
                if x >= ROWS or x <= 0:
                    flag = False
            return flag

        if (is_valid(state) and is_valid(next_state)):
            best_next_action = np.argmax(self.q_table[next_state])
            td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action]
            td_delta = td_target - self.q_table[state][action]
            self.q_table[state][action] += self.lr * td_delta

    def move(self, snack, other_snake):
        state = self.get_state(snack)
        action = self.make_action(state)
        #print(f"Snake {self.snake_number}: State={state}, Action={action}")

        if action == 0:  # Left
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 1:  # Right
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 2:  # Up
            self.dirny = -1
            self.dirnx = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        elif action == 3:  # Down
            self.dirny = 1
            self.dirnx = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

        # Create new state after moving and other needed values and return them
        new_state = self.get_state(snack)
        return state, new_state, action

    def check_out_of_board(self):
        headPos = self.head.pos
        if headPos[0] >= ROWS - 1 or headPos[0] < 1 or headPos[1] >= ROWS - 1 or headPos[1] < 1:
            #self.reset((random.randint(3, 18), random.randint(3, 18)))
            return True
        return False

    def calc_reward(self, snack, other_snake):
        reward = 0
        win_self, win_other = False, False

        if self.check_out_of_board():
            # Punish the snake for going out of bounds
            reward -= 500
            win_other = True
            self.reset(random_pos=True)
            # print(f"Snake {self.snake_number}: Went out of bounds. Resetting position.")
            return snack, reward, win_self, win_other

        if self.head.pos == snack.pos:
            self.addCube()
            snack = Cube(randomSnack(ROWS, self), color=(0, 255, 0))
            # Reward the snake for eating
            reward += 100
            # print(f"Snake {self.snake_number}: Ate snack. Growing in size.")

        distance_to_snack_before = np.abs(self.head.pos[0] - snack.pos[0]) + np.abs(self.head.pos[1] - snack.pos[1])
        distance_to_snack_after = np.abs(self.head.pos[0] + self.dirnx - snack.pos[0]) + np.abs(self.head.pos[1] + self.dirny - snack.pos[1])
        if distance_to_snack_after < distance_to_snack_before:
            # Reward for moving closer to the snack
            reward += 50
            #print(f"Snake {self.snake_number}: Moved closer to snack.")
        else:
            # Penalty for moving away from the snack
            reward -= 5
            #print(f"Snake {self.snake_number}: Moved away from snack.")

        if self.head.pos in list(map(lambda z: z.pos, self.body[1:])):
            # Punish the snake for hitting itself
            reward -= 500
            win_other = True
            self.reset(random_pos=True)
            # print(f"Snake {self.snake_number}: Hit itself. Resetting position.")
            return snack, reward, win_self, win_other

        if self.head.pos in list(map(lambda z: z.pos, other_snake.body)):
            if self.head.pos != other_snake.head.pos:
                # Punish the snake for hitting the other snake
                reward -= 1000
                win_other = True
                self.reset(random_pos=False)
                # print(f"Snake {self.snake_number}: Hit the other snake. Resetting position.")
            else:
                if len(self.body) > len(other_snake.body):
                    # Reward the snake for hitting the head of the other snake and being longer
                    reward += 200
                    win_self = True
                    # print(f"Snake {self.snake_number}: Hit the other snake's head and won.")
                elif len(self.body) == len(other_snake.body):
                    # No winner
                    reward += 0
                    # print(f"Snake {self.snake_number}: Head-on collision with equal length. No winner.")
                else:
                    # Punish the snake for hitting the head of the other snake and being shorter
                    reward -= 200
                    win_other = True
                    self.reset(random_pos=False)
                    # print(f"Snake {self.snake_number}: Hit the other snake's head and lost. Resetting position.")

        return snack, reward, win_self, win_other

    def reset(self, random_pos=False):
        if random_pos:
            pos = (random.randint(1, ROWS - 2), random.randint(1, ROWS - 2))
            self.head = Cube(pos, color=self.color)
            self.body = [self.head]
        else:
            self.head = Cube(self.pos, color=self.color)
            self.body = [self.head]
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1
        # print(f"Snake {self.snake_number}: Reset position to {self.head.pos}")

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0] - 1, tail.pos[1]), color=self.color))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0] + 1, tail.pos[1]), color=self.color))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] - 1), color=self.color))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] + 1), color=self.color))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy
        # print(f"Snake {self.snake_number}: Added new cube to body.")

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)

    def save_q_table(self, file_name):
        np.save(file_name, self.q_table)
        # print(f"Snake {self.snake_number}: Q-table saved to {file_name}")
