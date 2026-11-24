<div align="center">

# 🏫 Al-Aqsa School Management System

**A complete, multi-branch school management platform built with Flask: attendance, results, accounts, lessons, videos and notices, with a separate portal for each role.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![pandas](https://img.shields.io/badge/pandas-Excel%20Import-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)

[Live Demo](#-live-demo) •
[Features](#-features) •
[Screenshots](#-screenshots) •
[Roles](#-who-uses-it) •
[Tech Stack](#-tech-stack) •
[Getting Started](#-getting-started) •
[Configuration](#%EF%B8%8F-configuration) •
[Project Structure](#-project-structure)

</div>

---

## 🌐 Live Demo

**👉 [Open the demo](https://your-demo-url.com)**

Sign in with any of these accounts. Every account uses the password **`123456`**.

| Role | Username | What you'll see |
|------|----------|-----------------|
| 🛡️ Admin | `admin` | Everything: all branches, users, accounts, results, logs |
| 🧑‍💼 Service Admin | `office.mirpur` | Mirpur branch office with all modules enabled |
| 🧑‍💼 Service Admin | `office.uttara` | Uttara branch office with **Accounts turned off** (permissions demo) |
| 👩‍🏫 Teacher | `teacher.ruma` | Lesson schedule, syllabus, attendance and results |
| 🎒 Student | `ayaan` | A Class One student's attendance, results, fees and lessons |

> All names and records are fictional, and the demo data resets regularly, so feel free to click around and change things.

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

## 📸 Screenshots

> All names, numbers and records shown are demo data.

<table>
<tr>
<td width="50%"><img src="docs/screenshots/01-login-en.png" alt="Login"><p align="center"><b>Login</b> (English / বাংলা)</p></td>
<td width="50%"><img src="docs/screenshots/02-admin-dashboard.png" alt="Admin dashboard"><p align="center"><b>Admin dashboard</b></p></td>
</tr>
<tr>
<td><img src="docs/screenshots/07-attendance.png" alt="Attendance"><p align="center"><b>Attendance</b>: monthly register per class</p></td>
<td><img src="docs/screenshots/09-semester-result.png" alt="Semester results"><p align="center"><b>Semester results</b> with merit position</p></td>
</tr>
<tr>
<td><img src="docs/screenshots/08-student-accounts-admin.png" alt="Student accounts"><p align="center"><b>Student fees</b>: paid months and dues</p></td>
<td><img src="docs/screenshots/15-datasheet.png" alt="Data sheet"><p align="center"><b>Data sheet</b>: daily income and expense</p></td>
</tr>
<tr>
<td><img src="docs/screenshots/16-balance-sheet.png" alt="Balance sheet"><p align="center"><b>Balance sheet</b>: running balance per branch</p></td>
<td><img src="docs/screenshots/06-student-registration.png" alt="Student registration"><p align="center"><b>Student registration</b> with admin approval</p></td>
</tr>
</table>

### 🎒 Student portal and 📱 mobile

<table>
<tr>
<td width="33%"><img src="docs/screenshots/28-mobile-student-dashboard.png" alt="Student dashboard on mobile"><p align="center"><b>Student dashboard</b></p></td>
<td width="33%"><img src="docs/screenshots/29-mobile-student-attendance.png" alt="Student attendance on mobile"><p align="center"><b>My attendance</b></p></td>
<td width="33%"><img src="docs/screenshots/30-mobile-admin-dashboard.png" alt="Admin dashboard on mobile"><p align="center"><b>Admin on the go</b></p></td>
</tr>
</table>

<details>
<summary><b>More screenshots</b> (click to expand)</summary>
<br>

| | |
|---|---|
| ![Login in Bangla](docs/screenshots/01-login-bn.png)<br>**Login in Bangla** | ![Branch management](docs/screenshots/03-branch-management.png)<br>**Branch management** |
| ![User management](docs/screenshots/04-user-management.png)<br>**User management** | ![Student users](docs/screenshots/05-student-users.png)<br>**Student accounts list** |
| ![Class assessment](docs/screenshots/10-class-assessment.png)<br>**Class assessment** | ![Lesson schedule](docs/screenshots/11-lesson-schedule.png)<br>**Lesson schedule** |
| ![Internal accounts](docs/screenshots/12-internal-accounts.png)<br>**Internal accounts** | ![Income](docs/screenshots/13-income.png)<br>**Fee collection** |
| ![Expense](docs/screenshots/14-expense.png)<br>**Expenses and staff salary** | ![Activity log](docs/screenshots/17-activity-log.png)<br>**Login activity log** |
| ![Comments](docs/screenshots/18-feedback-comments.png)<br>**Guardian feedback and replies** | ![Call services](docs/screenshots/19-call-services.png)<br>**Call services with WhatsApp** |
| ![QR tutorials](docs/screenshots/20-qr-tutorials.png)<br>**QR code management** | ![Teacher dashboard](docs/screenshots/22-teacher-dashboard.png)<br>**Teacher dashboard** |
| ![Student dashboard](docs/screenshots/23-student-dashboard.png)<br>**Student dashboard** | ![Student attendance](docs/screenshots/24-student-attendance.png)<br>**Student attendance report** |
| ![Student result](docs/screenshots/25-student-result.png)<br>**Student progress report** | ![Student fees](docs/screenshots/26-student-fees.png)<br>**Student fee card** |
| ![Student lessons](docs/screenshots/27-student-lessons.png)<br>**Student lesson schedule** | |

</details>

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
git clone https://github.com/ethicalmahim/al-aqsa-school-management-system.git
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
