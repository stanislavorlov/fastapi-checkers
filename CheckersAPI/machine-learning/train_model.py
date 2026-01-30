import numpy as np
import json
import tensorflow as tf
from tensorflow.keras import layers, models, Input
from sklearn.model_selection import train_test_split

def build_model(num_moves):
    # Board state input: 32 squares
    board_input = Input(shape=(32,), name='board')
    # Turn input: -1 or 1
    turn_input = Input(shape=(1,), name='turn')
    # Outcome/Target result input: -1, 0, or 1
    outcome_input = Input(shape=(1,), name='outcome')
    
    # Merge all inputs
    merged = layers.Concatenate()([board_input, turn_input, outcome_input])
    
    # Simple feed-forward network
    x = layers.Dense(512, activation='relu')(merged)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    
    x = layers.Dense(256, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    
    x = layers.Dense(128, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    
    # Output layer: probabilities for each move in vocabulary
    output = layers.Dense(num_moves, activation='softmax', name='move')(x)
    
    model = models.Model(inputs=[board_input, turn_input, outcome_input], outputs=output)
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def main():
    print("Loading preprocessed data...")
    X_board = np.load('X_board.npy')
    X_turn = np.load('X_turn.npy')
    X_outcome = np.load('X_outcome.npy')
    y_move = np.load('y_move.npy')
    
    with open('move_vocab.json', 'r') as f:
        move_vocab = json.load(f)
        
    num_moves = len(move_vocab)
    print(f"Data loaded. Samples: {len(X_board)}, Unique moves: {num_moves}")
    
    # Splitting data
    print("Splitting data into train and test sets...")
    indices = np.arange(len(X_board))
    train_idx, val_idx = train_test_split(indices, test_size=0.1, random_state=42)
    
    X_board_train, X_board_val = X_board[train_idx], X_board[val_idx]
    X_turn_train, X_turn_val = X_turn[train_idx], X_turn[val_idx]
    X_outcome_train, X_outcome_val = X_outcome[train_idx], X_outcome[val_idx]
    y_train, y_val = y_move[train_idx], y_move[val_idx]
    
    print("Building model...")
    model = build_model(num_moves)
    model.summary()
    
    print("Starting training...")
    # Training for 5 epochs with a decent batch size
    history = model.fit(
        x=[X_board_train, X_turn_train, X_outcome_train],
        y=y_train,
        validation_data=([X_board_val, X_turn_val, X_outcome_val], y_val),
        epochs=5,
        batch_size=1024,
        verbose=1
    )
    
    print("Saving model...")
    model.save('checkers_model.keras')
    print("Training complete and model saved as 'checkers_model.keras'.")

if __name__ == "__main__":
    main()
