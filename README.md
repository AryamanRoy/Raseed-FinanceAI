# 💼 Raseed-FinanceAI

**Raseed-FinanceAI** is an intelligent financial assistant that categorizes expenses from bank statements and provides personalized insights using Google Gemini AI.

---

## 🚀 Features
- **Upload CSV**: Automatically categorizes your transactions.
- **AI Chat**: Ask personalized financial questions powered by Gemini.
- **Expense Insights**: Summaries, savings tips, and trend analysis.
- **Frontend**: React + TypeScript + Material UI.
- **Backend**: FastAPI + Google Generative AI SDK.

---

## 🧠 Tech Stack
| Layer | Tech |
|--------|------|
| Frontend | React + TypeScript + Vite |
| Backend | FastAPI (Python) |
| AI | Gemini 1.5 Pro |
| Styling | Tailwind / MUI |
| Data | Pandas |
| Environment | .env (GOOGLE_API_KEY) |

---

## 🧩 Setup

### 1️⃣ Backend
```bash
cd Raseed-FinanceAI
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
