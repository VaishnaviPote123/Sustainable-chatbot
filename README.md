# 🌱 Eco Lifestyle Coach Chatbot

An interactive AI-powered chatbot that helps users live more sustainably with daily challenges, carbon tracking, gamification, and habit reminders.

## ✨ Features

### 💬 **Chat with Eco Coach**
- Get personalized sustainability advice from an AI coach powered by Groq LLM
- Real-time responses with RAG (Retrieval-Augmented Generation) using knowledge base
- Auto-detect eco-friendly activities and award carbon points

### 🎯 **Daily Eco-Friendly Challenges**
- **Same challenge for ALL users each day** (ensures community engagement)
- 5 challenge categories: Transport, Nature, Diet, Water, Waste
- Carbon points reward for completing challenges
- Challenge rotates daily

### 📊 **Carbon Savings Tracker**
- Track your total CO2 saved (kg)
- Log custom eco activities with carbon values
- View your sustainability journey and progress
- Real-time statistics

### 🏆 **Leaderboard & Gamification**
- Compete with other eco warriors
- Ranked by total carbon saved
- Real-time leaderboard updates
- Encourage friendly competition for sustainability

### 🔔 **Habit Reminders**
- Create custom habit reminders (drink water, take a walk, etc.)
- Set frequency (daily, weekly, hourly)
- Enable/disable reminders anytime
- Never miss your eco habits

## 🏗️ Architecture

### Frontend
- **Location:** `frontend/index.html`
- **Tech:** Vanilla JavaScript, HTML5, CSS3
- **Features:** 5-tab interface (Chat, Challenge, Tracker, Reminders, Leaderboard)

### Backend
- **Location:** `backend/`
- **Framework:** FastAPI (Python)
- **LLM:** Groq (llama-3.1-8b-instant)
- **RAG:** LangChain + Chroma Vector DB
- **Database:** SQLite

### Key Files
- `app.py` - FastAPI routes and endpoints
- `rag.py` - RAG system with LangChain
- `database.py` - SQLite database management
- `chatbot.py` - Chatbot logic (extensible)
- `models.py` - Data models

## 📋 Setup Instructions

### 1. Prerequisites
- Python 3.8+
- pip

### 2. Install Dependencies
```bash
cd backend
pip install fastapi uvicorn pydantic groq langchain langchain-community \
  langchain-text-splitters langchain-huggingface chromadb sentence-transformers
```

### 3. Set Groq API Key
```powershell
# Windows PowerShell
$env:GROQ_API_KEY = "your-groq-api-key"
```

Get your free API key from: https://console.groq.com

### 4. Start Backend Server
```bash
cd backend
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Server will run on: `http://127.0.0.1:8000`

### 5. Open Frontend
Open `frontend/index.html` in your browser

## 🎮 How to Use

### Chat Tab 💬
1. Enter your name (optional)
2. Ask the eco coach any sustainability question
3. Get personalized advice backed by knowledge base
4. See auto-calculated carbon savings

### Challenge Tab 🎯
1. Click "Load Today's Challenge"
2. See the challenge shared by all users today
3. Complete the challenge
4. Log it to earn carbon points

### Tracker Tab 📊
1. Enter your username
2. Click "Load Stats" to see your progress
3. Log new activities manually
4. Track total carbon saved and current streak

### Reminders Tab 🔔
1. Create habit reminders (e.g., "Drink water daily")
2. Set frequency (daily, weekly, hourly)
3. Load reminders anytime
4. Modify or delete reminders

### Leaderboard Tab 🏆
1. See top eco warriors
2. Check how much carbon they've saved
3. Compete with others
4. Refresh to see real-time updates

## 📊 Database Schema

### Users Table
- id, username, email, total_carbon_saved, streak, last_challenge_date

### Carbon Log
- id, user_id, carbon_saved, activity, logged_at

### Reminders
- id, user_id, habit, frequency, enabled, last_reminded

### Challenge of Day
- id, date, challenge_id (ensures same challenge for all users)

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Chat with eco coach |
| GET | `/challenge/daily` | Get today's challenge (same for all) |
| POST | `/carbon/log` | Log carbon saved |
| GET | `/leaderboard` | Get top 10 users |
| GET | `/user/{username}` | Get user stats |
| POST | `/reminder/add` | Add new reminder |
| GET | `/reminders/{username}` | Get user's reminders |

## 🚀 Future Enhancements

- [ ] Email/SMS notifications for reminders
- [ ] Social sharing of achievements
- [ ] Community challenges
- [ ] Mobile app version
- [ ] Integration with real carbon tracking APIs
- [ ] Advanced analytics dashboard
- [ ] Badge/achievement system
- [ ] Carbon offset marketplace

## 📝 Knowledge Base

Add sustainability content to `backend/data/sustainability.txt` (or `docs/sustainability.txt`)

Example content:
```
- Using public transport saves 2.4kg CO2 per km vs driving
- Eating plant-based meals saves 0.5-1kg CO2 per meal
- Planting trees: one tree saves ~20kg CO2 per year
- LED bulbs use 75% less energy than incandescent
```

## 🔧 Configuration

### Change LLM Model
Edit `app.py`:
```python
model="llama-3.1-8b-instant"  # Change to other Groq models
```

### Adjust Challenge List
Edit `DAILY_CHALLENGES` in `app.py`

### Change Database Path
Edit `database.py`:
```python
DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - Feel free to use this project for educational or commercial purposes.

## 🌍 Environmental Impact

Every feature in this chatbot is designed to help users:
- Learn about sustainability
- Track their environmental impact
- Build sustainable habits
- Compete positively with others
- Make informed eco-friendly choices

Together, we can build a more sustainable future! 🌱

## 📧 Support

For questions or issues, please create an issue in the repository.

---

Made with 💚 for a sustainable planet.
