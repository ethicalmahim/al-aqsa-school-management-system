<div align="center">

# 🏫 Al-Aqsa School Management System

**A complete, multi-branch school management platform built with Flask: attendance, results, accounts, lessons, videos and notices, with a separate portal for each role.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![pandas](https://img.shields.io/badge/pandas-Excel%20Import-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)

[Features](#-features) •
[Roles](#-who-uses-it) •
[Tech Stack](#-tech-stack) •
[Getting Started](#-getting-started) •
[Configuration](#%EF%B8%8F-configuration) •
[Project Structure](#-project-structure)

</div>

---

## ✨ Overview

**Al-Aqsa School Management System** is a real-world web application built for a coaching/school network with **multiple branches**. It replaces paper registers and scattered spreadsheets with one place where admins, office staff, teachers and students each get their own dashboard and see only what they're allowed to see.

Staff keep working in **Excel** the way they're used to: attendance, results, accounts, curriculum and video lists are uploaded as `.xlsx` files and turned into searchable records. Legacy **Bijoy-encoded Bangla text** is automatically converted to Unicode on import.

---

## 🚀 Features

<table>
<tr>
<td width="50%" valign="top">

### 📋 Academics
- **Attendance**: upload and search by year, class and student; students see their own record
- **Results**: semester and class assessments with per-period history
- **Lesson schedule**: date-based lesson plans per class
- **Syllabus**: upload PDFs per class; students only get their own class's file

</td>
<td width="50%" valign="top">

### 💰 Accounts
- **Student accounts**: fee records students can check from their portal
- **Internal accounts**: income, expense, datasheet and **balance sheet**
- Bulk import straight from Excel files

</td>
</tr>
<tr>
<td valign="top">

### 🎥 Learning Content
- **Protected video lessons**: YouTube videos served through short-lived signed tokens, tied to the logged-in user, with a personal watermark
- **QR codes and a QR scanner** for quick access to tutorials
- Paste any YouTube link format (`youtu.be`, `shorts`, `watch?v=`, `live`…)

</td>
<td valign="top">

### 🛠️ Administration
- **Multi-branch** management with per-branch staff and data
- **User management** for Service Admins, Teachers and Students
- **Fine-grained permissions**: turn individual modules on or off for each Service Admin
- **Notice board** with images, **comments/feedback** with replies
- **Call services** directory with one-tap WhatsApp links
- **Activity log** of what happened and who did it

</td>
</tr>
</table>

🎨 **Kid-friendly UI**: a bright, playful, responsive theme that works on phones, tablets and desktops.

---

## 👥 Who Uses It

| Role | What they can do |
|------|------------------|
| 🛡️ **Admin** | Everything: branches, all users, permissions, logs, accounts, notices, comments |
| 🧑‍💼 **Service Admin** | Branch office staff: register students and manage the modules the Admin has enabled for them (attendance, results, accounts, notices, comments) |
| 👩‍🏫 **Teacher** | Lesson schedules, syllabus, attendance and results |
| 🎒 **Student / Guardian** | Their own attendance, results, fees, syllabus, schedule and video lessons, and sending feedback |

Every route is protected by a `@roles_required(...)` decorator, and logged-in users land on the dashboard for their role.

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, **Flask**, Flask-Login |
| Database | **SQLAlchemy 2.0** (typed `Mapped` models), SQLite by default, any SQLAlchemy URL supported |
| Data import | **pandas** + **openpyxl** for Excel uploads, `bijoy2unicode` for Bangla text |
| Security | Werkzeug password hashing, signed time-limited video tokens (`itsdangerous`), role-based access |
| Frontend | Jinja2 templates, **Bootstrap 5.3**, Bootstrap Icons, vanilla JavaScript |

---

## ⚡ Getting Started

### Prerequisites
- Python **3.10+**
- `pip` and (recommended) a virtual environment

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/mahim02580/al-aqsa-school-management-system.git
cd al-aqsa-school-management-system

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file (see Configuration below)

# 5. Run it
python app.py
```

Open **http://localhost:5000** and sign in with the admin account from your `.env`.

> 💡 On first run the app creates the database, the first branch and the first **Admin** user automatically. If `ADMIN_PASSWORD` is empty, a random password is printed in the console.

### Forgot the admin password?

```bash
flask --app app reset-admin-password              # prompts for a new password
flask --app app reset-admin-password --generate   # prints a random one
flask --app app reset-admin-password --username <name>   # when there are several admins
```

---

## ⚙️ Configuration

Create a `.env` file in the project root. It is git-ignored, so never commit it.

```env
# Required for production: a long random string
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=

# Database (default: sqlite:///school.db inside instance/)
DB_URI=

# First run only: used to create the first Admin and branch
ADMIN_USERNAME=
ADMIN_PASSWORD=
ADMIN_SCHOOL_ID=
INITIAL_BRANCH_NAME=
INITIAL_BRANCH_CODE=
INITIAL_BRANCH_DIRECTOR=
INITIAL_BRANCH_PHONE=

# Server
FLASK_DEBUG=false
HOST=0.0.0.0
PORT=5000
```

---

## 📁 Project Structure

```text
al-aqsa-school-management-system/
├── app.py              # Flask app: models, routes, APIs, CLI commands
├── decorators.py       # @roles_required access control
├── helpers.py          # Role redirects, Bijoy→Unicode, YouTube link parsing
├── requirements.txt
├── static/
│   ├── css/            # main.css + kids.css theme
│   ├── js/             # shared scripts
│   └── img/            # logo, uploaded notices and syllabus PDFs
└── templates/
    ├── admin/          # Admin-only pages
    ├── service_admin/  # Branch office pages
    ├── teacher/        # Teacher dashboard
    ├── student/        # Student portal
    └── *.html          # Shared pages (attendance, results, accounts…)
```

---

## 🗺️ Roadmap

- [ ] Screenshots and a live demo
- [ ] SMS/WhatsApp notifications for guardians
- [ ] Downloadable PDF report cards
- [ ] Dedicated video hosting (Bunny Stream / Cloudflare Stream)

---

## 🤝 Contributing

Issues and pull requests are welcome. If you have an idea or found a bug:

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-idea`
3. Commit your changes and open a Pull Request

---

## 🧑‍💻 Author

<div align="center">

Built by **[@ethicalmahim](https://github.com/ethicalmahim)**

If this project helped or inspired you, please consider giving it a ⭐. It really helps!

</div>
