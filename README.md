
# 🤖 FlaskAssist: Intelligent AI Chatbot

[![Live Demo](https://img.shields.io/badge/Live_Demo-Available-success?style=for-the-badge&logo=python)](https://flaskassist.pythonanywhere.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)]()
[![Flask](https://img.shields.io/badge/Flask-Web_Framework-black?style=for-the-badge&logo=flask&logoColor=white)]()
[![Cohere](https://img.shields.io/badge/Cohere-Command_API-purple?style=for-the-badge)]()

A full-stack, production-ready AI Chatbot application built with Flask, Bootstrap 5, and the Cohere LLM API. 

This project goes beyond a simple API wrapper by implementing a complete SaaS-style architecture, including secure user authentication, persistent chat history via relational databases, and a cookie-based freemium trial system for guest users.

---

## 🚀 Live Demo
**Try the application here:** [FlaskAssist Live](https://flaskassist.pythonanywhere.com/)

---

## ✨ Core Features

*   **Freemium Trial Logic:** Unauthenticated users can interact with the AI for up to 5 prompts. This state is securely tracked using browser cookies without bloating the database with guest data.
*   **Secure Authentication:** Full registration and login system utilizing `Flask-Login` and `Werkzeug.security` (PBKDF2 SHA-256 password hashing).
*   **Persistent Chat History:** Logged-in users have their conversations securely saved to a backend database, organized by distinct chat sessions.
*   **Full-Text Search:** Users can easily search through their historical chat data using a custom SQLAlchemy `.ilike()` query implementation.
*   **Markdown Parsing:** The AI's markdown responses (bolding, lists, code blocks) are dynamically parsed and rendered into beautiful, formatted HTML on the frontend.
*   **Context-Aware AI:** The backend automatically retrieves the previous messages of an active session and formats them into a context payload for the Cohere API, allowing the AI to "remember" the ongoing conversation.

---

## 🛠️ Technical Stack

*   **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
*   **Database:** SQLite (Relational mapping for Users, Sessions, and Messages)
*   **Frontend:** HTML5, CSS3, Bootstrap 5 (Responsive UI, Dismissible Alerts, Hover States)
*   **AI Integration:** Cohere API (`command-a-03-2025` model)
*   **Environment Management:** `python-decouple`
*   **Deployment:** PythonAnywhere

---

## 🗄️ Database Architecture

The backend utilizes a three-tier relational hierarchy to ensure data integrity and efficient querying:

1.  **User Table:** Manages authentication. (1-to-Many relationship with ChatSessions).
2.  **ChatSession Table:** Groups messages into distinct conversations. Configured with `cascade="all, delete-orphan"` to automatically clean up orphaned messages if a session is deleted.
3.  **Message Table:** Stores individual prompts and AI responses with timestamp metadata and role-designations (`USER` or `CHATBOT`).

---

## 💻 Local Setup & Installation

To run this project locally, follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/shumaim-fayyaz/flask-ai-assistant.git](https://github.com/shumaim-fayyaz/flask-ai-assistant.git)
cd flask-ai-assistant
```

**2. Set up a virtual environment**

**Bash**

```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

**3. Install dependencies**

**Bash**

```
pip install -r requirements.txt
```

**4. Configure Environment Variables**

Create a `.env` file in the root directory and add the following:

**Code snippet**

```
SECRET_KEY=your_secure_random_string
DATABASE_URL=sqlite:///db.sqlite3
COHERE_API_KEY=your_cohere_production_key_here
```

**5. Run the application**

**Bash**

```
python app.py
```

*The application will generate the local SQLite database on its first run and will be accessible at `http://127.0.0.1:5000`.*
