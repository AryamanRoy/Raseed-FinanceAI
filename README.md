# 💰 Raseed-FinanceAI  
**Your intelligent AI-powered personal finance assistant**

---

## 🎯 Overview  
**Raseed-FinanceAI** is an AI-driven personal finance management tool that helps users track expenses, analyse spending patterns, and receive personalised financial insights.  
Powered by **machine learning** and **generative AI**, it transforms raw transaction data into actionable advice — enabling smarter budgeting and saving decisions.

---

## 🚀 Features  
- 📊 **Automated Expense Tracking** – Upload CSVs and get instant categorisation.  
- 🤖 **AI Chat Assistant** – Ask natural questions like “Where did I spend the most last month?” or “How can I reduce my food expenses?”  
- 💡 **Personalised Insights** – Get savings recommendations and goal-based tips.  
- 📈 **Visual Analytics** – Charts and trend summaries for quick decision-making.  
- 🔒 **Secure & Private** – All data is processed locally with safe API integration.  

---

## 🧰 Tech Stack  

| Layer | Technology |
|-------|-------------|
| **Frontend** | React + TypeScript + TailwindCSS / MUI |
| **Backend** | FastAPI (Python) |
| **AI Engine** | Google Generative AI (Gemini) |
| **Data Handling** | Pandas, NumPy |
| **Deployment** | Vercel / Render / Railway (optional) |

---

## ⚙️ Installation & Setup  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/AryamanRoy/Raseed-FinanceAI.git
cd Raseed-FinanceAI
```

### 2️⃣ Backend Setup  
```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### 3️⃣ Frontend Setup  
```bash
cd frontend
npm install
npm run dev
```

### 4️⃣ Environment Variables  
Create a `.env` file in your backend directory:
```
GOOGLE_API_KEY=your_google_api_key_here
```

---

## 🧠 Usage  
1. Run the backend (`FastAPI`) and frontend (`React`) servers.  
2. Open the web interface (usually `http://localhost:5173/`).  
3. Upload your transaction CSV file.  
4. Explore detailed insights, AI summaries, and interactive visual charts.  
5. Chat with the AI for personalised budgeting tips.  

---

## 🗺️ Roadmap  
- [ ] Multi-account integration (bank + credit card APIs)  
- [ ] Predictive budgeting using AI forecasting  
- [ ] Expense anomaly detection  
- [ ] Mobile-responsive UI / PWA support  

---

## 🤝 Contributing  
Contributions are always welcome!  
To contribute:  
1. Fork this repository  
2. Create a new branch (`feature/your-feature-name`)  
3. Commit and push your changes  
4. Open a Pull Request  

---

## 🪪 License  
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 💬 Acknowledgements  
Special thanks to the open-source community and the Gemini AI API for enabling intelligent financial analysis.  

---

### ⭐ If you find this project useful, consider giving it a star on GitHub!
