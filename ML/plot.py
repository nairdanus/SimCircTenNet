import matplotlib.pyplot as plt

def plot_train_file(train_file):

    # Read the text file
    with open(train_file, 'r') as file:
        lines = file.readlines()

    # Initialize lists to store data
    loss_values = []
    accuracies = []

    # Parse the data
    for line in lines:
        if line.startswith("iter"):
            iter_loss = float(line.split(":")[1].strip())
            loss_values.append(iter_loss)
        elif line.startswith("acc"):
            accuracy = float(line.split(",")[0].split(":")[1].strip())
            accuracies.append(accuracy)

    # Plot the data
    plt.figure(figsize=(10, 5))

    plt.subplot(2, 1, 1)
    plt.plot(range(1, len(loss_values) + 1), loss_values, color='b')
    plt.title('Loss vs Iteration')
    plt.xlabel('Iteration')
    plt.ylabel('Loss')

    plt.subplot(2, 1, 2)
    plt.plot(range(1, len(accuracies) + 1), accuracies, color='r')
    plt.title('Accuracy vs Iteration')
    plt.xlabel('Iteration')
    plt.ylabel('Accuracy')

    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(train_file.replace(".txt", ".png"))
