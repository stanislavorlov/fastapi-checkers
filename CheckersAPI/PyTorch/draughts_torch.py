import json
import json5
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.nn.utils.rnn as rnn_utils
import random  # To illustrate a random sequence for prediction


# --- 1. Data Preprocessing ---
def preprocess_data(games):
    all_moves = set()
    for game in games:
        all_moves.update(game)
    move_to_index = {move: i + 1 for i, move in enumerate(sorted(list(all_moves)))}
    move_to_index['<pad>'] = 0
    index_to_move = {i: move for move, i in move_to_index.items()}
    vocab_size = len(move_to_index)
    training_sequences = []
    for game in games:
        for i in range(len(game) - 1):
            input_seq = [move_to_index[m] for m in game[:i + 1]]
            target = move_to_index[game[i + 1]]
            training_sequences.append((input_seq, target))
    return training_sequences, move_to_index, index_to_move, vocab_size


# --- 2. Custom Dataset and Collate Function ---
class DraughtsDataset(Dataset):
    def __init__(self, training_data):
        self.training_data = training_data

    def __len__(self):
        return len(self.training_data)

    def __getitem__(self, idx):
        input_seq, target = self.training_data[idx]
        input_tensor = torch.tensor(input_seq, dtype=torch.long)
        target_tensor = torch.tensor(target, dtype=torch.long)
        return input_tensor, target_tensor


def collate_fn(batch):
    inputs, targets = zip(*batch)
    padded_inputs = rnn_utils.pad_sequence(inputs, batch_first=True, padding_value=0)
    stacked_targets = torch.stack(targets, dim=0)
    return padded_inputs, stacked_targets


# --- 3. Model Architecture ---
class DraughtsModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers=1):
        super(DraughtsModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        logits = self.fc(lstm_out[:, -1, :])
        return logits


# --- 4. The `train_model` function ---
def train_model(model: DraughtsModel, dataloader, criterion, optimizer, epochs=10):
    model.train()  # Set the model to training mode
    for epoch in range(epochs):
        total_loss = 0
        for inputs, targets in dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")


# --- 5. The Prediction Function (from previous response) ---
def predict_next_move(model, move_to_index, index_to_move, current_game_sequence):
    model.eval()
    with torch.no_grad():
        indices = [move_to_index[m] for m in current_game_sequence]
        input_tensor = torch.tensor(indices, dtype=torch.long).unsqueeze(0)

        logits = model(input_tensor)
        predicted_index = torch.argmax(logits, dim=1).item()
        predicted_move = index_to_move[predicted_index]

    return predicted_move


# --- 6. Main Execution Block ---
if __name__ == "__main__":
    # Your raw data
    games = [
        ['11-15', '24-20', '8-11', '28-24', '9-13', '22-18', '15x22', '25x18', '4-8', '26-22', '10-14', '18x9', '5x14',
         '22-18', '1-5', '18x9', '5x14', '29-25', '11-15', '24-19', '15x24', '25-22', '24-28', '22-18', '6-9', '27-24',
         '8-11', '24-19', '7-10', '20-16', '11x20', '18-15', '2-6', '15-11', '12-16', '19x12', '10-15', '11-8', '15-18',
         '21-17', '13x22', '30-26', '18x27', '26x17x10x1'],
        ['11-15', '24-20', '8-11', '28-24', '4-8', '23-19', '9-14', '22-17', '15-18', '26-23', '5-9', '17-13', '1-5',
         '32-28', '14-17', '21x14', '10x17', '23x14', '9x18', '25-21', '6-10', '21x14', '10x17', '29-25', '17-22',
         '25-21', '11-16', '20x11x4', '3-8', '4x11', '7x16x23x32', '24-20', '22-25', '21-17', '25-29', '17-14', '2-6',
         '30-26', '29-25', '20-16', '12x19', '26-23', '19x26', '31x22x15', '25-22', '14-10', '22-18', '10x1', '18x11',
         '1-6', '11-15', '28-24'],
        ['11-15', '23-18', '8-11', '26-23', '10-14', '30-26', '7-10', '24-19', '15x24', '28x19', '2-7', '22-17', '4-8',
         '26-22', '11-16', '27-24', '16-20', '32-28', '20x27', '31x24', '8-11', '24-20'],
        ['11-15', '23-18', '8-11', '26-23', '10-14', '30-26', '6-10', '24-19', '15x24', '27x20', '4-8', '28-24',
         '12-16', '22-17', '8-12', '32-28', '10-15', '17x10', '7x14', '26-22', '2-6', '24-19', '15x24', '28x19', '6-10',
         '31-26', '1-6', '22-17', '11-15', '18x11', '14-18', '23x14x7', '16x23x30', '7-2', '9-13', '2x9', '13x22',
         '25x18', '5x14x23', '21-17'],
        ['11-15', '23-19', '9-14', '22-17', '5-9', '17-13', '14-18', '24-20', '15x24', '28x19', '9-14', '25-22',
         '18x25', '29x22', '8-11', '27-23', '11-15', '32-28', '15x24', '28x19', '4-8', '22-18', '8-11', '18x9', '11-15',
         '19-16', '12x19', '23x16', '1-5', '16-11', '5x14', '26-23', '7x16', '20x11', '15-18', '30-25', '18x27',
         '31x24', '14-18', '21-17', '18-23', '24-19', '23-26', '25-21', '26-31', '17-14', '10x17', '21x14', '31-26',
         '14-9', '26-23', '19-16', '23-18', '16-12', '18-14', '9-5', '14-10', '11-8', '10-7', '5-1', '7-10', '1-5',
         '10-14', '8-4', '6-9', '13x6', '2x9']
    ]

    # games = []
    # with open('moves.json', 'r') as f:
    #     for line in f:
    #         if line[0] != '[' and line[0] != ']':
    #             games.append(line)

    # 1. Preprocess the data
    training_data, move_to_index, index_to_move, vocab_size = preprocess_data(games)

    # 2. Create the Dataset and DataLoader
    draughts_dataset = DraughtsDataset(training_data)
    batch_size = 4
    draughts_dataloader = DataLoader(
        dataset=draughts_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn
    )

    # 3. Instantiate the model, loss function, and optimizer
    embedding_dim = 64
    hidden_dim = 128
    model = DraughtsModel(vocab_size, embedding_dim, hidden_dim)

    criterion = nn.CrossEntropyLoss(ignore_index=0)  # We ignore the padding index
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 4. Invoke the `train_model` function to start training
    print("Starting model training...")
    train_model(model, draughts_dataloader, criterion, optimizer, epochs=10)
    print("Training finished.")

    # save trained model into file
    torch.save(model.state_dict(), './trained_model.pth')

    # read trained model from files
    model.load_state_dict(torch.load('./trained_model.pth'))
    model.eval()

    # 5. Example prediction after training
    # Pick a random game from the dataset for a demonstration
    random_game = random.choice(games)
    # Pick a random point in that game (at least 2 moves in)
    split_point = random.randint(2, len(random_game) - 1)

    current_game_sequence = random_game[:split_point]
    actual_next_move = random_game[split_point]

    predicted_move = predict_next_move(model, move_to_index, index_to_move, current_game_sequence)

    print("\n--- Prediction Example ---")
    print("Current game sequence:", current_game_sequence)
    print("Predicted next move:", predicted_move)
    print("Actual next move:", actual_next_move)
    print("Prediction correct:", predicted_move == actual_next_move)