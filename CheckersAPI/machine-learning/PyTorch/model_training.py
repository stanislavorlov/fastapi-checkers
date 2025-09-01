import torch
import torch.nn as nn
import torch.optim as optim

# 1. Prepare dummy data: y = 2x + 1
x = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
y = torch.tensor([[3.0], [5.0], [7.0], [9.0]])

# 2. Define a simple linear model: y = wx + b
model = nn.Linear(in_features=1, out_features=1)

# 3. Define loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 4. Training loop
for epoch in range(5000):
    # Forward pass
    y_pred = model(x)
    loss = criterion(y_pred, y)

    # Backward pass
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Print every 100 epochs
    if epoch % 500 == 0:
        print(f"Epoch {epoch}: loss = {loss.item():.6f}")

# 5. Output learned parameters
[w, b] = model.parameters()
print(f"Learned weight: {w.item():.6f}, bias: {b.item():.6f}")

# Put model in evaluation mode
model.eval()

# Example input
new_x = torch.tensor([[5.0], [6.0]])

# Predict
with torch.no_grad():  # Disable gradient tracking for inference
    predictions = model(new_x)

# y = 2x + 1
print(predictions)

# torch.save(model.state_dict(), "linear_model.pth")
#model = nn.Linear(1, 1)           # Recreate model with same structure
#model.load_state_dict(torch.load("linear_model.pth"))
#model.eval()                      # Set to evaluation mode before inference