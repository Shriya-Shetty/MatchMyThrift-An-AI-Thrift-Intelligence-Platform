import torch
from torchvision import datasets, transforms, models
from torch import nn, optim

# ========== SETTINGS ==========
DATA_DIR = r"C:\Users\SHRIYA\MatchMyThrift-An-AI-Thrift-Intelligence-Platform\my_models\itemtype_dataset"
BATCH_SIZE = 32
EPOCHS = 5
LR = 0.0001

# ========== TRANSFORMS ==========
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# ========== DATA ==========
train_data = datasets.ImageFolder(f"{DATA_DIR}/train", transform=transform)
val_data = datasets.ImageFolder(f"{DATA_DIR}/val", transform=transform)

train_loader = torch.utils.data.DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
val_loader = torch.utils.data.DataLoader(val_data, batch_size=BATCH_SIZE)

# ========== MODEL ==========
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, len(train_data.classes))

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# ========== TRAIN ==========
for epoch in range(EPOCHS):
    model.train()
    for imgs, labels in train_loader:
        preds = model(imgs)
        loss = criterion(preds, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"Epoch {epoch+1}/{EPOCHS} done")

# ========== SAVE ==========
torch.save(model.state_dict(), "clothing_classifier.pth")
print("Model trained and saved.")
