# 🚀 SalesIQ — AI Sales Intelligence Platform

<p align="center">
  <strong>Research Smarter • Understand Leads • Personalize Outreach 🎯</strong>
</p>

**SalesIQ** is an AI-powered sales intelligence platform that researches companies, identifies business insights and pain points, qualifies leads, and generates personalized sales outreach using AI.

---

## ✨ Features

* 🔍 **AI Company Research** — Analyze companies using website and user-provided information.
* 🧠 **Business Insights** — Identify goals, challenges, opportunities, and potential pain points.
* 🎯 **Lead Scoring** — Generate a lead qualification score from 1–100.
* 📧 **Sales Email Generator** — Create personalized cold emails and follow-ups.
* 💼 **LinkedIn Outreach** — Generate connection requests and direct messages.
* 🎤 **Sales Pitch Generator** — Create value propositions, pitches, and meeting requests.
* 💾 **Saved Reports & Leads** — Store and manage previous company analyses.
* 📊 **Modern Dashboard** — View reports, leads, generated content, and key statistics.

---

## 🤖 How It Works

```text
🏢 Enter Company Details
          ↓
🌐 Research Public Company Information
          ↓
🤖 Analyze with AI
          ↓
🧠 Identify Insights & Pain Points
          ↓
🎯 Generate Lead Score
          ↓
✉️ Create Personalized Outreach
```

SalesIQ can extract publicly available information from company websites and use **AI** to transform that information into structured sales intelligence.

> ⚠️ AI-generated insights may contain estimates. Important company information should always be verified before making business decisions.

---

## 🛠️ Tech Stack

### 🎨 Frontend

* HTML5
* CSS3
* JavaScript

### ⚙️ Backend

* Python
* Flask
* Flask-CORS

### 🤖 AI

* Groq API

### 🌐 Research

* Requests
* BeautifulSoup / Trafilatura

### 🗄️ Database

* SQLite

---

## 📊 Dashboard

The SalesIQ dashboard includes:

* 🏢 Companies Analyzed
* 🎯 Saved Leads
* ✉️ Messages Generated
* 📈 Lead Scores
* 🔍 Company Research
* 🧠 AI Analysis
* ✍️ Content Generator
* 📁 Previous Reports

The interface follows a clean, responsive SaaS design inspired by modern platforms such as **Vercel, Stripe, and Linear**.

---

## ✉️ AI Content Generator

SalesIQ can generate:

* Cold Sales Emails
* Follow-Up Emails
* LinkedIn Connection Requests
* LinkedIn Messages
* Sales Pitches
* Discovery Call Openings
* Value Propositions
* Meeting Requests

Users can also select the **tone and length** of generated content.

---

## 📂 Project Structure

```text
SalesIQ/
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── database/
├── services/
│   ├── groq_service.py
│   ├── research_service.py
│   └── database_service.py
│
├── templates/
│   └── index.html
│
└── static/
    ├── css/
    ├── js/
    └── assets/
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd SalesIQ
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate it

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Groq API Setup

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=your_model_here
SECRET_KEY=your_secret_key_here
```

> 🔐 Never upload your `.env` file or API keys to GitHub.

---

## ▶️ Run the Project

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

🎉 SalesIQ should now be running locally.

---

## 🔐 Security

* API keys remain server-side
* `.env` is excluded from Git
* Website URLs and inputs are validated
* External requests use timeouts
* Private/login-protected pages are not intentionally accessed
* AI-generated information is clearly distinguished from verified information

---

## 🚀 Future Improvements

* 🔐 User Authentication
* ☁️ Cloud Database
* 📊 Advanced Analytics
* 💼 CRM Integration
* 📧 Gmail Integration
* 🔔 Lead Notifications
* 📄 PDF Reports
* 🌙 Dark Mode
* 🏢 Competitor Analysis
* 🎯 ICP Matching

---

## 👨‍💻 Developer

**Harshvardhan Kumar**

B.Tech Student | Information Technology

---

## ⭐ Support

If you like **SalesIQ**, consider giving the repository a ⭐!

<p align="center">
  <strong>SalesIQ 🚀</strong><br>
  Research Smarter • Personalize Faster • Sell Intelligently
</p>

<p align="center">
  Built with ❤️ using HTML • CSS • JavaScript • Python • Flask • AI
</p>

