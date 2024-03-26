from helpers. angle_preparation import get_angles, update_angles


class Classificator:  # TODO
    angles: dict = None
    prob = None
    meta = None
    learning_rate = None
    gold = None

    def __init__(self, prob: dict, meta: tuple, angle_names: set[str], learning_rate: float):
        self.angles = get_angles(angle_names)
        self.perturbed_angles = {n: a+0.001 for n, a in self.angles.items()}
        self.prob = prob
        self.meta = meta
        self.gold = meta[1]
        self.learning_rate = learning_rate

    def loss_function(self):
        # Cross-entropy loss
        return -np.log(self.prob[self.gold])

    def gradient_descent(self):
        gradients = []
        for i in range(len(self.angles)):
            # Perturb each rotation angle slightly
            perturbed_angles = np.copy(rotation_angles)
            perturbed_angles[i] += 0.001  # Small perturbation

            # Calculate the gradient using finite differences
            perturbed_output = self.simulate_circuit(perturbed_angles)
            perturbed_loss = self.loss_function()
            original_loss = self.loss_function()
            gradient = (perturbed_loss - original_loss) / 0.001

            gradients.append(gradient)

        # Update rotation angles using gradients and learning rate
        updated_angles = rotation_angles - learning_rate * np.array(gradients)

        return updated_angles

