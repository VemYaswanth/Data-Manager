# 🔐 Secure File Vault  
### A GitHub-style Local Dashboard for Encrypted Project & File Management  
_Local, Offline, Zero-Cloud, Fully Encrypted_

![Banner](docs/banner.png) <!-- optional screenshot placeholder -->

---

## 📌 Overview
Secure File Vault is a **local-only, privacy-first file management system** inspired by GitHub’s clean dashboard UI.  
You can organize projects, upload files, explore directories, and view analytics — **all encrypted**, stored **offline**, and **never uploaded to the cloud**.

Built for developers, analysts, and creators who want a **secure personal workspace** on their laptop or server.

---

## ✨ Features

### 🛡️ Security
- AES-256 file encryption  
- Local SQL database (SQLite / SQLCipher compatible)  
- Master key stored safely in `.env`  
- Zero cloud dependencies  

### 📂 File & Project Management
- GitHub-like **project cards**  
- Encrypted file storage per project  
- File explorer UI  
- Upload panel (future UI upgrade)  
- Auto-generated metadata & indexing  

### 📊 Analytics Dashboard
- File type distribution  
- Storage usage  
- Project statistics  
- Tag manager (coming soon)  

### 🖥️ Frontend
- Streamlit-based dashboard  
- Dark GitHub theme  
- Responsive sidebar & navigation  

### ⚙️ Backend
- Modular backend structure  
- Encryption engine  
- File I/O handler  
- Project & index services  
- REST-style API (future FastAPI integration)  

---

## 📁 Directory Structure

```
secure-file-vault/
│
├── backend/             # Encryption, DB, file operations
├── frontend/            # Streamlit dashboard
├── storage/             # Encrypted files
├── scripts/             # Utilities (backup, export, index)
├── tests/               # Unit tests
├── config/              # Settings, themes, env template
│
├── run.py               # Start the system
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/secure-file-vault.git
cd secure-file-vault
```

### 2️⃣ Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration

### Create `.env` file:
```
MASTER_KEY=<your-secure-key>
DB_PASSWORD=<optional-db-pass>
```

### Example:
A complete `.env.example` is inside `config/environment.example`.  

---

## ▶️ Running the Application

### Start the backend + UI
```bash
python run.py
```

Or directly run Streamlit:

```bash
streamlit run frontend/dashboard.py
```

Backend services will run automatically when accessed through the UI.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | Python |
| Database | SQLite / SQLCipher |
| Encryption | AES-256 (cryptography library) |
| Analytics | Python + Pandas |
| Environment | Local-only, offline |

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 🛣️ Roadmap

- [ ] File upload from dashboard  
- [ ] Project creation UI  
- [ ] FastAPI backend with token auth  
- [ ] Multi-user support  
- [ ] Drag-and-drop file explorer  
- [ ] Full encryption key rotation UI  

---

## 🤝 Contributing

Pull requests are welcome!  
Before contributing, run:

```bash
pytest
flake8
```

---

## 📜 License
This project is licensed under the **MIT License**.  
See `LICENSE` for details.

---

## 💬 Support
If you need help, open an issue or contact the maintainer.  
Future documentation + screenshots will be available in `/docs`.

---

## ⭐ Like This Project?
Consider starring ⭐ the repo — it motivates continued development!
