# 🔐 Secure Image Screening (Steganalysis Tool)

Secure Image Screening is a Python-based desktop application designed to detect hidden information in digital images using statistical steganalysis techniques. It provides an intuitive GUI for analyzing images and identifying potential data concealment.

---

## 📌 Overview

The system analyzes images using multiple forensic features such as chi-square statistics, LSB distribution, entropy, and texture noise. These features are combined using a normalized scoring model to classify images as clean or suspicious, along with a confidence score.

---

## 🚀 Features

* GUI-based image upload and preview
* Multi-feature steganalysis:

  * Chi-square test
  * LSB analysis
  * Entropy calculation
  * Texture noise detection
* Risk classification (Low, Medium, High)
* Confidence scoring with explanations
* Session history tracking
* Basic hidden message extraction

---

## 🛠️ Technology Stack

* Python
* Tkinter
* NumPy
* SciPy
* Pillow

---

## 📦 Installation

```bash
git clone https://github.com/your-username/steg-detector.git
cd steg-detector
pip install -r requirements.txt
```

---

## ▶️ Run the Tool

```bash
python steg_detector.py
```

---

## 📂 Project Structure

```
steg_detector/
│
├── steg_detector.py      # Main GUI + forensic detection system
├── train_model.py        # Optional ML training script (not required for main tool)
├── stego_model.pkl       # Saved trained model (if ML is used)
│
└── dataset/              # Image dataset
    ├── clean/            # Clean images
    └── stego/            # Stego images
```

---

## ⚠️ Notes

* The core system uses **statistical steganalysis (no ML required)**
* `train_model.py` and `stego_model.pkl` are optional and can be used for experimentation
* Hidden message extraction works only for simple LSB encoding
* Encrypted or compressed payloads may not be readable

---

## 🎯 Use Cases

* Academic projects
* Digital forensics demonstrations
* Cybersecurity learning

---

## 👤 Author

Ishika
Ashmeet

---

## 📜 License

For academic and educational use only.
