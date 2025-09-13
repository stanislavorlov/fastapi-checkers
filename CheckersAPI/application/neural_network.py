# --- Conceptual Neural Network ---
import random
import numpy as np


class NeuralNetwork:
    """
    A placeholder for the deep neural network.
    """

    def __init__(self, input_shape, output_size):
        self.input_shape = input_shape
        self.output_size = output_size
        print(f"Neural Network initialized with input shape: {input_shape}, output size: {output_size}")

    """
    Should be Keras implementation.
    """
    def predict(self, board_state):
        policy_probs = np.random.rand(self.output_size)
        policy_probs /= policy_probs.sum()
        value = random.uniform(-1, 1)
        return policy_probs, value