# 🛡️ FraudRadar AI

<p align="center">
 
</p>

<h2 align="center">
AI-Powered Scam Detection Platform
</h2>

<p align="center">
Detect • Analyze • Prevent Digital Fraud
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Reflex](https://img.shields.io/badge/Reflex-0.9.6-purple)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?logo=supabase)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker)
![Railway](https://img.shields.io/badge/Railway-Deployed-black?logo=railway)

</p>

<p align="center">

🚀 **Live Demo**

https://fraudradar-v2-yash.up.railway.app

</p>

---

# 📖 Overview

FraudRadar AI is a production-ready scam detection platform designed to identify fraudulent digital content using Artificial Intelligence.

The application allows users to detect scams in:

- 📩 Messages
- 🌐 URLs
- 📱 QR Codes
- 🖼 Screenshots
- 🤖 AI Chat Assistance

The project is built using Python, Reflex, Supabase, Docker and Railway with a modern cloud-native deployment workflow.

---

# ✨ Features

- 🔐 Email Authentication
- 🤖 AI Scam Detection
- 🌐 URL Analysis
- 📱 QR Code Scanner
- 🖼 OCR Screenshot Analysis
- 💬 AI Assistant
- 📊 Dashboard Analytics
- 📜 Scan History
- 👤 User Profile
- ⚙ Settings
- 📱 Responsive Design
- ☁ Cloud Deployment

---
# 🛠 Tech Stack

| Category | Technologies |
|----------|--------------|
| Frontend | Reflex, Python, Tailwind CSS |
| Backend | Python, Reflex |
| AI | Groq API |
| Database | Supabase, PostgreSQL |
| OCR | Tesseract OCR, Pyzbar |
| Deployment | Docker, Railway |
| Version Control | Git, GitHub |



# 🏗 Architecture

```text
                User
                  │
                  ▼
        FraudRadar AI Website
                  │
                  ▼
         Reflex Frontend (Python)
                  │
                  ▼
          Reflex Backend Server
             │             │
             ▼             ▼
        Groq AI API    Supabase Auth
                            │
                            ▼
                      PostgreSQL Database
```


# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/Yashr4635/FraudRadar-v2.git
```

Move into the project

```bash
cd FraudRadar_v2
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

### macOS/Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
reflex run
```

---

# 🐳 Docker

Build

```bash
docker compose build
```

Run

```bash
docker compose up
```

---

# ☁️ Deployment

FraudRadar AI is deployed using **Railway** and containerized with **Docker**.

Deployment workflow:

```
GitHub
    │
    ▼
Docker Image
    │
    ▼
Railway
    │
    ▼
Live Application
```

---

# 🔐 Authentication

Authentication is powered by **Supabase Authentication**.


Supported features:

- Email Registration
- Secure Login
- Session Management
- Protected Dashboard



# 📁 Project Structure

```
FraudRadar_v2/
│
├── assets/
├── screenshots/
├── fraudradar_ai_scam_detection_v2/
│   ├── components/
│   ├── states/
│   └── ...
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── rxconfig.py
└── README.md
```

---

# 🧠 Challenges Solved

During development, several real-world engineering challenges were addressed:

- Integrated Supabase Authentication
- Debugged Google OAuth callback issues
- Configured Railway environment variables
- Dockerized the application
- Connected Groq AI API
- Implemented OCR using Tesseract
- Built a responsive dashboard
- Fixed deployment and production issues

---

# 🚀 Future Improvements

- Browser Extension
- Android Application
- iOS Application
- Admin Dashboard
- Community Scam Reporting
- Multi-language Support
- AI Threat Intelligence
- Advanced ML Fraud Detection

---

# 👨‍💻 Author

**DS Yashaswi **

B.Tech Computer Science & Data Science

- AI
- Full Stack Development
- Data Science
- Cybersecurity

GitHub:

https://github.com/Yashr4635

LinkedIn:



---

# ⭐ Support

If you found this project interesting, consider giving it a ⭐ on GitHub.

Your support motivates future development.
