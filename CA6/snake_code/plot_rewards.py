import matplotlib.pyplot as plt
import csv

def plot_rewards(csv_file):
    episodes = []
    rewards_1 = []
    rewards_2 = []

    # Read the rewards from the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        for row in reader:
            episodes.append(int(row[0]))
            rewards_1.append(float(row[1]))
            rewards_2.append(float(row[2]))

    # Plot the rewards
    plt.plot(episodes, rewards_1, label='Snake 1')
    plt.plot(episodes, rewards_2, label='Snake 2')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.title('Rewards per Episode')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    plot_rewards('rewards.csv')
