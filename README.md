# Cash Clever Backend

Backend service for **Cash Clever**, a personal finance & expense tracking application.  
Built with **FastAPI**, supports OCR (scan receipts), Excel data ingestion, expense analysis, and report generation.

---

## 🚀 Features
- REST API for expense tracking
- WebSocket streaming for AI-like suggestions
- OCR support (EasyOCR / Tesseract) for scanned receipts
- Excel/CSV ingestion & export (via pandas, openpyxl)
- Rule-based expense analysis & recommendations
- Authentication (JWT / OAuth2)
- Database integration (PostgreSQL with SQLAlchemy)

---

## 🛠️ Tech Stack
- **Python 3.11+**
- **FastAPI** (API framework)
- **SQLAlchemy + Alembic** (ORM & migrations)
- **PostgreSQL** (database, dev = SQLite optional)
- **pandas + openpyxl** (data processing & Excel)
- **EasyOCR / Tesseract** (OCR engine)
- **Docker + Docker Compose** (deployment)
- **Pytest** (testing)

---

## 📂 Project Structure

smart-spend-backend/
│── app/
│ ├── api/ # API routes
│ ├── core/ # config, auth, settings
│ ├── models/ # SQLAlchemy models
│ ├── services/ # business logic (OCR, Excel, analysis)
│ └── main.py # FastAPI entry point
│
│── tests/ # unit & integration tests
│── migrations/ # alembic migrations
│── requirements.txt # dependencies
│── Dockerfile
│── docker-compose.yml
│── README.md

---

## ⚡ Getting Started

1️ Clone repo

git clone https://github.com/your-username/smart-spend-backend.git
cd smart-spend-backend

2️⃣ Setup environment

Create .env file:

DATABASE_URL=postgresql+psycopg2://user:password@db:5432/smartspend
SECRET_KEY=your-secret-key

3️⃣ Run with Docker
docker-compose up --build

Backend will be available at:
👉 http://localhost:8000/docs (Swagger UI)

4️⃣ Run tests
pytest

📌 API Docs

Swagger UI → /docs

📅 Roadmap

 Authentication (JWT)

 Receipt OCR (EasyOCR)

 Excel import/export

 Expense categorization & analysis

 AI-based spending suggestions

 Deployment (Render/AWS/DigitalOcean)

 📝 License

MIT License © 2025 Cash Clever
