import matplotlib.pyplot as plt
import re
import os

from reportlab.lib.pagesizes import A3, landscape, A4
from reportlab.pdfgen import canvas


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


def generate_report(train_file):

    with open(train_file, "r") as file:
        text = file.read()

    hyperparameters = {}
    metrics = {}

    # Extract hyperparameters
    hyperparameters["Dataset"] = re.search(r"DATASET = (.+)\n", text).group(1)
    hyperparameters["Syntax"] = re.search(r"SYNTAX = (.+)\n", text).group(1)
    hyperparameters["Ansatz"] = re.search(r"ANSATZ = (.+)\n", text).group(1)
    hyperparameters["Layers"] = re.search(r"LAYERS = (.+)\n", text).group(1)
    hyperparameters["Single Qubit Layers"] = re.search(r"SINGLE_LAYERS = (.+)\n", text).group(1)
    hyperparameters["Q_S"] = re.search(r"Q_S = (.+)\n", text).group(1)
    hyperparameters["Q_N"] = re.search(r"Q_N = (.+)\n", text).group(1)
    hyperparameters["Q_NP"] = re.search(r"Q_NP = (.+)\n", text).group(1)
    hyperparameters["Q_PP"] = re.search(r"Q_PP = (.+)\n", text).group(1)
    hyperparameters["Q_C"] = re.search(r"Q_C = (.+)\n", text).group(1)
    hyperparameters["Q_PUNC"] = re.search(r"Q_PUNC = (.+)\n", text).group(1)
    hyperparameters["X"] = re.search(r"𝓧 = (.+)\n", text).group(1)
    hyperparameters["Fidelity"] = re.search(r"FIDELITY = (.+)\n", text).group(1)

    # Extract metrics
    metrics_match = re.findall(r"iter \d+: (\d+\.\d+)\nacc: (\d+\.\d+), pr: (\d+\.\d+), re: (\d+\.\d+), f1: (\d+\.\d+)\n\s+Time passed: (\d+\.\d+)", text)
    if metrics_match:
        accuracies = [float(match[1]) for match in metrics_match]
        precisions = [float(match[2]) for match in metrics_match]
        recalls = [float(match[3]) for match in metrics_match]
        f1_scores = [float(match[4]) for match in metrics_match]
        total_time_passed = sum(float(match[5]) for match in metrics_match)
        avg_times_passed = total_time_passed / len(metrics_match)
        total_time_passed /= 3600
        metrics["Max Accuracy"] = max(accuracies)
        metrics["Max Precision"] = max(precisions)
        metrics["Max Recall"] = max(recalls)
        metrics["Max F1"] = max(f1_scores)
        metrics["Avg Time Passed"] = f"{avg_times_passed} s"
        metrics["Total Time Passed"] = f"{total_time_passed} h"
    
    metrics["Avg X"] = re.search(r"𝓧 has an average of (.+) with", text).group(1)
    metrics["Max X"] = re.search(r"with a maximum of (.+) of ", text).group(1)
    metrics["Max X Occurences"] = re.search(r"with a maximum of (.+) of (.+) o", text).group(2)
    metrics["Pram Angles"] = re.search(r"Operating on (.+) params", text).group(1)
    metrics["Avg Num Qubits"] = re.search(r"params on an average of (.+) qubits", text).group(1)

    

    # Create PDF
    filename = train_file.replace(".txt", ".pdf")
    doc = canvas.Canvas(filename, pagesize=A4)
    doc.setTitle("Training Report")

    if os.path.exists(plot := train_file.replace(".txt", ".png")):
        doc.drawImage(plot, 50, 450, preserveAspectRatio=True, width=470)

    y_position = 550
    # Draw table rows
    doc.setFont("Helvetica", 12)
    for key, value in hyperparameters.items():
        doc.drawString(70, y_position, key)
        doc.drawString(220, y_position, str(value))
        y_position -= 20

    # Add metrics section as a table
    y_position -= 45

    # Draw table headers
    doc.setFont("Helvetica-Bold", 12)
    doc.drawString(70, y_position, "Metric")
    doc.drawString(220, y_position, "Value")
    y_position -= 20

    # Draw table rows
    doc.setFont("Helvetica", 12)
    for key, value in metrics.items():
        doc.drawString(70, y_position, key)
        doc.drawString(220, y_position, str(value))
        y_position -= 20    

    doc.save()
    print(f"PDF report saved as '{filename}'")

if __name__ == "__main__":
    for train_file in os.listdir("createdTrainings"):
        if not train_file.endswith(".txt"): continue
        train_file = os.path.join("createdTrainings", train_file)

        plot_train_file(train_file)
        generate_report(train_file)
