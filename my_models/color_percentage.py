import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

# -------------------------------
# 1. BACKGROUND REMOVAL (GrabCut)
# -------------------------------
def remove_background(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    mask = np.zeros(img.shape[:2], np.uint8)
    h, w = img.shape[:2]

    rect = (10, 10, w - 20, h - 20)  # assume clothing is centered
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    mask = np.where((mask == 0) | (mask == 2), 0, 1).astype("uint8")
    foreground = img * mask[:, :, np.newaxis]

    return foreground, mask


# -----------------------------------
# 2. COLOR CLUSTERING (K-Means)
# -----------------------------------
def extract_colors(foreground, mask, k=3):
    pixels = foreground[mask == 1]
    pixels = pixels.reshape(-1, 3)

    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(pixels)

    labels = kmeans.labels_
    centers = kmeans.cluster_centers_

    counts = np.bincount(labels)
    percentages = counts / counts.sum()

    return centers.astype(int), percentages


# -----------------------------------
# 3. RGB → HUMAN COLOR NAME
# -----------------------------------
def rgb_to_color_name(rgb):
    r, g, b = rgb

    if r < 40 and g < 40 and b < 40:
        return "black"
    if r > 200 and g > 200 and b > 200:
        return "white"
    if abs(r - g) < 15 and abs(r - b) < 15:
        return "grey"
    if r > g and r > b:
        return "red"
    if g > r and g > b:
        return "green"
    if b > r and b > g:
        return "blue"
    if r > 150 and g > 100 and b < 80:
        return "brown"
    return "other"


# -----------------------------------
# 4. FINAL FUNCTION (CALL THIS)
# -----------------------------------
def get_color_percentages(image_path, clusters=3):
    foreground, mask = remove_background(image_path)
    colors, percentages = extract_colors(foreground, mask, clusters)

    color_distribution = {}

    for rgb, pct in zip(colors, percentages):
        color_name = rgb_to_color_name(rgb)
        color_distribution[color_name] = round(pct * 100, 2)

    return color_distribution


# -----------------------------------
# 5. TEST
# -----------------------------------
if __name__ == "__main__":
    image_path = r"C:\Users\SHRIYA\Downloads\test.jpg"  # change if needed
    result = get_color_percentages(image_path)

    print("Dominant clothing colors (background removed):")
    for color, pct in result.items():
        print(f"{color}: {pct}%")
