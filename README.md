# VERIFY_ID
## Secure Digital Identity Validation Platform


Verify-ID is an AI-powered identity verification system built to automate secure digital onboarding by combining document intelligence, biometric verification, and intelligent fraud detection.



## 📁 Project Structure

```
VerifyID/
│
├── pancard.py
├── requirements.txt
├── .gitignore
├── README.md
├── images/          # Add your input images here
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```
git clone https://github.com/YOUR_USERNAME/VERIFY_ID.git
cd VERIFY_ID
```

---

### 2️⃣ Create Virtual Environment

#### Windows:

```
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ Install Tesseract OCR (IMPORTANT)

Download and install from:
https://github.com/tesseract-ocr/tesseract

After installation, add this in your code if needed:

```
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

### 5️⃣ Add Input Images

* Add:

  * 📄 PAN card image
  * 🧍 Human photo 

Example:

```
├── pancard.jpg
├── person.jpg
```

---

### 6️⃣ Run the Project

```
python pancard.py
```

---

