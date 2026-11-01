import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
from scipy.stats import chisquare
import threading
import joblib
import json

# ================= LOAD MODEL =================
try:
    model = joblib.load("stego_model.pkl")
except:
    model = None

# ================= IMAGE =================
def load_gray(path):
    img = Image.open(path).convert("L")
    return np.array(img)

# ================= FEATURES =================
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

# ================= RULE ENGINE =================
def forensic_engine(gray):
    chi2, p = chi_square_test(gray)
    lsb = lsb_ratio(gray)
    ent = entropy(gray)
    noise = texture_noise(gray)
    ent2 = second_order_entropy(gray)

    reasons = []

    # SMART REASONS (not just thresholds)
    if chi2 > 5000:
        reasons.append(f"Chi-square deviation detected ({chi2:.0f})")

    if p < 0.01:
        reasons.append("Statistical distribution is highly unlikely (p < 0.01)")

    if abs(lsb - 0.5) > 0.08:
        reasons.append(f"LSB imbalance detected ({lsb:.3f})")

    if ent < 4:
        reasons.append("Lower entropy suggests structured/modified data")

    if ent > 7.5:
        reasons.append("Very high entropy indicates possible hidden data")

    if noise > 1.2:
        reasons.append("Texture noise suggests possible embedding artifacts")

    return chi2, p, lsb, ent, noise, ent2, reasons

# ================= ML =================
def ml_predict(gray):
    if model is None:
        return "Model not loaded", 0

    chi2, p = chi_square_test(gray)
    lsb = lsb_ratio(gray)
    ent = entropy(gray)
    noise = texture_noise(gray)
    ent2 = second_order_entropy(gray)

    X = np.array([[chi2, p, lsb, ent, noise, ent2]])

    pred = model.predict(X)[0]
    probs = model.predict_proba(X)[0]
    conf = int(max(probs) * 100)

    if pred == 0:
        return "✔ Clean", conf
    elif pred == 1:
        return "⚠ Suspicious", conf
    else:
        return "🚨 Likely Stego", conf

# ================= ANALYSIS =================
def analyze():
    if not selected_image.get():
        return
    threading.Thread(target=run_analysis).start()

def run_analysis():
    gray = load_gray(selected_image.get())

    chi2, p, lsb, ent, noise, ent2, reasons = forensic_engine(gray)
    ml_v, ml_c = ml_predict(gray)

    result_box.delete("1.0", tk.END)

    # ===== FINAL RESULT =====
    result_box.insert(tk.END, "=== FINAL RESULT ===\n\n")
    result_box.insert(tk.END, f"{ml_v}\n")
    result_box.insert(tk.END, f"Confidence: {ml_c}%\n\n")

    # ===== FORENSIC REPORT =====
    result_box.insert(tk.END, "=== FORENSIC DETAILS ===\n\n")
    result_box.insert(tk.END, f"Chi-square: {chi2:.2f}\n")
    result_box.insert(tk.END, f"p-value: {p:.6f}\n")
    result_box.insert(tk.END, f"LSB ratio: {lsb:.4f}\n")
    result_box.insert(tk.END, f"Entropy: {ent:.4f}\n")
    result_box.insert(tk.END, f"Texture: {noise:.4f}\n")
    result_box.insert(tk.END, f"Second-order entropy: {ent2:.4f}\n\n")

    # ===== REASONS =====
    result_box.insert(tk.END, "Reasons:\n")
    if reasons:
        for r in reasons:
            result_box.insert(tk.END, f"- {r}\n")
    else:
        result_box.insert(tk.END, "- No strong anomalies detected\n")

    # ===== DIAGNOSTICS =====
    result_box.insert(tk.END, "\n=== DIAGNOSTICS ===\n")
    result_box.insert(tk.END, f"chi2>12000: {chi2>12000}\n")
    result_box.insert(tk.END, f"p<0.01: {p<0.01}\n")
    result_box.insert(tk.END, f"LSB dev>0.12: {abs(lsb-0.5)>0.12}\n")
    result_box.insert(tk.END, f"entropy>7.85: {ent>7.85}\n")
    result_box.insert(tk.END, f"H2>5.5: {ent2>5.5}\n")

    # ===== JSON =====
    data = {
        "chi2": chi2,
        "p": p,
        "lsb": lsb,
        "entropy": ent,
        "entropy2": ent2
    }

    result_box.insert(tk.END, "\nJSON:\n")
    result_box.insert(tk.END, json.dumps(data, indent=2))

# ================= EXTRA BUTTONS =================
def extract_data():
    result_box.insert(tk.END, "\n[!] Extraction module coming soon...\n")

def clear_all():
    result_box.delete("1.0", tk.END)
    canvas.delete("all")
    selected_image.set("")

# ================= GUI =================
root = tk.Tk()
root.title("🔍 Steganography Detector")
root.geometry("1000x600")
root.configure(bg="#f4f6f9")

selected_image = tk.StringVar()

# HEADER
tk.Label(root, text="🔍 Steganography Detector",
         font=("Segoe UI", 16, "bold"),
         bg="#1e293b", fg="white").pack(fill="x")

main_frame = tk.Frame(root, bg="#f4f6f9")
main_frame.pack(fill="both", expand=True)

# LEFT (IMAGE)
left_frame = tk.Frame(main_frame, bg="#f4f6f9")
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

canvas = tk.Canvas(left_frame, width=350, height=350, bg="white")
canvas.pack()

def show_preview(path):
    img = Image.open(path)
    img.thumbnail((350,350))
    img = ImageTk.PhotoImage(img)
    canvas.delete("all")
    canvas.create_image(175,175,image=img)
    canvas.image = img

def browse():
    path = filedialog.askopenfilename()
    if path:
        selected_image.set(path)
        show_preview(path)

tk.Button(left_frame, text="Browse Image", command=browse).pack(pady=10)

# RIGHT (RESULT)
right_frame = tk.Frame(main_frame, bg="#f4f6f9")
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

result_box = tk.Text(right_frame, font=("Consolas", 11))
result_box.pack(fill="both", expand=True)

# BUTTONS
btn_frame = tk.Frame(root, bg="#f4f6f9")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Analyze", width=15, command=analyze).pack(side="left", padx=10)
tk.Button(btn_frame, text="Extract", width=15, command=extract_data).pack(side="left", padx=10)
tk.Button(btn_frame, text="Clear", width=15, command=clear_all).pack(side="left", padx=10)

root.mainloop()
