import os
import numpy as np
from PIL import Image
from scipy.stats import chisquare
from sklearn.ensemble import RandomForestClassifier
import joblib

# ===== FEATURE FUNCTIONS (SAME AS MAIN CODE) =====
def load_gray(path):
    return np.array(Image.open(path).convert("L"))

def chi_square_test(gray):
    pixels = gray.flatten()
    even = np.sum(pixels % 2 == 0)
    odd = np.sum(pixels % 2 == 1)
    observed = np.array([even, odd], dtype=float)
    expected = np.array([len(pixels)/2]*2)
    chi2, p = chisquare(observed, expected)
    return chi2, p

def lsb_ratio(gray):
    return np.mean(gray.flatten() & 1)

def entropy(gray):
    hist, _ = np.histogram(gray, bins=256, range=(0,256))
    hist = hist/np.sum(hist)
    hist = hist[hist>0]
    return -np.sum(hist*np.log2(hist))

def texture_noise(gray):
    gy = np.abs(np.diff(gray.astype(float), axis=0)).mean()
    gx = np.abs(np.diff(gray.astype(float), axis=1)).mean()
    return (gx+gy)/2

def second_order_entropy(gray):
    diff = np.diff(gray.flatten().astype(float))
    hist, _ = np.histogram(diff, bins=256, range=(-256,256))
    hist = hist/np.sum(hist)
    hist = hist[hist>0]
    return -np.sum(hist*np.log2(hist)) if len(hist)>0 else 0

# ===== LOAD DATASET =====
def extract_features(folder, label):
    X, y = [], []

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        try:
            gray = load_gray(path)

            chi2, p = chi_square_test(gray)
            lsb = lsb_ratio(gray)
            ent = entropy(gray)
            noise = texture_noise(gray)
            ent2 = second_order_entropy(gray)

            X.append([chi2, p, lsb, ent, noise, ent2])
            y.append(label)

        except:
            continue

    return X, y

# ===== MAIN TRAINING =====
clean_path = "dataset/clean"
stego_path = "dataset/stego"

X_clean, y_clean = extract_features(clean_path, 0)
X_stego, y_stego = extract_features(stego_path, 1)

X = np.array(X_clean + X_stego)
y = np.array(y_clean + y_stego)

print("Dataset size:", len(X))

# ===== TRAIN MODEL =====
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# ===== SAVE =====
joblib.dump(model, "stego_model.pkl")

print("✅ Model trained and saved as stego_model.pkl")
