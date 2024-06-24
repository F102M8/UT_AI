import matplotlib.pyplot as plt
import csv
import os

def plot_summary_rewards(summary_csv_file, output_image):
    episodes = []
    rewards_1 = []
    rewards_2 = []

    with open(summary_csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            episodes.append(int(row[0]))
            rewards_1.append(float(row[1]))
            rewards_2.append(float(row[2]))

    plt.figure(figsize=(10, 6))
    plt.plot(episodes, rewards_1, label='Snake 1 (Summary)')
    plt.plot(episodes, rewards_2, label='Snake 2 (Summary)')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.title('Summary Rewards per Episode')
    plt.legend()

    plt.savefig(output_image)
    plt.show()

def plot_episode_rewards(episode_files_pattern):
    episode_files = [f for f in os.listdir('.') if f.startswith('rewards_episode_') and f.endswith('.csv')]
    for episode_file in episode_files:
        episode = episode_file.split('_')[2].split('.')[0]
        rewards_1 = []
        rewards_2 = []
        steps = []

        with open(episode_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                steps.append(int(row[0]))
                rewards_1.append(float(row[1]))
                rewards_2.append(float(row[2]))

        plt.figure(figsize=(10, 6))
        plt.plot(steps, rewards_1, label='Snake 1')
        plt.plot(steps, rewards_2, label='Snake 2')
        plt.xlabel('Step')
        plt.ylabel('Reward')
        plt.title(f'Rewards in Episode {episode}')
        plt.legend()

        plt.savefig(f'rewards_plot_episode_{episode}.png')
        plt.show()

if __name__ == "__main__":
    plot_summary_rewards('rewards.csv', 'rewards_summary_plot.png')
    plot_episode_rewards('rewards_episode_{}.csv')
