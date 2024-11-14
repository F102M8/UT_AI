from snake_1 import *
from snake_2 import *

from utility import *
from cube import *

import pygame
import numpy as np
from tkinter import messagebox
from snake_2 import Snake_2
from snake_1 import Snake_1


import csv
import os
import subprocess

def main():
    rewards_1 = []
    rewards_2 = []
    num_episodes = 50
    win_count_1 = 0
    win_count_2 = 0
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))

    snake_1 = Snake_1((255, 0, 0), (15, 15), SNAKE_1_Q_TABLE)
    snake_2 = Snake_2((255, 255, 0), (5, 5), SNAKE_2_Q_TABLE)
    snake_1.addCube()
    snake_2.addCube()
    snack = Cube(randomSnack(ROWS, snake_1), color=(0, 255, 0))
    clock = pygame.time.Clock()

    start_episode = 1
    if os.path.exists('rewards.csv'):
        with open('rewards.csv', 'r') as file:
            reader = csv.reader(file)
            lines = list(reader)
            if len(lines) > 1:  # There are previous results
                last_episode = int(lines[-1][0])
                start_episode = last_episode + 1

    try:
        for episode in range(start_episode, start_episode + num_episodes):
            total_reward_1 = 0
            total_reward_2 = 0

            rewards_step_1 = []
            rewards_step_2 = []

            while True:
                reward_1 = 0
                reward_2 = 0
                pygame.time.delay(10)
                clock.tick(10)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        if messagebox.askokcancel("Quit", "Do you want to save the Q-tables and rewards?"):
                            save(snake_1, snake_2)
                        pygame.quit()
                        exit()

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        np.save(SNAKE_1_Q_TABLE, snake_1.q_table)
                        np.save(SNAKE_2_Q_TABLE, snake_2.q_table)
                        pygame.time.delay(100)

                state_1, new_state_1, action_1 = snake_1.move(snack, snake_2)
                state_2, new_state_2, action_2 = snake_2.move(snack, snake_1)

                snack, reward_1, win_1, win_2 = snake_1.calc_reward(snack, snake_2)
                snack, reward_2, _, _ = snake_2.calc_reward(snack, snake_1)

                snake_1.update_q_table(state_1, action_1, new_state_1, reward_1)
                snake_2.update_q_table(state_2, action_2, new_state_2, reward_2)

                total_reward_1 += reward_1
                total_reward_2 += reward_2

                rewards_step_1.append(reward_1)
                rewards_step_2.append(reward_2)

                redrawWindow(snake_1, snake_2, snack, win)

                if win_1 or win_2:
                    print(f"Snake 1: {win_1, reward_1}, Snake 2: {win_2, reward_2}")

                    if win_1:
                        win_count_1 += 1
                    if win_2:
                        win_count_2 += 1

                    break

            rewards_1.append(total_reward_1 / (len(rewards_1) + 1))
            rewards_2.append(total_reward_2 / (len(rewards_1) + 1))
            print(f"Episode {episode}: Snake 1 Reward: {total_reward_1}, Snake 2 Reward: {total_reward_2}")
            snake_1.save_q_table(SNAKE_1_Q_TABLE)
            snake_2.save_q_table(SNAKE_2_Q_TABLE)
            #save_episode_rewards(episode, rewards_step_1, rewards_step_2)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        save_summary_rewards(start_episode, episode, rewards_1, rewards_2)
        save_win_counts(win_count_1, win_count_2)

def save_summary_rewards(start_episode, current_episode, rewards_1, rewards_2):
    file_exists = os.path.isfile('rewards.csv')
    with open('rewards.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Episode", "Snake 1 Reward", "Snake 2 Reward"])
        for i in range(current_episode - start_episode):
            writer.writerow([start_episode + i, rewards_1[i], rewards_2[i]])

def save_episode_rewards(episode, rewards_1, rewards_2):
    filename = f'rewards_episode_{episode}.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Step", "Snake 1 Reward", "Snake 2 Reward"])
        for step, (reward_1, reward_2) in enumerate(zip(rewards_1, rewards_2)):
            writer.writerow([step, reward_1, reward_2])

def save_win_counts(win_count_1, win_count_2):
    with open('win_counts.txt', 'w') as file:
        file.write(f'Snake 1 Wins: {win_count_1}\n')
        file.write(f'Snake 2 Wins: {win_count_2}\n')

if __name__ == "__main__":
    main()
