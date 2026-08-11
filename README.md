# Monika G Cafe Management System

A robust, full-stack **Cafe Management System API** built with **FastAPI**, **SQLAlchemy**, and **MySQL**. Designed to streamline day-to-day cafe operations including orders, inventory, billing, table reservations, staff management, and business reporting.

---

## 🚀 Features

- 🔑 **Authentication & Authorization**: Secure JWT token authentication with role-based access control and bcrypt password hashing.
- 📜 **Menu Management**: Add, update, view, and organize cafe food and beverage items with pricing and categories.
- 🛒 **Order Processing**: Real-time order creation, item customization, and status updates (Pending, Preparing, Completed, Cancelled).
- 💳 **Billing & Invoicing**: Automated bill calculations, discount applications, receipt generation, and payment tracking.
- 📦 **Inventory Control**: Track raw ingredients, stock levels, reorder alerts, and supplier information.
- 👨‍🍳 **Staff & Employee Management**: Manage employee records, roles, shifts, and contact information.
- 🧑‍🤝‍🧑 **Customer Management**: Maintain customer records, order history, and loyalty tracking.
- 📅 **Table Reservations**: Book, confirm, and update table availability for customers.
- 💬 **Feedback & Reviews**: Collect ratings and reviews to monitor guest satisfaction.
- 📊 **Reports & Analytics**: Generate sales summaries, daily revenue stats, and inventory consumption reports.

---

## 🛠️ Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **Database ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Database Engine**: MySQL / MariaDB (via `PyMySQL`)
- **Security & Auth**: `python-jose` (JWT), `passlib` (bcrypt), `python-multipart`
- **Data Validation**: Pydantic v2 / `pydantic-settings`
- **Deployment Ready**: Configured for deployment on [Railway](https://railway.app/) (`railway.toml`)

---

## 📁 Repository Structure

```text
monika_g_cafe/
├── backend/
│   ├── main.py              # Application entry point & route definitions
│   ├── config.py            # Environment configuration settings
│   ├── database.py          # Database connection setup & ORM session
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic models for request/response validation
│   ├── requirements.txt     # Python dependencies
│   ├── railway.toml         # Railway deployment configuration
│   ├── routers/             # API endpoint handlers
│   │   ├── auth.py          # Login & registration endpoints
│   │   ├── menu.py          # Menu items CRUD
│   │   ├── orders.py        # Order creation & tracking
│   │   ├── billing.py       # Payment & invoicing
│   │   ├── inventory.py     # Stock & ingredient management
│   │   ├── employees.py     # Staff directory
│   │   ├── customer.py      # Customer profile management
│   │   ├── reservation.py   # Table reservation management
│   │   ├── feedback.py      # Customer ratings & reviews
│   │   └── reports.py       # Sales & analytics reports
│   └── frontend/            # Static Web UI files
├── monika g cafe.sql        # Database schema export file
├── railway.toml             # Root deployment config
└── README.md                # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites

Make sure you have installed:
- **Python 3.10+**
- **MySQL / MariaDB Database Server**

### 2. Clone the Repository

```bash
git clone https://github.com/Gangula007415/Monika-g-cafe.git
cd Monika-g-cafe
```

### 3. Create a Virtual Environment & Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 4. Database Setup

1. Create a MySQL database named `monika_g_cafe` (or preferred name).
2. Import the provided schema:
   ```bash
   mysql -u root -p monika_g_cafe < "monika g cafe.sql"
   ```

### 5. Environment Variables Setup

Create a `.env` file inside the `backend/` directory with the following variables:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/monika_g_cafe
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🏃 Running the Application

Start the FastAPI development server:

```bash
uvicorn backend.main:app --reload
```

The server will launch at `http://127.0.0.1:8000`.

### 📖 Interactive API Documentation

Once the app is running, access the automatic interactive docs:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🚀 Deployment

The project includes `railway.toml` configurations for quick 1-click deployment on [Railway](https://railway.app/). Ensure environment variables (`DATABASE_URL`, `SECRET_KEY`, etc.) are configured in your deployment platform dashboard.

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
