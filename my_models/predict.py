import torch
from torchvision import transforms, models
from torch import nn
from PIL import Image

# MUST match training order exactly
CLASSES = ['dress', 'jacket', 'jeans', 'shirt', 'tshirt']

# Model
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, len(CLASSES))

# Load trained weights
model.load_state_dict(
    torch.load(r"clothing_classifier.pth", map_location="cpu")
)
model.eval()

# Transform
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

# Load image
img = Image.open(r"C:\Users\SHRIYA\Downloads\test.jpg")
img = transform(img).unsqueeze(0)

# Predict
with torch.no_grad():
    outputs = model(img)
    probs = torch.softmax(outputs, dim=1)
    conf, idx = torch.max(probs, 1)

confidence = conf.item() * 100
label = CLASSES[idx.item()]

if confidence < 60:
    print("Uncertain prediction")
else:
    print(f"Category: {label} | Confidence: {confidence:.2f}%")
