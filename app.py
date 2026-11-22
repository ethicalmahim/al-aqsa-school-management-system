import re
import math
import os
import json
from urllib.parse import unquote, urlparse

import click

from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify, send_from_directory
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Date, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import roles_required
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import pandas as pd
from datetime import date, timedelta, datetime
import helpers
from zoneinfo import ZoneInfo

load_dotenv()

ADMIN_ROLE = "Admin"
SERVICE_ADMIN_ROLE = "Service Admin"
TEACHER_ROLE = "Teacher"
STUDENT_ROLE = "Student"

CLASS_MAP = {
    1: "Play",
    2: "Nursery",
    3: "One",
    4: "Two",
    5: "Three",
    6: "Four",
    7: "Five",
}


class Base(DeclarativeBase):
    pass


def env_flag(name, default=False):
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in ("1", "true", "yes", "on")


app = Flask(__name__)

# Settings come from .env (see .env.example); every one has a safe fallback so the app starts anyway
_secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    import secrets
    _secret_key = secrets.token_hex(32)
    print("WARNING: SECRET_KEY is not set in .env; using a temporary key, so logins reset on every restart.")
app.config['SECRET_KEY'] = _secret_key
# Relative sqlite paths such as sqlite:///school.db are created inside the instance/ folder
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI") or "sqlite:///school.db"

# Folders that uploaded files are saved into
NOTICES_DIR = os.path.join(app.root_path, "static", "img", "notices")
SYLLABUS_DIR = os.path.join(app.root_path, "static", "img", "syllabus")

db = SQLAlchemy(app, model_class=Base)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# DB Models-------------------------------------------------------------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)  # Admin, Teacher, Guardian
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    branch = relationship("Branch", back_populates="user")
    is_active: Mapped[bool] = mapped_column(default=True)
    has_lesson_schedule_option_access: Mapped[bool] = mapped_column(default=True)
    has_attendance_option_access: Mapped[bool] = mapped_column(default=True)
    has_accounts_option_access: Mapped[bool] = mapped_column(default=True)
    has_results_option_access: Mapped[bool] = mapped_column(default=True)
    has_qr_code_access: Mapped[bool] = mapped_column(default=True)
    has_comment_access: Mapped[bool] = mapped_column(default=True)
    has_notice_access: Mapped[bool] = mapped_column(default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Branch(db.Model):
    __tablename__ = "branches"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    director: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    user = relationship("User", back_populates="branch")


class Curriculum(db.Model):
    __tablename__ = "curriculum"
    id: Mapped[int] = mapped_column(primary_key=True)
    class_name: Mapped[str] = mapped_column()
    subject_name: Mapped[str] = mapped_column()
    date: Mapped[date] = mapped_column(Date)
    topic: Mapped[str] = mapped_column()


class Video(db.Model):
    __tablename__ = "videos"
    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(nullable=False)
    class_name: Mapped[str] = mapped_column()


class AttendanceRecord(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column()
    class_name: Mapped[str] = mapped_column()
    month: Mapped[str] = mapped_column()
    student_id: Mapped[int] = mapped_column()
    student_name: Mapped[str] = mapped_column()
    d1: Mapped[str] = mapped_column(nullable=True)
    d2: Mapped[str] = mapped_column(nullable=True)
    d3: Mapped[str] = mapped_column(nullable=True)
    d4: Mapped[str] = mapped_column(nullable=True)
    d5: Mapped[str] = mapped_column(nullable=True)
    d6: Mapped[str] = mapped_column(nullable=True)
    d7: Mapped[str] = mapped_column(nullable=True)
    d8: Mapped[str] = mapped_column(nullable=True)
    d9: Mapped[str] = mapped_column(nullable=True)
    d10: Mapped[str] = mapped_column(nullable=True)
    d11: Mapped[str] = mapped_column(nullable=True)
    d12: Mapped[str] = mapped_column(nullable=True)
    d13: Mapped[str] = mapped_column(nullable=True)
    d14: Mapped[str] = mapped_column(nullable=True)
    d15: Mapped[str] = mapped_column(nullable=True)
    d16: Mapped[str] = mapped_column(nullable=True)
    d17: Mapped[str] = mapped_column(nullable=True)
    d18: Mapped[str] = mapped_column(nullable=True)
    d19: Mapped[str] = mapped_column(nullable=True)
    d20: Mapped[str] = mapped_column(nullable=True)
    d21: Mapped[str] = mapped_column(nullable=True)
    d22: Mapped[str] = mapped_column(nullable=True)
    d23: Mapped[str] = mapped_column(nullable=True)
    d24: Mapped[str] = mapped_column(nullable=True)
    d25: Mapped[str] = mapped_column(nullable=True)
    d26: Mapped[str] = mapped_column(nullable=True)
    d27: Mapped[str] = mapped_column(nullable=True)
    d28: Mapped[str] = mapped_column(nullable=True)
    d29: Mapped[str] = mapped_column(nullable=True)
    d30: Mapped[str] = mapped_column(nullable=True)
    d31: Mapped[str] = mapped_column(nullable=True)


class AccountsRecord(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column()
    class_name: Mapped[str] = mapped_column()
    student_id: Mapped[int] = mapped_column()
    student_name: Mapped[str] = mapped_column()
    january: Mapped[float] = mapped_column(nullable=True)
    february: Mapped[float] = mapped_column(nullable=True)
    march: Mapped[float] = mapped_column(nullable=True)
    april: Mapped[float] = mapped_column(nullable=True)
    may: Mapped[float] = mapped_column(nullable=True)
    june: Mapped[float] = mapped_column(nullable=True)
    july: Mapped[float] = mapped_column(nullable=True)
    august: Mapped[float] = mapped_column(nullable=True)
    september: Mapped[float] = mapped_column(nullable=True)
    october: Mapped[float] = mapped_column(nullable=True)
    november: Mapped[float] = mapped_column(nullable=True)
    december: Mapped[float] = mapped_column(nullable=True)
    due: Mapped[float] = mapped_column(nullable=True)
    # No longer set by the income page (checkboxes no longer add month fees); kept so cancelling an
    # older payment can restore it.
    due_month: Mapped[int] = mapped_column(nullable=True)
    # Miscellaneous-income due (admission, books, ...), kept apart from `due`, which is the monthly
    # fee due only (negative = advance). Not part of the Excel upload; an upload keeps it.
    misc_due: Mapped[float] = mapped_column(nullable=True)


class SemesterResultRecord(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column(nullable=False)
    class_name: Mapped[str] = mapped_column(nullable=False)
    exam_name: Mapped[str] = mapped_column(nullable=False)
    student_id: Mapped[int] = mapped_column(nullable=False)
    student_name: Mapped[str] = mapped_column(nullable=True)
    merit: Mapped[int] = mapped_column(nullable=True)
    arabic: Mapped[float] = mapped_column(nullable=True)
    quran: Mapped[float] = mapped_column(nullable=True)
    bengali: Mapped[float] = mapped_column(nullable=True)
    english: Mapped[float] = mapped_column(nullable=True)
    math: Mapped[float] = mapped_column(nullable=True)
    science: Mapped[float] = mapped_column(nullable=True)
    bgs: Mapped[float] = mapped_column(nullable=True)
    aqaid_and_fiqh: Mapped[float] = mapped_column(nullable=True)
    class_test: Mapped[float] = mapped_column(nullable=True)
    presence: Mapped[float] = mapped_column(nullable=True)
    total: Mapped[float] = mapped_column(nullable=True)
    letter_grade: Mapped[str] = mapped_column(nullable=True)


class ClassTestResultRecord(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column(nullable=False)
    class_name: Mapped[str] = mapped_column(nullable=False)
    month: Mapped[str] = mapped_column(nullable=False)
    student_id: Mapped[int] = mapped_column(nullable=False)
    student_name: Mapped[str] = mapped_column()
    arabic: Mapped[float] = mapped_column(nullable=True)
    quran: Mapped[float] = mapped_column(nullable=True)
    bengali: Mapped[float] = mapped_column(nullable=True)
    english: Mapped[float] = mapped_column(nullable=True)
    math: Mapped[float] = mapped_column(nullable=True)
    science: Mapped[float] = mapped_column(nullable=True)
    aqaid_and_fiqh: Mapped[float] = mapped_column(nullable=True)
    bgs: Mapped[float] = mapped_column(nullable=True)
    total: Mapped[float] = mapped_column(nullable=True)


class Notice(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    notice_link: Mapped[str] = mapped_column()
    branch: Mapped[str] = mapped_column()


class LogInfo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    login_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Dhaka")))


class PhoneNumber(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_name: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column()


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    comment: Mapped[str] = mapped_column()
    comment_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Dhaka")))

    reply = relationship("CommentReply", back_populates="comment", uselist=False)


class CommentReply(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    replier: Mapped[str] = mapped_column()
    comment_id: Mapped[int] = mapped_column(ForeignKey(Comment.id))
    reply_txt: Mapped[str] = mapped_column()
    reply_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Dhaka")))

    comment = relationship("Comment", back_populates="reply")


class StudentRecord(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column()
    student_name: Mapped[str] = mapped_column()
    fathers_name: Mapped[str] = mapped_column()
    guardian_phone: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    class_name: Mapped[str] = mapped_column()
    roll: Mapped[str] = mapped_column()
    fixed_fee: Mapped[float] = mapped_column(nullable=True)  # ধার্যকৃত বেতন
    fixed_exam_fee: Mapped[float] = mapped_column(nullable=True)  # ধার্যকৃত পরীক্ষার ফি
    # Students a service admin registers wait for an admin's approval; an admin's own are approved at once
    status: Mapped[str] = mapped_column(default="Approved", server_default="Approved")


STUDENT_PENDING = "Pending"
STUDENT_APPROVED = "Approved"


class TeacherRecord(db.Model):
    """Registered teachers/staff. monthly_salary feeds the staff salary section of the expense page."""
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column()
    staff_id: Mapped[str] = mapped_column(unique=True)
    teacher_name: Mapped[str] = mapped_column()
    designation: Mapped[str] = mapped_column(nullable=True)  # পদবী
    phone: Mapped[str] = mapped_column(nullable=True)
    address: Mapped[str] = mapped_column(nullable=True)
    joining_date: Mapped[date] = mapped_column(Date, nullable=True)
    monthly_salary: Mapped[float] = mapped_column()  # মাসিক বেতন
    # Unpaid salary carried forward from the expense page (negative = paid in advance)
    salary_due: Mapped[float] = mapped_column(nullable=True)


class StaffPayment(db.Model):
    """One salary payment from the expense page, so it can be listed and cancelled."""
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Dhaka")))
    date: Mapped[date] = mapped_column(Date)
    branch: Mapped[str] = mapped_column()
    teacher_id: Mapped[int] = mapped_column(nullable=True)  # None for staff typed in by hand
    staff_name: Mapped[str] = mapped_column()
    staff_id: Mapped[str] = mapped_column(nullable=True)
    month: Mapped[int] = mapped_column()  # the month paid for (1-12)
    year: Mapped[int] = mapped_column()
    subtotal: Mapped[float] = mapped_column()  # this month's salary + other salary
    previous_due: Mapped[float] = mapped_column()
    total: Mapped[float] = mapped_column()
    paid: Mapped[float] = mapped_column()  # added into the month's box on the expense page
    due_after: Mapped[float] = mapped_column()
    due_before: Mapped[float] = mapped_column(nullable=True)  # the teacher's stored due, for cancelling
    datasheet_id: Mapped[int] = mapped_column(nullable=True)
    paid_by: Mapped[str] = mapped_column()
    cancelled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    cancelled_by: Mapped[str] = mapped_column(nullable=True)


class DataSheet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    branch: Mapped[str] = mapped_column(nullable=True)  # set on every save; older rows are filled in at startup
    monthly_fee: Mapped[float] = mapped_column()
    exam_fee: Mapped[float] = mapped_column()
    admission_fee: Mapped[float] = mapped_column()
    book_fee: Mapped[float] = mapped_column()
    copy_fee: Mapped[float] = mapped_column()
    id_card_fee: Mapped[float] = mapped_column()
    other_income: Mapped[float] = mapped_column()
    total_income: Mapped[float] = mapped_column()
    daily_expense: Mapped[float] = mapped_column()
    all_rent_and_bills: Mapped[float] = mapped_column()
    staff_salary: Mapped[float] = mapped_column()
    other_expenses: Mapped[float] = mapped_column()
    total_expense: Mapped[float] = mapped_column()


class Payment(db.Model):
    """One collection from the income page, so it can be looked up later or cancelled."""
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Dhaka")))
    date: Mapped[date] = mapped_column(Date)
    branch: Mapped[str] = mapped_column()
    class_name: Mapped[str] = mapped_column()
    student_id: Mapped[int] = mapped_column()
    student_name: Mapped[str] = mapped_column()
    month: Mapped[int] = mapped_column()  # the month collected for (1-12)
    collected_by: Mapped[str] = mapped_column()
    tuition_paid: Mapped[float] = mapped_column()
    misc_paid: Mapped[float] = mapped_column()
    # How the money was recorded in the data sheet, as {income field: amount}
    income: Mapped[str] = mapped_column()
    total_income: Mapped[float] = mapped_column()
    due_after: Mapped[float] = mapped_column(nullable=True)
    misc_due_after: Mapped[float] = mapped_column(nullable=True)
    datasheet_id: Mapped[int] = mapped_column(nullable=True)
    accounts_record_id: Mapped[int] = mapped_column(nullable=True)
    # What the save changed on the accounts record, so cancelling can put it back (JSON)
    undo: Mapped[str] = mapped_column()
    cancelled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    cancelled_by: Mapped[str] = mapped_column(nullable=True)


class BalanceSheet(db.Model):
    """One row per branch per day; each branch keeps its own running balance."""
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    branch: Mapped[str] = mapped_column(nullable=True)
    total_income: Mapped[float] = mapped_column()
    total_expense: Mapped[float] = mapped_column()
    deposit: Mapped[float] = mapped_column()
    deposit_description: Mapped[str] = mapped_column()
    withdraw: Mapped[float] = mapped_column()
    withdraw_description: Mapped[str] = mapped_column()
    balance: Mapped[float] = mapped_column()


@app.template_global()
def get_branches():
    # Creation order, so the first branch always comes first in every dropdown
    return db.session.execute(
        db.select(Branch).order_by(Branch.id)
    ).scalars().all()


# End of DB Models------------------------------------------------------------------------------------------------------

def add_missing_columns():
    """create_all() never alters existing tables, so add columns introduced after the table was created."""
    new_columns = {
        AccountsRecord.__table__.name: {"due_month": "INTEGER", "misc_due": "FLOAT"},
        Payment.__table__.name: {"misc_due_after": "FLOAT"},
        DataSheet.__table__.name: {"branch": "VARCHAR"},
        TeacherRecord.__table__.name: {"salary_due": "FLOAT"},
        BalanceSheet.__table__.name: {"branch": "VARCHAR"},
        StudentRecord.__table__.name: {"fixed_fee": "FLOAT",
                                       "fixed_exam_fee": "FLOAT",
                                       # Students registered before approvals existed count as approved
                                       "status": "VARCHAR NOT NULL DEFAULT 'Approved'"},
    }
    inspector = db.inspect(db.engine)
    with db.engine.begin() as connection:
        for table, columns in new_columns.items():
            existing = {column["name"] for column in inspector.get_columns(table)}
            for column, column_type in columns.items():
                if column not in existing:
                    connection.execute(db.text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))


def assign_sheet_branches():
    """Data sheet and balance sheet rows saved before branches were kept apart have no branch.
    A data sheet row takes the branch of the payment that made it; everything else goes to the
    first branch. Then each branch's running balance is worked out again."""
    data_rows = db.session.execute(db.select(DataSheet).where(DataSheet.branch.is_(None))).scalars().all()
    balance_rows = db.session.execute(db.select(BalanceSheet).where(BalanceSheet.branch.is_(None))).scalars().all()
    if not data_rows and not balance_rows:
        return
    first_branch = db.session.execute(db.select(Branch.name).order_by(Branch.id).limit(1)).scalar()
    if first_branch is None:
        return

    payment_branches = dict(db.session.execute(
        db.select(Payment.datasheet_id, Payment.branch)
        .where(Payment.datasheet_id.is_not(None), Payment.cancelled_at.is_(None))).all())
    for row in data_rows:
        row.branch = payment_branches.get(row.id, first_branch)
    for row in balance_rows:
        row.branch = first_branch
    db.session.flush()

    starts = {}
    for model in (DataSheet, BalanceSheet):
        for branch, day in db.session.execute(
                db.select(model.branch, func.min(model.date)).group_by(model.branch)).all():
            starts[branch] = min(day, starts.get(branch, day))
    for branch, day in starts.items():
        refresh_balance_sheet(branch, day)
    db.session.commit()


def seed_first_admin():
    """On a brand-new database, create the first branch and Admin account from .env.

    Runs only while there is no Admin user at all, so restarting the app (or changing .env later)
    never creates duplicates or overwrites anything. More branches are added from Branch Management.
    """
    if db.session.execute(db.select(User.id).where(User.role == ADMIN_ROLE).limit(1)).first():
        return

    branch_name = os.getenv("INITIAL_BRANCH_NAME") or "Main Branch"
    branch = db.session.execute(db.select(Branch).where(Branch.name == branch_name)).scalars().first()
    if branch is None:
        branch = Branch(
            code=os.getenv("INITIAL_BRANCH_CODE") or "MB",
            name=branch_name,
            director=os.getenv("INITIAL_BRANCH_DIRECTOR") or "",
            phone=os.getenv("INITIAL_BRANCH_PHONE") or "",
        )
        db.session.add(branch)
        db.session.flush()

    username = os.getenv("ADMIN_USERNAME") or "admin"
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        import secrets
        password = secrets.token_urlsafe(9)
        print(f"No ADMIN_PASSWORD in .env. Created admin '{username}' with password: {password}  "
              f"(change it after logging in)")

    try:
        school_id = int(os.getenv("ADMIN_SCHOOL_ID") or 101)
    except ValueError:
        school_id = 101

    admin = User(username=username, branch_id=branch.id, role=ADMIN_ROLE, school_id=school_id)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()


def ensure_upload_folders():
    """Upload routes save straight into these folders, so make sure they exist (e.g. after a fresh clone)."""
    os.makedirs(SYLLABUS_DIR, exist_ok=True)
    for (name,) in db.session.execute(db.select(Branch.name)).all():
        os.makedirs(os.path.join(NOTICES_DIR, name), exist_ok=True)


@app.cli.command("reset-admin-password")
@click.option("--username", help="Admin to reset. Needed only when there is more than one Admin.")
@click.option("--generate", is_flag=True, help="Create a random password and print it instead of asking.")
def reset_admin_password(username, generate):
    """Reset a forgotten Admin password. Run on the server:  flask --app app reset-admin-password"""
    admins = db.session.execute(db.select(User).where(User.role == ADMIN_ROLE)).scalars().all()
    names = ", ".join(a.username for a in admins) or "none"

    if username:
        admin = next((a for a in admins if a.username == username), None)
        if admin is None:
            raise click.ClickException(f"No Admin named '{username}'. Admins: {names}")
    elif len(admins) == 1:
        admin = admins[0]
    else:
        raise click.ClickException(f"Several Admins exist; choose one with --username. Admins: {names}")

    if generate:
        import secrets
        password = secrets.token_urlsafe(9)
    else:
        password = click.prompt(f"New password for '{admin.username}'", hide_input=True,
                                confirmation_prompt=True)
        if len(password) < MIN_PASSWORD_LENGTH:
            raise click.ClickException(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")

    admin.set_password(password)
    admin.is_active = True  # make sure the account can log in again
    db.session.commit()

    click.echo(f"Password for Admin '{admin.username}' has been reset.")
    if generate:
        click.echo(f"New password: {password}  (change it after logging in)")


with app.app_context():
    os.makedirs(app.instance_path, exist_ok=True)  # default sqlite database lives here
    db.create_all()
    add_missing_columns()
    seed_first_admin()
    ensure_upload_folders()


# Language ------------------------------------------------------------------------------------------------------------
# Every page can show English or Bangla. The choice is kept in a cookie, so it also works before login.
LANGUAGES = ("bn", "en")
DEFAULT_LANGUAGE = "bn"
LANGUAGE_COOKIE = "lang"


def current_language():
    lang = request.cookies.get(LANGUAGE_COOKIE)
    return lang if lang in LANGUAGES else DEFAULT_LANGUAGE


def tr(english, bangla):
    """Server-side messages (flash etc.) in the current language."""
    return bangla if current_language() == "bn" else english


@app.context_processor
def inject_language():
    lang = current_language()

    def t(english, bangla):
        """Pick the text for the current language: {{ t("Attendance", "হাজিরা") }}"""
        return bangla if lang == "bn" else english

    return {"lang": lang, "t": t}


@app.route("/set-language/<lang>")
def set_language(lang):
    if lang not in LANGUAGES:
        abort(404)

    # Go back to the page the button was clicked on, but never to another site
    target = request.referrer or ""
    parsed = urlparse(target)
    if not target or (parsed.netloc and parsed.netloc != request.host):
        target = url_for("login")

    response = redirect(target)
    response.set_cookie(LANGUAGE_COOKIE, lang, max_age=365 * 24 * 60 * 60, samesite="Lax")
    return response


# Routes -------------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = db.session.execute(db.select(User).where(User.username == username)).scalar()

        if user and user.check_password(password):
            log = LogInfo(username=user.username)
            db.session.add(log)
            db.session.commit()
            login_user(user, duration=timedelta(hours=3))
            return helpers.redirect_dashboard(user.role)

        flash(tr('Invalid username or password', 'ইউজারনেম অথবা পাসওয়ার্ড ভুল'), 'danger')
        return redirect(url_for("login"))

    return render_template('login.html')


# Dashboard Routes -----------------------------------------------------------------------------------------------------
@app.route('/admin-dashboard')
@login_required
@roles_required(ADMIN_ROLE)
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')


@app.route('/service-admin-dashboard')
@login_required
@roles_required(SERVICE_ADMIN_ROLE)
def service_admin_dashboard():
    return render_template('service_admin/service-admin_dashboard.html')


@app.route('/teacher-dashboard')
@login_required
@roles_required(TEACHER_ROLE)
def teacher_dashboard():
    return render_template('teacher/teacher_dashboard.html')


@app.route('/student-dashboard')
@login_required
@roles_required(STUDENT_ROLE)
def student_dashboard():
    # The class is the first digit of the school ID; Play-Three (1-5) use Lesson Schedule, Four/Five use Syllabus
    first = str(current_user.school_id or "")[:1]
    class_code = int(first) if first.isdigit() else 0
    return render_template('student/student_dashboard.html', class_code=class_code,
                           class_name=CLASS_MAP.get(class_code))


# Options --------------------------------------------------------------------------------------------------------------
@app.route("/lesson-schedule")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE, TEACHER_ROLE)
def lesson_schedule():
    return render_template("lesson_schedule.html", classes=CLASS_NAMES, subjects=SUBJECTS,
                           today=today_in_dhaka().isoformat())


def own_student_class():
    """A student's class always comes from their own login, never from the URL."""
    student_class = CLASS_MAP.get(int(str(current_user.school_id)[:1])) if str(current_user.school_id)[:1].isdigit() else None
    if student_class is None:
        abort(404)
    return student_class


@app.route("/student-lesson-schedule")
@login_required
@roles_required(STUDENT_ROLE)
def student_lesson_schedule():
    return render_template("student/lesson_schedule.html", student_class=own_student_class(),
                           today=today_in_dhaka().isoformat())


@app.route("/student-lesson-syllabus")
@login_required
@roles_required(STUDENT_ROLE)
def student_lesson_syllabus():
    student_class = own_student_class()
    return render_template("student/student_lesson_syllabus.html", student_class=student_class,
                           pdf_url=url_for("syllabus_pdf", class_name=student_class)
                           if student_class in SYLLABUS_CLASSES else None)


@app.route("/lesson-syllabus")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE, TEACHER_ROLE)
def lesson_syllabus():
    return render_template("lesson_syllabus.html", classes=SYLLABUS_CLASSES,
                           uploaded=[c for c in SYLLABUS_CLASSES if os.path.isfile(syllabus_path(c))])


SYLLABUS_CLASSES = ["Three", "Four", "Five"]  # classes that follow a PDF syllabus instead of a daily schedule
SYLLABUS_MAX_BYTES = 25 * 1024 * 1024


def syllabus_path(class_name):
    return os.path.join(SYLLABUS_DIR, f"{class_name}.pdf")


@app.route("/syllabus-pdf/<class_name>")
@login_required
def syllabus_pdf(class_name):
    """The syllabus PDF, only for logged-in users; a student only gets their own class's."""
    if class_name not in SYLLABUS_CLASSES:
        abort(404)
    if current_user.role == STUDENT_ROLE and class_from_school_id(current_user.school_id) != class_name:
        abort(403)
    if not os.path.isfile(syllabus_path(class_name)):
        abort(404)
    response = send_from_directory(SYLLABUS_DIR, f"{class_name}.pdf", mimetype="application/pdf", max_age=0)
    response.headers["Cache-Control"] = "no-store, private"
    return response


MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
CLASS_NAMES = list(CLASS_MAP.values())


def attendance_years():
    """This year and the two before, so last year's records stay reachable in January."""
    year = today_in_dhaka().year
    return [year, year - 1, year - 2]


def class_from_school_id(school_id):
    """A student's class is the first digit of their ID (see CLASS_MAP); None if it doesn't fit."""
    first = str(school_id or "")[:1]
    return CLASS_MAP.get(int(first)) if first.isdigit() else None


def can_open_attendance():
    # Service Admins need the attendance option, as on their dashboard
    return current_user.role != SERVICE_ADMIN_ROLE or current_user.has_attendance_option_access


@app.route("/attendance")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE, TEACHER_ROLE)
def attendance():
    if not can_open_attendance():
        abort(403)
    today = today_in_dhaka()
    return render_template("attendance.html", months=MONTH_NAMES, years=attendance_years(),
                           classes=CLASS_NAMES, current_month=MONTH_NAMES[today.month - 1],
                           current_year=today.year)


@app.route("/student-attendance")
@login_required
@roles_required(STUDENT_ROLE)
def student_attendance():
    # Always the logged-in student; the ?student_id= in the link is ignored
    student_class = class_from_school_id(current_user.school_id)
    today = today_in_dhaka()
    return render_template("student/attendance.html", student_class=student_class, months=MONTH_NAMES,
                           years=attendance_years(), current_month=MONTH_NAMES[today.month - 1],
                           current_year=today.year)


ACCOUNT_MONTHS = ["january", "february", "march", "april", "may", "june", "july",
                  "august", "september", "october", "november", "december"]


def can_open_accounts():
    # Service Admins need the accounts option, as on their dashboard
    return current_user.role == ADMIN_ROLE or (
            current_user.role == SERVICE_ADMIN_ROLE and current_user.has_accounts_option_access)


@app.route("/accounts")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def accounts():
    if not can_open_accounts():
        abort(403)
    return render_template("accounts.html", classes=CLASS_NAMES)


# Internal accounts (school income/expense) are staff-only
@app.route("/internal-accounts")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def internal_accounts():
    return render_template("internal_accounts.html")


@app.route("/internal-accounts-income")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def internal_accounts_income():
    return render_template("income.html")


@app.route("/internal-accounts-expense")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def internal_accounts_expense():
    return render_template("expense.html")


@app.route("/internal-accounts-datasheet")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def internal_accounts_datasheet():
    return render_template("datasheet.html")


@app.route("/internal-accounts-balance-sheet")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def internal_accounts_balance_sheet():
    return render_template("balancesheet.html")


@app.route("/student-accounts")
@login_required
@roles_required(STUDENT_ROLE)
def student_accounts():
    # Always the logged-in student; the ?student_id= in the link is ignored
    return render_template("student/student_accounts.html",
                           student_class=class_from_school_id(current_user.school_id))


EXAM_TYPES = ["1st Semester Assessment", "2nd Semester Assessment", "Final Semester Assessment"]


def can_open_results():
    # Service Admins need the result option, as on their dashboard
    return current_user.role != SERVICE_ADMIN_ROLE or current_user.has_results_option_access


def staff_results_page():
    if not can_open_results():
        abort(403)


def period_sort_key(period):
    """'2nd Semester Assessment 2026' / 'August 2026' -> sortable (year, order)."""
    parts = period.split()
    year = int(parts[-1]) if parts and parts[-1].isdigit() else 0
    name = " ".join(parts[:-1])
    if name in MONTH_NAMES:
        return year, MONTH_NAMES.index(name)
    return year, EXAM_TYPES.index(name) if name in EXAM_TYPES else len(EXAM_TYPES)


def student_periods(model, column):
    """Exams / months that have results for the logged-in student's branch and class, newest first."""
    values = db.session.execute(
        db.select(column).distinct().where(
            model.branch == current_user.branch.name,
            model.class_name == class_from_school_id(current_user.school_id),
        )
    ).scalars().all()
    return sorted(values, key=period_sort_key, reverse=True)


@app.route("/result")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE, TEACHER_ROLE)
def result():
    staff_results_page()
    return render_template("result.html")


@app.route("/student-result")
@login_required
@roles_required(STUDENT_ROLE)
def student_result():
    return render_template("student/student_result.html")


@app.route("/result/semester-assessment")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE, TEACHER_ROLE)
def semester_assessment():
    staff_results_page()
    return render_template("semester_assessment.html", classes=CLASS_NAMES, exam_types=EXAM_TYPES,
                           years=attendance_years(), current_year=today_in_dhaka().year)


@app.route("/student-result/semester-assessment")
@login_required
@roles_required(STUDENT_ROLE)
def student_semester_assessment():
    return render_template("student/semester_assessment.html",
                           student_class=class_from_school_id(current_user.school_id),
                           exams=student_periods(SemesterResultRecord, SemesterResultRecord.exam_name))


@app.route("/result/class-assessment")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE, TEACHER_ROLE)
def class_assessment():
    staff_results_page()
    today = today_in_dhaka()
    return render_template("class_assessment.html", classes=CLASS_NAMES, months=MONTH_NAMES,
                           years=attendance_years(), current_month=MONTH_NAMES[today.month - 1],
                           current_year=today.year)


@app.route("/student-result/class-assessment")
@login_required
@roles_required(STUDENT_ROLE)
def student_class_assessment():
    return render_template("student/class_assessment.html",
                           student_class=class_from_school_id(current_user.school_id),
                           months=student_periods(ClassTestResultRecord, ClassTestResultRecord.month))


@app.route("/qr-code-management")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def qr_code_management():
    return render_template("admin/qr_code_management.html")


@app.route("/qr-scanner")
@login_required
def qr_scanner():
    return render_template("qr_scanner.html")


@app.route("/qr-code-management/tutorial-management")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def tutorial_management():
    return render_template("admin/tutorial_management.html", classes=CLASS_NAMES)


@app.route("/admin-user-management")
@login_required
@roles_required(ADMIN_ROLE)
def admin_user_management():
    return render_template("admin/user_management.html")


@app.route("/admin-user-management/service-admin")
@login_required
@roles_required(ADMIN_ROLE)
def service_admin_user_management():
    return render_template("admin/service_admin_user_management.html")


@app.route("/admin-user-management/teacher")
@login_required
@roles_required(ADMIN_ROLE)
def teacher_user_management():
    return render_template("admin/teacher_user_management.html")


@app.route("/admin-user-management/student")
@login_required
@roles_required(ADMIN_ROLE)
def student_user_management():
    return render_template("admin/student_user_management.html")


def can_open_notices():
    # Service Admins need the Notice option, as on their dashboard
    return current_user.role != SERVICE_ADMIN_ROLE or current_user.has_notice_access


@app.route("/notice-board-management")
@login_required
def notice_board_management():
    if not can_open_notices():
        abort(403)

    branches = [b.name for b in get_branches()]
    own_branch = current_user.branch.name if current_user.branch else None
    if current_user.role == ADMIN_ROLE:
        # Admins can look at any branch's notice board
        requested = (request.args.get("branch") or "").strip()
        branch = requested if requested in branches else (own_branch if own_branch in branches else
                                                          (branches[0] if branches else None))
    else:
        branch = own_branch

    return render_template("notice_board_management.html", notices=list_notices(branch),
                           branch=branch, branches=branches,
                           can_manage=current_user.role in (ADMIN_ROLE, SERVICE_ADMIN_ROLE),
                           max_mb=NOTICE_MAX_BYTES // (1024 * 1024))


@app.route("/branch-management")
@login_required
@roles_required(ADMIN_ROLE)
def branch_management():
    user_counts = dict(db.session.execute(
        db.select(User.branch_id, func.count()).group_by(User.branch_id)).all())
    student_counts = dict(db.session.execute(
        db.select(StudentRecord.branch, func.count()).group_by(StudentRecord.branch)).all())
    branches = [{"branch": b, "users": user_counts.get(b.id, 0), "students": student_counts.get(b.name, 0)}
                for b in get_branches()]
    return render_template("admin/branch_management.html", branches=branches)


@app.route("/log-info")
@login_required
@roles_required(ADMIN_ROLE)
def log_info():
    # Logs are loaded per day by the page (there are thousands; loading them all made the page slow)
    return render_template("admin/log_info.html", today=today_in_dhaka().isoformat())


MAX_COMMENT_LENGTH = 1000


def can_manage_comments():
    """Admins always; Service Admins only when given the comment option."""
    return current_user.role == ADMIN_ROLE or (
            current_user.role == SERVICE_ADMIN_ROLE and current_user.has_comment_access)


def managed_comments_query():
    """Comments the current user may read and reply to: all for an Admin,
    only comments from their own branch's users for a Service Admin."""
    stmt = db.select(Comment)
    if current_user.role != ADMIN_ROLE:
        stmt = stmt.join(User, User.username == Comment.username).where(User.branch_id == current_user.branch_id)
    return stmt


def format_comment_time(value):
    return value.strftime("%d-%m-%Y %I:%M %p") if value else ""


def serialize_comment(comment):
    return {
        "id": comment.id,
        "comment": comment.comment,
        "username": comment.username,
        # Unanswered comments have no reply row
        "reply_txt": comment.reply.reply_txt if comment.reply else "",
        "comment_time": format_comment_time(comment.comment_time),
    }


@app.route("/submitted-comments")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def submitted_comments():
    if not can_manage_comments():
        abort(403)
    comments = db.session.execute(
        managed_comments_query().order_by(Comment.comment_time.desc())
    ).scalars().all()
    return render_template("admin/comments.html", comments=[serialize_comment(c) for c in comments])


@app.route("/comment")
@login_required
def student_comment():
    comments = db.session.execute(
        db.select(Comment).where(Comment.username == current_user.username).order_by(Comment.comment_time.desc())
    ).scalars().all()
    return render_template("student/comments.html", comments=comments, format_time=format_comment_time,
                           max_length=MAX_COMMENT_LENGTH)


def normalize_phone(text):
    """Keep digits (Bengali digits converted) and a leading +; drop spaces, dashes, etc."""
    text = (text or "").strip().translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789"))
    digits = "".join(ch for ch in text if ch.isdigit())
    return ("+" + digits) if text.startswith("+") and digits else digits


@app.template_filter("whatsapp_number")
def whatsapp_number(phone):
    """wa.me needs the full international number without '+': 017... -> 88017..."""
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    return "88" + digits if digits.startswith("01") else digits


def can_manage_phone_numbers():
    return current_user.role in (ADMIN_ROLE, SERVICE_ADMIN_ROLE)


def phone_branch_for_current_user(requested_branch):
    """A Service Admin can only manage their own branch; an Admin any existing branch."""
    if current_user.role == SERVICE_ADMIN_ROLE:
        return current_user.branch.name
    requested_branch = (requested_branch or "").strip()
    exists = db.session.execute(db.select(Branch.id).where(Branch.name == requested_branch).limit(1)).first()
    return requested_branch if exists else None


def validate_phone_form():
    """Returns (name, phone, error)."""
    name = (request.form.get("name") or "").strip()
    phone = normalize_phone(request.form.get("phone_number"))
    if not name:
        return name, phone, tr("Please enter a name.", "অনুগ্রহ করে নাম লিখুন।")
    if not 6 <= len(phone.lstrip("+")) <= 15:
        return name, phone, tr("Enter a valid phone number.", "সঠিক ফোন নাম্বার লিখুন।")
    return name, phone, None


@app.route("/call-services")
@login_required
def call_services():
    # Branches in the order they were created (Branch.id), so the first branch comes first.
    # Outer join: numbers whose branch no longer exists still show, at the end.
    stmt = (
        db.select(PhoneNumber)
        .outerjoin(Branch, Branch.name == PhoneNumber.branch_name)
        .order_by(Branch.id.is_(None), Branch.id, PhoneNumber.id)
    )
    # Admins see every branch; everyone else only their own
    if current_user.role != ADMIN_ROLE:
        stmt = stmt.where(PhoneNumber.branch_name == current_user.branch.name)
    phone_numbers = db.session.execute(stmt).scalars().all()

    grouped = {}
    for phone_number in phone_numbers:
        grouped.setdefault(phone_number.branch_name, []).append(phone_number)

    return render_template("call_service.html", grouped=grouped, phone_count=len(phone_numbers),
                           can_manage=can_manage_phone_numbers())


@app.route("/student-registration")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def student_registration():
    return render_template("service_admin/student_registration.html")


@app.route("/teacher-registration")
@login_required
@roles_required(ADMIN_ROLE)
def teacher_registration():
    return render_template("admin/teacher_registration.html")


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


# APIs -----------------------------------------------------------------------------------------------------------------
SUBJECTS = ["Arabic", "Quran", "Bengali", "Science", "English", "Math", "BGS", "Aqaid & Fiqh"]


def schedule_date(value):
    """An Excel date cell or a typed date (day first, as written in Bangladesh: 25/01/2026) -> date, else None."""
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return None
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip().translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789"))
    if not text:
        return None
    parsed = pd.to_datetime(text, errors="coerce", dayfirst=not text[:4].isdigit())
    return None if pd.isna(parsed) else parsed.date()


@app.route("/upload-curriculum", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_curriculum():
    try:
        class_name = (request.form.get("class_name") or "").strip()
        subject_name = (request.form.get("subject_name") or "").strip()
        if class_name not in CLASS_NAMES:
            raise ValueError("অনুগ্রহ করে সঠিক শ্রেণী নির্বাচন করুন।")
        if subject_name not in SUBJECTS:
            raise ValueError("অনুগ্রহ করে সঠিক বিষয় নির্বাচন করুন।")

        file = request.files.get("excel_file")
        if not file or file.filename == "":
            raise ValueError("No file uploaded")
        if not file.filename.lower().endswith(".xlsx"):
            raise ValueError("Only .xlsx Excel files are supported. In Excel use Save As → .xlsx")

        df = pd.read_excel(file)
        headers = {str(c).strip().lower(): c for c in df.columns}
        missing = [name for name in ("Date", "Topic") if name.lower() not in headers]
        if missing:
            raise ValueError(f"Excel file is missing column(s): {', '.join(missing)}")

        records = []
        for excel_row, row in enumerate(df.to_dict("records"), start=2):
            raw_date, topic = row[headers["date"]], row[headers["topic"]]
            topic = "" if topic is None or (not isinstance(topic, str) and pd.isna(topic)) else str(topic).strip()
            day = schedule_date(raw_date)
            if not topic and day is None:
                continue  # blank line
            if day is None:
                raise ValueError(f"Row {excel_row}: '{raw_date}' is not a valid date (use DD/MM/YYYY).")
            if not topic:
                continue  # a date with no lesson
            records.append(Curriculum(class_name=class_name, subject_name=subject_name, date=day, topic=topic))

        if not records:
            raise ValueError("Excel file has no lesson rows.")

        # Replace this class + subject only once the whole file is valid
        db.session.query(Curriculum).filter_by(class_name=class_name, subject_name=subject_name).delete()
        db.session.add_all(records)
        db.session.commit()
        flash(tr(f"Lesson schedule uploaded: {class_name} · {subject_name} ({len(records)} days).",
                 f"পাঠ পরিকল্পনা আপলোড হয়েছে: {class_name} · {subject_name} ({len(records)} দিন)।"), "success")
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")

    return redirect(url_for("lesson_schedule"))


@app.route("/upload-syllabus", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_syllabus():
    try:
        # The class becomes the file name, so it must be one of the known classes (no paths)
        class_name = (request.form.get("class_name") or "").strip()
        if class_name not in SYLLABUS_CLASSES:
            raise ValueError("অনুগ্রহ করে সঠিক শ্রেণী নির্বাচন করুন।")

        file = request.files.get("pdf_file")
        if not file or file.filename == "":
            raise ValueError("No file uploaded")
        data = file.read(SYLLABUS_MAX_BYTES + 1)
        if len(data) > SYLLABUS_MAX_BYTES:
            raise ValueError(f"PDF is too large. Maximum size is {SYLLABUS_MAX_BYTES // (1024 * 1024)} MB.")
        if not data.startswith(b"%PDF"):
            raise ValueError("Only PDF files can be uploaded as a syllabus.")

        os.makedirs(SYLLABUS_DIR, exist_ok=True)
        temp_path = syllabus_path(class_name) + ".uploading"
        with open(temp_path, "wb") as out:
            out.write(data)
        os.replace(temp_path, syllabus_path(class_name))  # the old PDF stays until the new one is fully saved
        flash(tr(f"Lesson syllabus uploaded for class {class_name}.", f"{class_name} শ্রেণীর সিলেবাস আপলোড হয়েছে।"), "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("lesson_syllabus"))


@app.route("/api/search-curriculum", methods=["POST"])
@login_required
def search_curriculum():
    data = request.get_json(silent=True) or {}
    if current_user.role == STUDENT_ROLE:
        class_name = class_from_school_id(current_user.school_id)  # students only see their own class
    else:
        class_name = (data.get("class") or "").strip()
    if class_name not in CLASS_NAMES:
        return jsonify({"success": False, "error": "Please select a valid class", "data": []}), 400
    try:
        day = date.fromisoformat(str(data.get("date") or ""))
    except ValueError:
        return jsonify({"success": False, "error": "Please select a valid date", "data": []}), 400

    rows = db.session.execute(
        db.select(Curriculum).where(Curriculum.class_name == class_name, Curriculum.date == day)
    ).scalars().all()
    order = {name: i for i, name in enumerate(SUBJECTS)}
    rows.sort(key=lambda r: (order.get(r.subject_name, len(order)), r.subject_name, r.id))

    return jsonify({"success": True, "class": class_name, "date": day.strftime("%d-%m-%Y"),
                    "data": [{"subject": r.subject_name, "topic": r.topic} for r in rows]})


@app.route("/api/upload-videos", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_videos():
    try:
        class_name = (request.form.get("class_name") or "").strip()
        if class_name not in CLASS_NAMES:
            raise ValueError("অনুগ্রহ করে সঠিক শ্রেণী নির্বাচন করুন।")
        # A video ID starts with its class number (Play = 1 ... Five = 7); the QR on the book is that ID
        class_digit = str(CLASS_NAMES.index(class_name) + 1)

        file = request.files.get("excel_file")
        if not file or file.filename == "":
            raise ValueError("No file uploaded")
        if not file.filename.lower().endswith(".xlsx"):
            raise ValueError("Only .xlsx Excel files are supported. In Excel use Save As → .xlsx")

        df = pd.read_excel(file)
        headers = {str(c).strip().lower(): c for c in df.columns}
        missing = [name for name in ("ID", "Link") if name.lower() not in headers]
        if missing:
            raise ValueError(f"Excel file is missing column(s): {', '.join(missing)}")

        videos, seen = [], set()
        for excel_row, row in enumerate(df.itertuples(index=False), start=2):
            row = dict(zip(df.columns, row))
            raw_id, raw_link = row[headers["id"]], row[headers["link"]]
            if raw_id is None or pd.isna(raw_id):
                continue  # blank line in the sheet
            try:
                video_id = int(float(raw_id))
            except (TypeError, ValueError):
                raise ValueError(f"Row {excel_row}: ID '{raw_id}' is not a number.")
            if not str(video_id).startswith(class_digit):
                raise ValueError(f"Row {excel_row}: ID {video_id} must start with {class_digit} for class {class_name}.")
            if video_id in seen:
                raise ValueError(f"Row {excel_row}: ID {video_id} appears more than once.")
            seen.add(video_id)

            link = helpers.youtube_embed_url(None if raw_link is None or pd.isna(raw_link) else raw_link)
            if link is None:
                raise ValueError(f"Row {excel_row}: '{raw_link}' is not a valid YouTube link.")
            videos.append(Video(id=video_id, class_name=class_name, link=link))

        if not videos:
            raise ValueError("Excel file has no video rows.")

        # IDs are unique across all classes; refuse ones that belong to another class
        taken = db.session.execute(
            db.select(Video.id, Video.class_name).where(Video.id.in_(seen), Video.class_name != class_name)
        ).all()
        if taken:
            raise ValueError("These IDs already belong to another class: " +
                             ", ".join(f"{vid} ({cls})" for vid, cls in taken[:10]))

        # Replace this class's links only once the whole file is valid
        db.session.query(Video).filter_by(class_name=class_name).delete()
        db.session.add_all(videos)
        db.session.commit()
        flash(tr(f"Video links uploaded successfully ({len(videos)} videos).",
                 f"ভিডিও লিংক সফলভাবে আপলোড হয়েছে ({len(videos)} টি ভিডিও)।"), "success")
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")

    return redirect(url_for("tutorial_management"))


@app.route("/api/search-video-links", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def search_video_links():
    class_ = ((request.get_json(silent=True) or {}).get("class") or "").strip()
    if class_ not in CLASS_NAMES:
        return jsonify({"success": False, "error": "Please select a valid class", "data": []}), 400

    videos = db.session.execute(
        db.select(Video).where(Video.class_name == class_).order_by(Video.id)
    ).scalars().all()

    return jsonify({"success": True, "data": [
        {"id": v.id, "link": v.link, "url": url_for("show_video", video_id=v.id)} for v in videos
    ]})


@app.route("/api/add-user", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def add_user():
    data = request.json

    # Extract fields
    school_id = data.get("id")
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    branch = data.get("branch")

    # Options (lesson_schedule, attendance, accounts, result, qr_scanner)
    lesson_schedule_access = data.get("lesson_schedule", False)
    attendance_access = data.get("attendance", False)
    accounts_access = data.get("accounts", False)
    result_access = data.get("result", False)
    qr_code_access = data.get("qr_code", False)
    comment_access = data.get("comments", False)
    notice_access = data.get("notice", False)

    # Simple validation
    if not school_id or not username or not password or not role:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    branch = db.session.execute(db.select(Branch).where(Branch.name == branch)).scalar()
    # Add user
    user = User(
        school_id=school_id,
        username=username,
        role=role,
        branch_id=branch.id,
        has_lesson_schedule_option_access=lesson_schedule_access,
        has_attendance_option_access=attendance_access,
        has_accounts_option_access=accounts_access,
        has_results_option_access=result_access,
        has_qr_code_access=qr_code_access,
        has_comment_access=comment_access,
        has_notice_access=notice_access,
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True})


@app.route("/api/search-users", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def search_users():
    filters = request.json or {}
    branch_name = filters.get("branch")
    role = filters.get("role")
    school_id = filters.get("id")  # comes from the client
    class_ = filters.get("studentClass")
    stmt = db.select(User)

    # filter by branch if provided
    if branch_name:
        # find branch first
        branch_obj = db.session.execute(
            db.select(Branch).where(Branch.name == branch_name)
        ).scalars().first()

        # if branch not found, return empty result
        if branch_obj is None:
            return jsonify({"users": []})

        stmt = stmt.where(User.branch_id == branch_obj.id)

    # filter by role if provided
    if role:
        stmt = stmt.where(User.role == role)

    # filter by school_id if provided
    if school_id:
        try:
            school_id_int = int(school_id)
            stmt = stmt.where(User.school_id == school_id_int)
        except ValueError:
            # invalid numeric id; return empty result or ignore
            return jsonify({"users": []})

    # execute query
    users = db.session.execute(stmt).scalars().all()

    if class_:
        users = filter(lambda user: str(user.school_id).startswith(class_), users)

    # serialize cleanly
    def serialize_user(u):
        return {
            "db_id": u.id,
            "id": u.school_id,  # adjust field names to your model
            "username": u.username,
            "role": u.role,
            "branch": getattr(u.branch, "name", None) if getattr(u, "branch", None) else None,
            # example option fields; rename if different in your model
            "lesson_schedule": u.has_lesson_schedule_option_access,
            "attendance": u.has_attendance_option_access,
            "accounts": u.has_accounts_option_access,
            "result": u.has_results_option_access,
            "qr_code": u.has_qr_code_access,
            "comments": u.has_comment_access,
            "notice": u.has_notice_access,
        }

    users_serialized = [serialize_user(u) for u in users]

    return jsonify({"users": users_serialized})


@app.route("/api/update-user", methods=["PATCH"])
@login_required
@roles_required(ADMIN_ROLE)
def update_user():
    data = request.json

    # Extract fields
    db_id = data.get("db_id")
    school_id = data.get("id")
    username = data.get("username")
    branch = data.get("branch")

    # Options (lesson_schedule, attendance, accounts, result, qr_scanner)
    lesson_schedule_access = data.get("lesson_schedule", False)
    attendance_access = data.get("attendance", False)
    accounts_access = data.get("accounts", False)
    result_access = data.get("result", False)
    qr_code_access = data.get("qr_code", False)
    comments_access = data.get("comments", False)
    notice_access = data.get("notice", False)

    # Simple validation
    if not school_id or not username:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    branch_obj = db.session.execute(db.select(Branch).where(Branch.name == branch)).scalar()

    # Update user
    user = db.session.get(User, db_id)
    user.school_id = school_id
    user.username = username
    user.branch_id = branch_obj.id
    user.has_lesson_schedule_option_access = lesson_schedule_access
    user.has_attendance_option_access = attendance_access
    user.has_accounts_option_access = accounts_access
    user.has_results_option_access = result_access
    user.has_qr_code_access = qr_code_access
    user.has_comment_access = comments_access
    user.has_notice_access = notice_access

    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/delete-user/<id>", methods=["DELETE"])
@login_required
@roles_required(ADMIN_ROLE)
def delete_user(id):
    try:
        user = db.session.get(User, id)
        db.session.delete(user)
        db.session.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


MIN_PASSWORD_LENGTH = 6


@app.route('/api/change-password', methods=["PATCH"])
@login_required
@roles_required(ADMIN_ROLE)
def change_password():
    """Admin sets another user's password (user management pages)."""
    data = request.get_json(silent=True) or {}
    password = data.get("password") or ""
    # Spaces don't count towards the length, so "      " can't become a password
    if len(password.strip()) < MIN_PASSWORD_LENGTH:
        return jsonify({"success": False,
                        "error": f"Password must be at least {MIN_PASSWORD_LENGTH} characters"}), 400

    try:
        user_id = int(data.get("id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "User not found"}), 404

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"success": False, "error": "User not found"}), 404

    user.set_password(password)
    db.session.commit()
    return jsonify({"success": True})


@app.route('/change-password', methods=["GET", "POST"])
@login_required
def change_own_password():
    """Any logged-in user changes their own password (needs the current one)."""
    if request.method == "POST":
        current_password = request.form.get("current_password") or ""
        new_password = request.form.get("new_password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not current_user.check_password(current_password):
            flash(tr("The current password is incorrect.", "বর্তমান পাসওয়ার্ড সঠিক নয়।"), "danger")
        elif len(new_password.strip()) < MIN_PASSWORD_LENGTH:  # spaces don't count
            flash(tr(f"The new password must be at least {MIN_PASSWORD_LENGTH} characters.",
                     f"নতুন পাসওয়ার্ড কমপক্ষে {MIN_PASSWORD_LENGTH} অক্ষরের হতে হবে।"), "danger")
        elif new_password != confirm_password:
            flash(tr("The new passwords do not match.", "নতুন পাসওয়ার্ড দুটি মিলছে না।"), "danger")
        elif new_password == current_password:
            flash(tr("The new password must be different from the current one.",
                     "নতুন পাসওয়ার্ড বর্তমান পাসওয়ার্ড থেকে আলাদা হতে হবে।"), "danger")
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash(tr("Password changed successfully.", "পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে।"), "success")

        return redirect(url_for("change_own_password"))

    return render_template("change_password.html", min_length=MIN_PASSWORD_LENGTH)


def attendance_branch_for_current_user(requested_branch):
    """Admins may use any existing branch; everyone else only their own."""
    if current_user.role != ADMIN_ROLE:
        return current_user.branch.name
    requested_branch = (requested_branch or "").strip()
    exists = db.session.execute(db.select(Branch.id).where(Branch.name == requested_branch).limit(1)).first()
    return requested_branch if exists else None


def valid_attendance_month(month):
    """'November 2026' style, as stored by uploads."""
    parts = (month or "").split()
    return len(parts) == 2 and parts[0] in MONTH_NAMES and parts[1].isdigit()


def excel_day_columns(columns):
    """Map day number (1-31) -> column label. Headers may be 1, "1", 1.0 or a date in that month."""
    days = {}
    for column in columns:
        if isinstance(column, (datetime, date, pd.Timestamp)):
            day = column.day
        else:
            try:
                day = int(float(str(column).strip()))
            except ValueError:
                continue
        if 1 <= day <= 31 and day not in days:
            days[day] = column
    return days


def attendance_cell(value):
    """Excel cell -> stored text: blanks become None and 1.0 becomes "1"."""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = str(value).strip()
    return text or None


@app.route('/upload-attendance', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_attendance():
    try:
        if not can_open_attendance():
            abort(403)

        branch = attendance_branch_for_current_user(request.form.get("branch_name"))
        class_ = (request.form.get("class_name") or "").strip()
        month = (request.form.get("month_name") or "").strip()

        if branch is None:
            raise ValueError("অনুগ্রহ করে সঠিক ব্রাঞ্চ নির্বাচন করুন।")
        if class_ not in CLASS_NAMES:
            raise ValueError("অনুগ্রহ করে সঠিক শ্রেণী নির্বাচন করুন।")
        if not valid_attendance_month(month):
            raise ValueError("অনুগ্রহ করে সঠিক মাস নির্বাচন করুন।")

        file = request.files.get('excel_file')
        if not file or file.filename == "":
            raise ValueError("No file uploaded")
        if not file.filename.lower().endswith(".xlsx"):
            raise ValueError("Only .xlsx Excel files are supported. In Excel use Save As → .xlsx")

        df = pd.read_excel(file)
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

        missing = [c for c in ("ID", "Student Name") if c not in df.columns]
        if missing:
            raise ValueError(f"Excel file is missing column(s): {', '.join(missing)}")

        day_columns = excel_day_columns(df.columns)
        if not day_columns:
            raise ValueError("Excel file has no date columns (headers 1 to 31).")

        records = []
        for excel_row, row in enumerate(df.itertuples(index=False), start=2):
            row = dict(zip(df.columns, row))
            if row["ID"] is None or pd.isna(row["ID"]):
                continue  # blank line in the sheet
            try:
                student_id = int(float(row["ID"]))
            except (TypeError, ValueError):
                raise ValueError(f"Row {excel_row}: ID '{row['ID']}' is not a number.")

            record = AttendanceRecord(
                branch=branch,
                class_name=class_,
                month=month,
                student_id=student_id,
                student_name=helpers.convert_bangla_text(attendance_cell(row["Student Name"]) or ""),
            )
            for day in range(1, 32):
                column = day_columns.get(day)
                setattr(record, f"d{day}", attendance_cell(row[column]) if column is not None else None)
            records.append(record)

        if not records:
            raise ValueError("Excel file has no student rows.")

        # Replace the previous upload for this branch/class/month in the same transaction
        db.session.query(AttendanceRecord).filter_by(branch=branch, class_name=class_, month=month).delete()
        db.session.add_all(records)
        db.session.commit()
        flash(tr(f"Attendance uploaded successfully ({len(records)} students).",
                 f"হাজিরা সফলভাবে আপলোড হয়েছে ({len(records)} জন শিক্ষার্থী)।"), "success")

    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")

    return redirect(url_for("attendance"))


@app.route("/api/search-attendance", methods=["POST"])
@login_required
def search_attendance():
    data = request.get_json(silent=True) or {}
    month = (data.get("month") or "").strip()

    if current_user.role == STUDENT_ROLE:
        # Students only ever see their own record
        branch_name = current_user.branch.name
        class_name = class_from_school_id(current_user.school_id)
        student_id = current_user.school_id
    else:
        if not can_open_attendance():
            abort(403)
        branch_name = attendance_branch_for_current_user(data.get("branch"))
        class_name = (data.get("class") or "").strip()
        student_id = data.get("student_id")

    if branch_name is None or class_name not in CLASS_NAMES or not valid_attendance_month(month):
        return jsonify({"success": False, "error": "Please select a valid branch, class and month", "data": []}), 400

    stmt = db.select(AttendanceRecord).where(
        AttendanceRecord.branch == branch_name,
        AttendanceRecord.class_name == class_name,
        AttendanceRecord.month == month,
    )
    if student_id:
        try:
            stmt = stmt.where(AttendanceRecord.student_id == int(student_id))
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Invalid ID", "data": []}), 400

    rows = db.session.execute(stmt.order_by(AttendanceRecord.student_id)).scalars().all()

    results = []
    for r in rows:
        record = {"ID": r.student_id, "student_name": r.student_name}
        for i in range(1, 32):
            value = getattr(r, f"d{i}")
            # Older uploads stored 1.0 / "nan"; show them as "1" / blank
            if value in ("nan", "None"):
                value = None
            elif isinstance(value, str) and value.endswith(".0") and value[:-2].isdigit():
                value = value[:-2]
            record[f"d{i}"] = value
        results.append(record)

    return jsonify({"success": True, "data": results})


def account_amount(value):
    """Excel cell -> stored amount: blanks become None, numbers (also Bengali digits) a float.
    Any other text (e.g. a note) is kept as written."""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")).replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return str(value).strip()


def account_value_for_display(value):
    """Numbers stay numbers (500.0 -> 500); text is converted from Bijoy to Unicode."""
    if value is None:
        return None
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, int):
        return value
    return helpers.convert_bangla_text(value)


@app.route('/upload-accounts', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_accounts():
    try:
        if not can_open_accounts():
            abort(403)

        branch = attendance_branch_for_current_user(request.form.get("branch_name"))
        class_ = (request.form.get("class_name") or "").strip()

        if branch is None:
            raise ValueError("অনুগ্রহ করে সঠিক ব্রাঞ্চ নির্বাচন করুন।")
        if class_ not in CLASS_NAMES:
            raise ValueError("অনুগ্রহ করে সঠিক শ্রেণী নির্বাচন করুন।")

        file = request.files.get('excel_file')
        if not file or file.filename == "":
            raise ValueError("No file uploaded")
        if not file.filename.lower().endswith(".xlsx"):
            raise ValueError("Only .xlsx Excel files are supported. In Excel use Save As → .xlsx")

        df = pd.read_excel(file)
        # Match headers case-insensitively: "January", "january ", "JANUARY" all work
        columns = {str(c).strip().lower(): c for c in df.columns}

        missing = [name for name in ("ID", "Student Name") if name.lower() not in columns]
        if missing:
            raise ValueError(f"Excel file is missing column(s): {', '.join(missing)}")
        if not any(month in columns for month in ACCOUNT_MONTHS + ["due"]):
            raise ValueError("Excel file has no month columns (January to December) or Due column.")

        records = []
        for excel_row, row in enumerate(df.itertuples(index=False), start=2):
            row = dict(zip(df.columns, row))
            raw_id = row[columns["id"]]
            if raw_id is None or pd.isna(raw_id):
                continue  # blank line in the sheet
            try:
                student_id = int(float(raw_id))
            except (TypeError, ValueError):
                raise ValueError(f"Row {excel_row}: ID '{raw_id}' is not a number.")

            name = row[columns["student name"]]
            record = AccountsRecord(
                branch=branch,
                class_name=class_,
                student_id=student_id,
                student_name=helpers.convert_bangla_text("" if name is None or pd.isna(name) else str(name)),
            )
            for field in ACCOUNT_MONTHS + ["due"]:
                setattr(record, field, account_amount(row[columns[field]]) if field in columns else None)
            records.append(record)

        if not records:
            raise ValueError("Excel file has no student rows.")

        # The misc due is not in the Excel file, so carry it over to the new rows
        misc_dues = dict(db.session.execute(
            db.select(AccountsRecord.student_id, AccountsRecord.misc_due)
            .where(AccountsRecord.branch == branch, AccountsRecord.class_name == class_)).all())
        for record in records:
            record.misc_due = misc_dues.get(record.student_id)

        # Replace this class's previous upload only once the new file has been read successfully
        db.session.query(AccountsRecord).filter_by(branch=branch, class_name=class_).delete()
        db.session.add_all(records)
        db.session.commit()
        flash(tr(f"Accounts uploaded successfully ({len(records)} students).",
                 f"হিসাব সফলভাবে আপলোড হয়েছে ({len(records)} জন শিক্ষার্থী)।"), "success")
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")

    return redirect(url_for("accounts"))


@app.route('/api/search-accounts', methods=['POST'])
@login_required
def search_accounts():
    """Used by the Accounts page, the student's salary card and the internal income page."""
    data = request.get_json(silent=True) or {}

    if current_user.role == STUDENT_ROLE:
        # Students only ever see their own record
        branch = current_user.branch.name
        class_ = class_from_school_id(current_user.school_id)
        student_id = current_user.school_id
    elif current_user.role in (ADMIN_ROLE, SERVICE_ADMIN_ROLE):
        branch = attendance_branch_for_current_user(data.get("branch"))
        class_ = (data.get("class") or "").strip()
        student_id = data.get("student_id")
    else:
        abort(403)

    if branch is None or class_ not in CLASS_NAMES:
        return jsonify({"success": False, "error": "Please select a valid branch and class", "data": []}), 400

    stmt = db.select(AccountsRecord).where(AccountsRecord.branch == branch, AccountsRecord.class_name == class_)
    if student_id:
        try:
            stmt = stmt.where(AccountsRecord.student_id == int(student_id))
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Invalid ID", "data": []}), 400

    records = db.session.execute(stmt.order_by(AccountsRecord.student_id)).scalars().all()

    # Each student's fixed monthly and exam fees come from Student Registration, matched by branch and roll
    fixed_fees = {roll: (fee, exam_fee) for roll, fee, exam_fee in db.session.execute(
        db.select(StudentRecord.roll, StudentRecord.fixed_fee, StudentRecord.fixed_exam_fee)
        .where(StudentRecord.branch == branch)).all()}

    results = []
    for record in records:
        fee, exam_fee = fixed_fees.get(str(record.student_id), (None, None))
        row = {"ID": record.student_id, "student_name": record.student_name,
               "fixed_fee": fee, "fixed_exam_fee": exam_fee, "misc_due": money(record.misc_due)}
        for field in ACCOUNT_MONTHS + ["due"]:
            row[field] = account_value_for_display(getattr(record, field))
        results.append(row)

    return jsonify({"success": True, "data": results})


# Income columns of DataSheet, in the order they appear in the table
INCOME_FIELDS = ["monthly_fee", "exam_fee", "admission_fee", "book_fee",
                 "copy_fee", "id_card_fee", "other_income"]


def money(value):
    """A stored amount as a number: blanks and notes count as 0; rounded to paisa."""
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0


def take(rest, limit):
    """Take up to `limit` from `rest`; returns (taken, what is left)."""
    taken = round(max(0.0, min(rest, limit)), 2)
    return taken, round(rest - taken, 2)


def read_amount(data, key):
    try:
        amount = float(data.get(key) or 0)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid amount for {key}")
    if amount < 0:
        raise ValueError(f"{key} cannot be negative")
    return round(amount, 2)


def read_signed_amount(data, key):
    """An optional amount that may be negative (an advance): None when it was left out or blank."""
    value = data.get(key)
    if value in (None, ""):
        return None
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid amount for {key}")
    if not math.isfinite(amount):
        raise ValueError(f"Invalid amount for {key}")
    return round(amount, 2)


# Miscellaneous items, in the order a misc payment is shared out between them
MISC_FIELDS = ["admission_fee", "book_fee", "copy_fee", "id_card_fee", "other_income"]


@app.route('/api/save-income', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def save_income():
    """Collect one student's payment.

    Tuition: total = stored due; the fee checkboxes only choose payment categories and never add an
    amount. The paid amount goes to Monthly Salary
    (if ticked) up to the previous due only, then Exam Fee (if ticked) up to the exam
    fee, and the rest to Others. The selected month's column records the monthly amount, and
    total - paid becomes the student's due (negative = advance).
    Misc: kept separately in misc_due. Total = misc_due + items; the paid amount covers the items in
    order, the rest goes to Others, and total - paid becomes the new misc_due.
    Each save adds one DataSheet row; the data sheet page shows the totals per date.
    """
    data = request.get_json(silent=True) or {}

    branch = attendance_branch_for_current_user(data.get("branch"))
    class_ = (data.get("class") or "").strip()
    try:
        student_id = int(data.get("student_id"))
        month = int(data.get("month"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Please search a student and select a month"}), 400
    if branch is None or class_ not in CLASS_NAMES or not 1 <= month <= 12:
        return jsonify({"success": False, "error": "Please search a student and select a month"}), 400

    record = db.session.execute(db.select(AccountsRecord).where(
        AccountsRecord.branch == branch, AccountsRecord.class_name == class_,
        AccountsRecord.student_id == student_id)).scalars().first()
    if record is None:
        return jsonify({"success": False, "error": "Student not found"}), 404

    try:
        tuition_paid = read_amount(data, "tuition_paid")
        # Total Amount is editable on the income page; it may be negative (an advance)
        tuition_total = read_signed_amount(data, "tuition_total")
        # Due is editable too: when given, it is saved instead of total - paid (negative = advance)
        tuition_due = read_signed_amount(data, "tuition_due")
        misc_due = read_signed_amount(data, "misc_due")
        misc_paid = read_amount(data, "misc_paid")
        misc_items = {field: read_amount(data.get("misc") or {}, field) for field in MISC_FIELDS}
    except (TypeError, ValueError) as e:
        return jsonify({"success": False, "error": str(e)}), 400

    fixed_fee, fixed_exam_fee = db.session.execute(
        db.select(StudentRecord.fixed_fee, StudentRecord.fixed_exam_fee)
        .where(StudentRecord.branch == branch, StudentRecord.roll == str(student_id))).first() or (None, None)
    pay_monthly = bool(data.get("monthly")) and fixed_fee is not None
    pay_exam = bool(data.get("exam")) and fixed_exam_fee is not None
    pay_others = bool(data.get("others"))

    income = dict.fromkeys(INCOME_FIELDS, 0.0)
    response = {"success": True}
    # What this save may change on the accounts record, so cancelling it can put it back
    column = ACCOUNT_MONTHS[month - 1]
    undo = {"due": record.due, "due_month": record.due_month, "misc_due": record.misc_due,
            "column": column, "column_value": getattr(record, column)}

    # Tuition
    previous_due = money(record.due)
    # The fee checkboxes only choose the payment categories: no amount is added to the total. The
    # total is the stored due (negative = advance), unless the user edited Total Amount.
    total = previous_due if tuition_total is None else tuition_total
    tuition_used = tuition_paid > 0 or pay_monthly or pay_exam or pay_others or total != previous_due \
        or (tuition_due is not None and tuition_due != round(total - tuition_paid, 2))
    if tuition_used:
        rest = tuition_paid
        if pay_monthly:
            # The previous due is the monthly fee due, so only that much counts as monthly salary
            income["monthly_fee"], rest = take(rest, max(0.0, previous_due))
        if pay_exam:
            income["exam_fee"], rest = take(rest, fixed_exam_fee)
        income["other_income"] += rest

        if income["monthly_fee"] > 0:
            paid_before = getattr(record, column)
            setattr(record, column, money(paid_before) + income["monthly_fee"]
                    if isinstance(paid_before, (int, float)) else income["monthly_fee"])
        record.due = round(total - tuition_paid, 2) if tuition_due is None else tuition_due

    # Miscellaneous: its own due, separate from the monthly fee due
    misc_total_items = sum(misc_items.values())
    misc_used = misc_total_items > 0 or misc_paid > 0 \
        or (misc_due is not None and misc_due != round(money(record.misc_due) - misc_paid, 2))
    if misc_used:
        total = money(record.misc_due) + misc_total_items
        rest = misc_paid
        for field in MISC_FIELDS:
            taken, rest = take(rest, misc_items[field])
            income[field] += taken
        income["other_income"] += rest  # paying an earlier misc due, or in advance
        record.misc_due = round(total - misc_paid, 2) if misc_due is None else misc_due

    if not tuition_used and not misc_used:
        return jsonify({"success": False, "error": "Nothing to save, all amounts are empty"}), 400

    income = {field: round(amount, 2) for field, amount in income.items()}
    total_income = round(sum(income.values()), 2)
    if total_income > 0:
        row = DataSheet(
            date=today_in_dhaka(),
            branch=branch,
            **income,
            total_income=total_income,
            # Expenses are recorded from the expense page; the columns are NOT NULL
            daily_expense=0,
            all_rent_and_bills=0,
            staff_salary=0,
            other_expenses=0,
            total_expense=0,
        )
        db.session.add(row)
        db.session.flush()
        # Keep the branch's balance sheet in step with the new income
        refresh_balance_sheet(branch, row.date)

    payment = Payment(
        date=today_in_dhaka(), branch=branch, class_name=class_, student_id=student_id,
        student_name=record.student_name, month=month, collected_by=current_user.username,
        tuition_paid=tuition_paid, misc_paid=misc_paid, income=json.dumps(income), total_income=total_income,
        due_after=money(record.due), misc_due_after=money(record.misc_due), datasheet_id=row.id if total_income > 0 else None,
        # Also what the save left behind, so cancelling can tell whether the record was replaced since
        accounts_record_id=record.id,
        undo=json.dumps({**undo, "due_after": record.due, "misc_due_after": record.misc_due,
                         "column_after": getattr(record, column)}),
    )
    db.session.add(payment)
    db.session.commit()

    response.update({"income": income, "total_income": total_income, "due": record.due,
                     "misc_due": money(record.misc_due), "payment_id": payment.id})
    return jsonify(response)


# Expense categories of the expense page's checkboxes = DataSheet expense columns
EXPENSE_CATEGORIES = ["daily_expense", "all_rent_and_bills", "other_expenses"]


@app.route('/api/save-expense', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def save_expense():
    """Save the expense page's total (all rows added up) as one DataSheet row for today, in the
    column of the ticked category."""
    data = request.get_json(silent=True) or {}
    branch = attendance_branch_for_current_user(data.get("branch"))
    if branch is None:
        return jsonify({"success": False, "error": "Please select a branch"}), 400
    category = data.get("category")
    if category not in EXPENSE_CATEGORIES:
        return jsonify({"success": False, "error": "Please tick one expense type"}), 400
    try:
        amount = read_amount(data, "amount")
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    if amount <= 0:
        return jsonify({"success": False, "error": "The total amount must be more than 0"}), 400

    expenses = dict.fromkeys(EXPENSE_CATEGORIES + ["staff_salary"], 0.0)
    expenses[category] = amount
    row = DataSheet(date=today_in_dhaka(), branch=branch, **dict.fromkeys(INCOME_FIELDS, 0.0),
                    total_income=0.0, **expenses, total_expense=amount)
    db.session.add(row)
    db.session.flush()
    # Keep the branch's balance sheet in step with the new expense
    refresh_balance_sheet(branch, row.date)
    db.session.commit()
    return jsonify({"success": True, "branch": branch, "category": category, "amount": amount})


def latest_active_payment(branch, class_, student_id):
    return db.session.execute(
        db.select(Payment).where(Payment.branch == branch, Payment.class_name == class_,
                                 Payment.student_id == student_id, Payment.cancelled_at.is_(None))
        .order_by(Payment.id.desc()).limit(1)).scalars().first()


def serialize_payment(payment, latest_id):
    return {
        "id": payment.id,
        "date": payment.date.isoformat(),
        "time": payment.created_at.strftime("%H:%M") if payment.created_at else "",
        "month": payment.month,
        "collected_by": payment.collected_by,
        "tuition_paid": payment.tuition_paid,
        "misc_paid": payment.misc_paid,
        "income": json.loads(payment.income),
        "total_income": payment.total_income,
        "due_after": payment.due_after,
        "misc_due_after": payment.misc_due_after,
        "cancelled": payment.cancelled_at is not None,
        "cancelled_by": payment.cancelled_by,
        # Only the latest active payment can be cancelled: later saves were worked out on top of it
        "can_cancel": payment.id == latest_id,
    }


@app.route('/api/student-payments', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def student_payments():
    data = request.get_json(silent=True) or {}
    branch = attendance_branch_for_current_user(data.get("branch"))
    class_ = (data.get("class") or "").strip()
    try:
        student_id = int(data.get("student_id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid ID", "data": []}), 400
    if branch is None or class_ not in CLASS_NAMES:
        return jsonify({"success": False, "error": "Please select a valid branch and class", "data": []}), 400

    payments = db.session.execute(
        db.select(Payment).where(Payment.branch == branch, Payment.class_name == class_,
                                 Payment.student_id == student_id)
        .order_by(Payment.id.desc())).scalars().all()
    latest = latest_active_payment(branch, class_, student_id)
    latest_id = latest.id if latest else None
    return jsonify({"success": True, "data": [serialize_payment(p, latest_id) for p in payments]})


@app.route('/api/cancel-payment/<int:id>', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def cancel_payment(id):
    """Undo a mistaken save: remove its data sheet row and put the student's due and month back."""
    payment = db.session.get(Payment, id)
    if payment is None or (current_user.role != ADMIN_ROLE and payment.branch != current_user.branch.name):
        return jsonify({"success": False, "error": "Payment not found"}), 404
    if payment.cancelled_at is not None:
        return jsonify({"success": False, "error": "This payment is already cancelled"}), 409
    latest = latest_active_payment(payment.branch, payment.class_name, payment.student_id)
    if latest.id != payment.id:
        return jsonify({"success": False,
                        "error": "Only the latest payment of this student can be cancelled. Cancel the later ones first."}), 409

    if payment.datasheet_id:
        row = db.session.get(DataSheet, payment.datasheet_id)
        if row is not None:
            day, row_branch = row.date, row.branch or payment.branch
            db.session.delete(row)
            db.session.flush()
            refresh_balance_sheet(row_branch, day)

    # If the class was uploaded again since, the record is gone or replaced (an upload may even reuse
    # the id); then only the income is undone. It is unchanged only if it still shows what this save left.
    undo = json.loads(payment.undo)
    record = db.session.get(AccountsRecord, payment.accounts_record_id) if payment.accounts_record_id else None
    restored = (record is not None and record.student_id == payment.student_id
                and record.due == undo.get("due_after")
                and record.misc_due == undo.get("misc_due_after", record.misc_due)
                and getattr(record, undo["column"]) == undo.get("column_after"))
    if restored:
        record.due = undo["due"]
        record.due_month = undo["due_month"]
        if "misc_due" in undo:  # saves made before misc dues were kept apart do not have it
            record.misc_due = undo["misc_due"]
        setattr(record, undo["column"], undo["column_value"])

    payment.cancelled_at = datetime.now(ZoneInfo("Asia/Dhaka"))
    payment.cancelled_by = current_user.username
    db.session.commit()
    return jsonify({"success": True, "accounts_restored": restored})


def today_in_dhaka():
    return datetime.now(ZoneInfo("Asia/Dhaka")).date()


def refresh_balance_sheet(branch, day):
    """Make sure `branch` has a BalanceSheet row for `day`, then recalculate it and every later row
    of that branch.

    Each row's total_income / total_expense are the sums of that branch's DataSheet rows for the day,
    and balance = the branch's previous balance + income - expense + deposit - withdraw.
    Does not commit; the caller does.
    """
    row = db.session.execute(
        db.select(BalanceSheet).where(BalanceSheet.branch == branch, BalanceSheet.date == day)
    ).scalars().first()
    if row is None:
        db.session.add(BalanceSheet(date=day, branch=branch, total_income=0, total_expense=0, deposit=0,
                                    deposit_description="", withdraw=0,
                                    withdraw_description="", balance=0))
        db.session.flush()

    previous = db.session.execute(
        db.select(BalanceSheet.balance)
        .where(BalanceSheet.branch == branch, BalanceSheet.date < day)
        .order_by(BalanceSheet.date.desc())
        .limit(1)
    ).scalar()
    balance = previous or 0

    daily_totals = dict(
        (row_date, (income or 0, expense or 0))
        for row_date, income, expense in db.session.execute(
            db.select(DataSheet.date, func.sum(DataSheet.total_income), func.sum(DataSheet.total_expense))
            .where(DataSheet.branch == branch, DataSheet.date >= day)
            .group_by(DataSheet.date)
        ).all()
    )

    later_rows = db.session.execute(
        db.select(BalanceSheet).where(BalanceSheet.branch == branch, BalanceSheet.date >= day)
        .order_by(BalanceSheet.date)
    ).scalars().all()

    for row in later_rows:
        row.total_income, row.total_expense = daily_totals.get(row.date, (0, 0))
        balance += row.total_income - row.total_expense + (row.deposit or 0) - (row.withdraw or 0)
        row.balance = round(balance, 2)


def sheet_branch_for_current_user(requested_branch):
    """Which branch the data sheet / balance sheet shows: (ok, branch).

    A Service Admin always gets their own branch. An Admin gets the branch they picked, or None
    (all branches together) for "" / "all"; ok is False for a branch that does not exist.
    """
    if current_user.role != ADMIN_ROLE:
        return True, current_user.branch.name
    requested_branch = (requested_branch or "").strip()
    if requested_branch in ("", "all"):
        return True, None
    branch = attendance_branch_for_current_user(requested_branch)
    return branch is not None, branch


@app.route('/api/save-balance', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def save_balance():
    data = request.get_json(silent=True) or {}
    branch = attendance_branch_for_current_user(data.get("branch"))
    if branch is None:
        return jsonify({"success": False, "error": "Please select a branch"}), 400

    try:
        day = date.fromisoformat(data.get("date")) if data.get("date") else today_in_dhaka()
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid date"}), 400
    if day > today_in_dhaka():
        return jsonify({"success": False, "error": "Date cannot be in the future"}), 400

    amounts = {}
    for field in ("deposit", "withdraw"):
        try:
            amount = float(data.get(field) or 0)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": f"Invalid amount for {field}"}), 400
        if amount < 0:
            return jsonify({"success": False, "error": f"{field} cannot be negative"}), 400
        amounts[field] = amount

    if amounts["deposit"] == 0 and amounts["withdraw"] == 0:
        return jsonify({"success": False, "error": "Enter a deposit or a withdraw amount"}), 400

    refresh_balance_sheet(branch, day)  # creates the day's row if it is missing
    row = db.session.execute(
        db.select(BalanceSheet).where(BalanceSheet.branch == branch, BalanceSheet.date == day)
    ).scalars().first()

    # Several entries on the same day add up; their descriptions are kept side by side
    for field in ("deposit", "withdraw"):
        if amounts[field] == 0:
            continue
        setattr(row, field, (getattr(row, field) or 0) + amounts[field])
        description = (data.get(f"{field}_description") or "").strip()
        if description:
            old = getattr(row, f"{field}_description") or ""
            setattr(row, f"{field}_description", f"{old}; {description}" if old else description)

    refresh_balance_sheet(branch, day)  # recalculate with the new amounts
    db.session.commit()

    return jsonify({"success": True, "branch": branch, "date": row.date.isoformat(), "balance": row.balance})


@app.route('/api/search-balance-sheet', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def search_balance_sheet():
    """One branch's balance sheet, or (Admin only) every branch added up day by day."""
    data = request.get_json(silent=True) or {}
    ok, branch = sheet_branch_for_current_user(data.get("branch"))
    if not ok:
        return jsonify({"success": False, "error": "Please select a valid branch"}), 400

    try:
        start = date.fromisoformat(data.get("from"))
        end = date.fromisoformat(data.get("to"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Please choose a valid date range"}), 400

    if start > end:
        return jsonify({"success": False, "error": "From date must be before To date"}), 400

    stmt = db.select(BalanceSheet).where(BalanceSheet.date <= end)
    if branch is not None:
        stmt = stmt.where(BalanceSheet.branch == branch)
    rows = db.session.execute(stmt.order_by(BalanceSheet.date, BalanceSheet.id)).scalars().all()

    # Each branch's latest balance so far; the balance shown is their sum (one branch: just its own)
    latest = {}
    per_day = {}
    for row in rows:
        if row.date >= start:
            per_day.setdefault(row.date, []).append(row)
        else:
            latest[row.branch] = row.balance or 0

    results = []
    for day_date in sorted(per_day):
        totals = dict.fromkeys(("total_income", "total_expense", "deposit", "withdraw"), 0.0)
        descriptions = {"deposit_description": [], "withdraw_description": []}
        for row in per_day[day_date]:
            latest[row.branch] = row.balance or 0
            for field in totals:
                totals[field] += getattr(row, field) or 0
            for field, texts in descriptions.items():
                text = getattr(row, field) or ""
                if text:
                    # With all branches together, say which branch each entry belongs to
                    texts.append(f"{row.branch}: {text}" if branch is None else text)
        results.append({
            "date": day_date.isoformat(),
            **{field: round(value, 2) for field, value in totals.items()},
            **{field: "; ".join(texts) for field, texts in descriptions.items()},
            "balance": round(sum(latest.values()), 2),
        })

    return jsonify({"success": True, "branch": branch, "data": results})


DATASHEET_FIELDS = INCOME_FIELDS + ["total_income", "daily_expense", "all_rent_and_bills",
                                    "staff_salary", "other_expenses", "total_expense"]


@app.route('/api/search-datasheet', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def search_datasheet():
    """One branch's data sheet, or (Admin only) every branch added up per date."""
    data = request.get_json(silent=True) or {}
    ok, branch = sheet_branch_for_current_user(data.get("branch"))
    if not ok:
        return jsonify({"success": False, "error": "Please select a valid branch"}), 400

    try:
        start = date.fromisoformat(data.get("from"))
        end = date.fromisoformat(data.get("to"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Please choose a valid date range"}), 400

    if start > end:
        return jsonify({"success": False, "error": "From date must be before To date"}), 400

    stmt = db.select(DataSheet).where(DataSheet.date.between(start, end))
    if branch is not None:
        stmt = stmt.where(DataSheet.branch == branch)
    records = db.session.execute(stmt.order_by(DataSheet.date, DataSheet.id)).scalars().all()

    # Every save is its own row in the database; the page shows one row per date with the day's totals
    per_day = {}
    for record in records:
        day = per_day.setdefault(record.date, dict.fromkeys(DATASHEET_FIELDS, 0))
        for field in DATASHEET_FIELDS:
            day[field] += getattr(record, field) or 0
    results = [{"date": day.isoformat(), **{field: round(value, 2) for field, value in totals.items()}}
               for day, totals in per_day.items()]

    return jsonify({"success": True, "branch": branch, "data": results})


# Result sheets: database field -> accepted Excel headers (matched ignoring case/spaces).
# Missing subject columns are fine (lower classes have fewer subjects); they stay empty.
SEMESTER_FIELDS = {
    "merit": ["Merit"],
    "arabic": ["Arabic"],
    "quran": ["Quran"],
    "bengali": ["Bengali"],
    "english": ["English"],
    "math": ["Math"],
    "science": ["Science"],
    "bgs": ["BGS"],
    "aqaid_and_fiqh": ["Aqaid & Fiqh", "Aqaid and Fiqh"],
    "class_test": ["Class Assessment", "Class Test"],
    "presence": ["Attendance", "Presence"],
    "total": ["Total"],
    "letter_grade": ["Letter Grade", "Grade"],
}
CLASS_TEST_FIELDS = {
    "arabic": ["Arabic"],
    "quran": ["Quran"],
    "bengali": ["Bengali"],
    "english": ["English"],
    "math": ["Math"],
    "science": ["Science"],
    "aqaid_and_fiqh": ["Aqaid & Fiqh", "Aqaid and Fiqh"],
    "bgs": ["BGS"],
    "total": ["Total"],
}
TEXT_RESULT_FIELDS = {"letter_grade"}
INTEGER_RESULT_FIELDS = {"merit"}


def valid_exam_name(exam):
    """'1st Semester Assessment 2026' style."""
    parts = (exam or "").rsplit(" ", 1)
    return len(parts) == 2 and parts[0] in EXAM_TYPES and parts[1].isdigit()


def result_cell(value, field, excel_row, header):
    """Excel cell -> stored value. Blank/'-' -> None; marks may use Bengali digits."""
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return None
    if field in TEXT_RESULT_FIELDS:
        return str(value).strip() or None
    text = str(value).strip().translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789"))
    if text in ("", "-"):
        return None
    try:
        number = float(text)
    except ValueError:
        raise ValueError(f"Row {excel_row}, column '{header}': '{value}' is not a number.")
    return int(number) if field in INTEGER_RESULT_FIELDS else round(number, 2)


def read_result_sheet(file, fields, model, fixed_values):
    """Parse an uploaded result sheet into model rows (nothing is saved here)."""
    if not file or file.filename == "":
        raise ValueError("No file uploaded")
    if not file.filename.lower().endswith(".xlsx"):
        raise ValueError("Only .xlsx Excel files are supported. In Excel use Save As → .xlsx")

    df = pd.read_excel(file)
    headers = {" ".join(str(c).split()).lower(): c for c in df.columns}

    missing = [name for name in ("ID", "Student Name", "Total") if name.lower() not in headers]
    if missing:
        raise ValueError(f"Excel file is missing column(s): {', '.join(missing)}")

    field_columns = {}
    for field, names in fields.items():
        for name in names:
            if name.lower() in headers:
                field_columns[field] = headers[name.lower()]
                break

    records = []
    for excel_row, row in enumerate(df.itertuples(index=False), start=2):
        row = dict(zip(df.columns, row))
        raw_id = row[headers["id"]]
        if raw_id is None or pd.isna(raw_id):
            continue  # blank line in the sheet
        try:
            student_id = int(float(raw_id))
        except (TypeError, ValueError):
            raise ValueError(f"Row {excel_row}: ID '{raw_id}' is not a number.")

        name = row[headers["student name"]]
        record = model(**fixed_values, student_id=student_id,
                       student_name=helpers.convert_bangla_text("" if name is None or pd.isna(name) else str(name)))
        for field, column in field_columns.items():
            setattr(record, field, result_cell(row[column], field, excel_row, column))
        records.append(record)

    if not records:
        raise ValueError("Excel file has no student rows.")
    return records


def result_upload_target(period_ok, period_error):
    """Common checks for both result uploads. Returns (branch, class_name)."""
    if not can_open_results():
        abort(403)
    branch = attendance_branch_for_current_user(request.form.get("branch_name"))
    class_ = (request.form.get("class_name") or "").strip()
    if branch is None:
        raise ValueError("অনুগ্রহ করে সঠিক ব্রাঞ্চ নির্বাচন করুন।")
    if class_ not in CLASS_NAMES:
        raise ValueError("অনুগ্রহ করে সঠিক শ্রেণী নির্বাচন করুন।")
    if not period_ok:
        raise ValueError(period_error)
    return branch, class_


def result_search_target(data):
    """Returns (branch, class_name, student_id) the current user may search."""
    if current_user.role == STUDENT_ROLE:
        # Students only ever see their own result
        return current_user.branch.name, class_from_school_id(current_user.school_id), current_user.school_id
    if not can_open_results():
        abort(403)
    return (attendance_branch_for_current_user(data.get("branch")),
            (data.get("class") or "").strip(), data.get("student_id"))


def result_value_for_display(value, field):
    if isinstance(value, float) and value != value:  # NaN is not valid JSON
        return None
    if field in TEXT_RESULT_FIELDS:
        # Letter grades are plain English ("A+"); the Bijoy converter would turn "A" into "অ"
        return value
    return account_value_for_display(value)


def search_results(model, period_column, period, fields, order_by):
    data = request.get_json(silent=True) or {}
    branch, class_, student_id = result_search_target(data)

    if branch is None or class_ not in CLASS_NAMES or not period:
        return jsonify({"success": False, "error": "Please select a valid branch, class and exam/month",
                        "data": []}), 400

    stmt = db.select(model).where(model.branch == branch, model.class_name == class_, period_column == period)
    if student_id:
        try:
            stmt = stmt.where(model.student_id == int(student_id))
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Invalid ID", "data": []}), 400

    results = []
    for record in db.session.execute(stmt.order_by(*order_by)).scalars().all():
        row = {"ID": record.student_id, "student_name": record.student_name}
        for field in fields:
            row[field] = result_value_for_display(getattr(record, field), field)
        results.append(row)

    return jsonify({"success": True, "data": results})


@app.route('/api/upload-semester-result', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_semester_result():
    try:
        exam = " ".join((request.form.get("exam_name") or "").split())
        branch, class_ = result_upload_target(valid_exam_name(exam), "অনুগ্রহ করে সঠিক পরীক্ষা নির্বাচন করুন।")
        records = read_result_sheet(request.files.get("excel_file"), SEMESTER_FIELDS, SemesterResultRecord,
                                    {"branch": branch, "class_name": class_, "exam_name": exam})

        # Replace the previous upload only once the new file has been read successfully
        db.session.query(SemesterResultRecord).filter_by(branch=branch, class_name=class_, exam_name=exam).delete()
        db.session.add_all(records)
        db.session.commit()
        flash(tr(f"Semester assessment result uploaded successfully ({len(records)} students).",
                 f"সাময়িক মূল্যায়নের ফলাফল সফলভাবে আপলোড হয়েছে ({len(records)} জন শিক্ষার্থী)।"), "success")
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
    return redirect(url_for("semester_assessment"))


@app.route('/api/search-semester-result', methods=['POST'])
@login_required
def search_semester_result():
    exam = " ".join(((request.get_json(silent=True) or {}).get("exam") or "").split())
    return search_results(SemesterResultRecord, SemesterResultRecord.exam_name,
                          exam if valid_exam_name(exam) else None, SEMESTER_FIELDS,
                          # Merit order first; students without a merit position go last
                          [SemesterResultRecord.merit.is_(None), SemesterResultRecord.merit,
                           SemesterResultRecord.student_id])


@app.route('/api/upload-class-result', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_class_result():
    try:
        month = (request.form.get("month_name") or "").strip()
        branch, class_ = result_upload_target(valid_attendance_month(month), "অনুগ্রহ করে সঠিক মাস নির্বাচন করুন।")
        records = read_result_sheet(request.files.get("excel_file"), CLASS_TEST_FIELDS, ClassTestResultRecord,
                                    {"branch": branch, "class_name": class_, "month": month})

        db.session.query(ClassTestResultRecord).filter_by(branch=branch, class_name=class_, month=month).delete()
        db.session.add_all(records)
        db.session.commit()
        flash(tr(f"Class assessment result uploaded successfully ({len(records)} students).",
                 f"শ্রেণী মূল্যায়নের ফলাফল সফলভাবে আপলোড হয়েছে ({len(records)} জন শিক্ষার্থী)।"), "success")
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
    return redirect(url_for("class_assessment"))


@app.route('/api/search-class-result', methods=['POST'])
@login_required
def search_class_result():
    month = ((request.get_json(silent=True) or {}).get("month") or "").strip()
    return search_results(ClassTestResultRecord, ClassTestResultRecord.month,
                          month if valid_attendance_month(month) else None, CLASS_TEST_FIELDS,
                          [ClassTestResultRecord.student_id])


NOTICE_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")
NOTICE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
NOTICE_NAME = re.compile(r"^(\d{2})-(\d{2})-(\d{4}) (\d{2})-(\d{2})-(\d{2})")


def notice_image_type(head):
    """The real image type from the file's first bytes (the file name can lie); None if not an image."""
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if head.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    if head[:2] == b"BM":
        return ".bmp"
    return None


def list_notices(branch):
    """A branch's notices, newest first, with the date they were posted."""
    if not branch:
        return []
    folder = os.path.join(NOTICES_DIR, branch)
    os.makedirs(folder, exist_ok=True)  # e.g. a branch that was just created
    notices = []
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if not (os.path.isfile(path) and name.lower().endswith(NOTICE_IMAGE_EXTENSIONS)):
            continue
        match = NOTICE_NAME.match(name)
        if match:
            d, mo, y, h, mi, se = map(int, match.groups())
            posted = datetime(y, mo, d, h, mi, se)
        else:
            posted = datetime.fromtimestamp(os.path.getmtime(path))
        notices.append({"url": url_for("static", filename=f"img/notices/{branch}/{name}"),
                        "posted": posted, "date": posted.strftime("%d-%m-%Y %I:%M %p")})
    notices.sort(key=lambda n: n["posted"], reverse=True)
    return notices


def notice_branch_for_current_user(requested_branch):
    """The branch a notice action may touch: a Service Admin only their own, an Admin any existing branch."""
    if current_user.role == SERVICE_ADMIN_ROLE:
        return current_user.branch.name
    exists = db.session.execute(
        db.select(Branch.id).where(Branch.name == (requested_branch or "").strip()).limit(1)
    ).first()
    return requested_branch.strip() if exists else None


@app.route('/api/upload-notice', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_notice():
    if not can_open_notices():
        abort(403)

    branch = notice_branch_for_current_user(request.form.get("branch_name"))
    try:
        # Never trust the branch name as a folder path; it must be a real branch
        if branch is None:
            raise ValueError("Please select a valid branch.")

        img = request.files.get("img")
        if not img or not img.filename:
            raise ValueError("Please choose a notice image.")

        data = img.read(NOTICE_MAX_BYTES + 1)
        if len(data) > NOTICE_MAX_BYTES:
            raise ValueError(f"Image is too large. Maximum size is {NOTICE_MAX_BYTES // (1024 * 1024)} MB.")
        extension = notice_image_type(data[:16])
        if extension is None:
            raise ValueError("Only image files (PNG, JPG, GIF, WEBP, BMP) can be uploaded as notices. "
                             "For a PDF, take a screenshot or export it as an image.")

        branch_folder = os.path.join(NOTICES_DIR, branch)
        os.makedirs(branch_folder, exist_ok=True)
        stamp = datetime.now(ZoneInfo("Asia/Dhaka")).strftime("%d-%m-%Y %H-%M-%S")
        # Two uploads in the same second must not overwrite each other
        name, n = f"{stamp}{extension}", 2
        while os.path.exists(os.path.join(branch_folder, name)):
            name, n = f"{stamp} ({n}){extension}", n + 1
        with open(os.path.join(branch_folder, name), "wb") as out:
            out.write(data)
        flash(tr(f"Notice uploaded to {branch}.", f"{branch} ব্রাঞ্চে নোটিশ আপলোড হয়েছে।"), "success")
    except Exception as e:
        flash(str(e), "danger")

    if current_user.role == ADMIN_ROLE and branch:
        return redirect(url_for("notice_board_management", branch=branch))
    return redirect(url_for("notice_board_management"))


@app.route("/api/search-log-info", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def search_login_info():
    try:
        day = date.fromisoformat(str((request.get_json(silent=True) or {}).get("date") or ""))
    except ValueError:
        return jsonify({"success": False, "error": "Please select a valid date", "data": []}), 400

    start = datetime.combine(day, datetime.min.time())
    rows = db.session.execute(
        db.select(LogInfo, User.role, Branch.name)
        .outerjoin(User, User.username == LogInfo.username)
        .outerjoin(Branch, Branch.id == User.branch_id)
        .where(LogInfo.login_time >= start, LogInfo.login_time < start + timedelta(days=1))
        .order_by(LogInfo.login_time.desc())
    ).all()

    return jsonify({"success": True, "data": [{
        "username": log.username,
        "role": role or "—",          # "—" when the user has since been deleted
        "branch": branch or "—",
        "login_time": log.login_time.strftime("%I:%M %p"),
    } for log, role, branch in rows]})


@app.route("/api/search-comments", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def search_comments():
    if not can_manage_comments():
        abort(403)

    data = request.get_json(silent=True) or {}
    stmt = managed_comments_query()

    # No date = all comments
    if data.get("date"):
        try:
            selected_date = date.fromisoformat(data["date"])
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "Invalid date", "data": []}), 400
        start = datetime.combine(selected_date, datetime.min.time())
        stmt = stmt.where(Comment.comment_time >= start, Comment.comment_time < start + timedelta(days=1))

    comments = db.session.execute(stmt.order_by(Comment.comment_time.desc())).scalars().all()

    return jsonify({"success": True, "data": [serialize_comment(c) for c in comments]})


@app.route('/api/upload-phone-number', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_phone_number():
    branch_name = phone_branch_for_current_user(request.form.get("branch_name"))
    name, phone, error = validate_phone_form()

    if branch_name is None:
        flash(tr("Please select a valid branch.", "অনুগ্রহ করে সঠিক ব্রাঞ্চ নির্বাচন করুন।"), "danger")
    elif error:
        flash(error, "danger")
    else:
        try:
            db.session.add(PhoneNumber(branch_name=branch_name, name=name, phone_number=phone))
            db.session.commit()
            flash(tr("Phone number added.", "ফোন নাম্বার যোগ করা হয়েছে।"), "success")
        except Exception as e:
            db.session.rollback()
            flash(str(e), "danger")

    return redirect(url_for("call_services"))


def editable_phone_number(phone_id):
    """The PhoneNumber row if the current user may change it, else None."""
    phone_number = db.session.get(PhoneNumber, phone_id)
    if phone_number is None:
        return None
    if current_user.role == SERVICE_ADMIN_ROLE and phone_number.branch_name != current_user.branch.name:
        return None
    return phone_number


@app.route('/api/update-phone-number/<int:phone_id>', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def update_phone_number(phone_id):
    phone_number = editable_phone_number(phone_id)
    branch_name = phone_branch_for_current_user(request.form.get("branch_name"))
    name, phone, error = validate_phone_form()

    if phone_number is None:
        flash(tr("Phone number not found.", "ফোন নাম্বারটি পাওয়া যায়নি।"), "danger")
    elif branch_name is None:
        flash(tr("Please select a valid branch.", "অনুগ্রহ করে সঠিক ব্রাঞ্চ নির্বাচন করুন।"), "danger")
    elif error:
        flash(error, "danger")
    else:
        phone_number.branch_name = branch_name
        phone_number.name = name
        phone_number.phone_number = phone
        db.session.commit()
        flash(tr("Phone number updated.", "ফোন নাম্বার আপডেট করা হয়েছে।"), "success")

    return redirect(url_for("call_services"))


@app.route('/api/delete-phone-number/<int:phone_id>', methods=['DELETE'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def delete_phone_number(phone_id):
    phone_number = editable_phone_number(phone_id)
    if phone_number is None:
        return jsonify({"success": False, "error": "Phone number not found"}), 404

    db.session.delete(phone_number)
    db.session.commit()
    return jsonify({"success": True})


@app.route('/api/upload-comment', methods=['POST'])
@login_required
def upload_comment():
    comment = (request.form.get("comment") or "").strip()

    if not comment:
        flash(tr("Please write a comment.", "অনুগ্রহ করে মন্তব্য লিখুন।"), "danger")
    elif len(comment) > MAX_COMMENT_LENGTH:
        flash(tr(f"A comment can be at most {MAX_COMMENT_LENGTH} characters.",
                 f"মন্তব্য সর্বোচ্চ {MAX_COMMENT_LENGTH} অক্ষরের হতে পারে।"), "danger")
    else:
        try:
            # Always the logged-in user; never trust a username sent by the form
            db.session.add(Comment(username=current_user.username, comment=comment))
            db.session.commit()
            flash(tr("Comment submitted successfully.", "মন্তব্য সফলভাবে জমা হয়েছে।"), "success")
        except Exception as e:
            db.session.rollback()
            flash(str(e), "danger")

    return redirect(url_for("student_comment"))


@app.route("/api/reply-comment", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def reply_comment():
    if not can_manage_comments():
        abort(403)

    reply_txt = (request.form.get("comment_reply") or "").strip()
    try:
        comment_id = int(request.form.get("comment_db_id") or 0)
    except ValueError:
        comment_id = 0

    # Must be a comment this user is allowed to see
    comment = db.session.execute(
        managed_comments_query().where(Comment.id == comment_id)
    ).scalars().first()

    if comment is None:
        flash(tr("Comment not found.", "মন্তব্যটি পাওয়া যায়নি।"), "danger")
    elif not reply_txt:
        flash(tr("Please write a reply.", "অনুগ্রহ করে উত্তর লিখুন।"), "danger")
    elif len(reply_txt) > MAX_COMMENT_LENGTH:
        flash(tr(f"A reply can be at most {MAX_COMMENT_LENGTH} characters.",
                 f"উত্তর সর্বোচ্চ {MAX_COMMENT_LENGTH} অক্ষরের হতে পারে।"), "danger")
    else:
        try:
            # One reply per comment: replying again edits the existing reply
            if comment.reply:
                comment.reply.reply_txt = reply_txt
                comment.reply.replier = current_user.username
                comment.reply.reply_time = datetime.now(ZoneInfo("Asia/Dhaka"))
            else:
                db.session.add(CommentReply(replier=current_user.username, comment_id=comment.id,
                                            reply_txt=reply_txt))
            db.session.commit()
            flash(tr("Reply sent.", "উত্তর পাঠানো হয়েছে।"), "success")
        except Exception as e:
            db.session.rollback()
            flash(str(e), "danger")

    return redirect(url_for("submitted_comments"))


@app.route("/api/delete_notice", methods=["DELETE"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def delete_notice():
    if not can_open_notices():
        return jsonify({"success": False, "error": "You do not have access to notices."}), 403
    notice_url = unquote((request.get_json(silent=True) or {}).get("notice_path") or "")
    # "/static/img/notices/Branch%20Name/file.png" -> <NOTICES_DIR>/Branch Name/file.png
    prefix = url_for("static", filename="img/notices/")
    if not notice_url.startswith(prefix):
        return jsonify({"success": False, "error": "Invalid notice"}), 400
    notice_path = os.path.realpath(os.path.join(NOTICES_DIR, notice_url[len(prefix):]))

    # Only files directly inside a branch's notices folder may be deleted
    notices_root = os.path.realpath(NOTICES_DIR)
    branch_folder = os.path.dirname(notice_path)
    if os.path.dirname(branch_folder) != notices_root \
            or not notice_path.lower().endswith(NOTICE_IMAGE_EXTENSIONS):
        return jsonify({"success": False, "error": "Invalid notice"}), 400

    # A Service Admin may only delete their own branch's notices
    if notice_branch_for_current_user(os.path.basename(branch_folder)) != os.path.basename(branch_folder):
        return jsonify({"success": False, "error": "You cannot delete another branch's notice"}), 403

    if not os.path.isfile(notice_path):
        return jsonify({"success": False, "error": "Notice not found"}), 404

    os.remove(notice_path)
    return jsonify({"success": True})


BRANCH_NAME_TABLES = [  # tables that store the branch by name rather than by id
    (AttendanceRecord, AttendanceRecord.branch),
    (AccountsRecord, AccountsRecord.branch),
    (SemesterResultRecord, SemesterResultRecord.branch),
    (ClassTestResultRecord, ClassTestResultRecord.branch),
    (Notice, Notice.branch),
    (PhoneNumber, PhoneNumber.branch_name),
    (StudentRecord, StudentRecord.branch),
    (TeacherRecord, TeacherRecord.branch),
]


def validate_branch_form(data, branch_id=None):
    """Clean branch fields -> (fields, None) or (None, error). Names and codes must be unique."""
    fields = {
        "code": (data.get("code") or "").strip().upper(),
        "name": " ".join((data.get("name") or "").split()),
        "director": " ".join((data.get("director") or "").split()),
        "phone": normalize_phone(data.get("phone")),
    }
    if not all(fields.values()):
        return None, "অনুগ্রহ করে সকল তথ্য পূরণ করুন।"
    # The name is also a folder name for the branch's notices
    if any(ch in fields["name"] for ch in '/\\:*?"<>|') or fields["name"].strip(".") == "":
        return None, "শাখার নামে / \\ : * ? \" < > | চিহ্ন ব্যবহার করা যাবে না।"
    if len(fields["phone"].lstrip("+")) < 6:
        return None, "সঠিক ফোন নম্বর দিন।"

    for column, label in ((Branch.name, "নামে"), (Branch.code, "কোডে")):
        value = fields["name"] if column is Branch.name else fields["code"]
        clash = db.session.execute(
            db.select(Branch.id).where(func.lower(column) == value.lower(), Branch.id != (branch_id or 0)).limit(1)
        ).first()
        if clash:
            return None, f"এই {label} আরেকটি শাখা আছে: {value}"
    return fields, None


@app.route("/api/add-branch", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def add_branch():
    data = request.get_json(silent=True) or {}
    fields, error = validate_branch_form({"code": data.get("code"), "name": data.get("branch"),
                                          "director": data.get("director"), "phone": data.get("phone")})
    if error:
        return jsonify({"success": False, "error": error}), 400

    branch = Branch(**fields)
    db.session.add(branch)
    db.session.commit()
    # Folder for the branch's notices; it may already exist if a branch with this name was deleted earlier
    os.makedirs(os.path.join(NOTICES_DIR, branch.name), exist_ok=True)
    return jsonify({"success": True})


@app.route("/api/update-branch", methods=["PATCH"])
@login_required
@roles_required(ADMIN_ROLE)
def update_branch():
    data = request.get_json(silent=True) or {}
    try:
        branch = db.session.get(Branch, int(data.get("branch_id")))
    except (TypeError, ValueError):
        branch = None
    if branch is None:
        return jsonify({"success": False, "error": "Branch not found"}), 404

    fields, error = validate_branch_form({"code": data.get("new_code"), "name": data.get("new_branch_name"),
                                          "director": data.get("new_director_name"), "phone": data.get("new_phone")},
                                         branch_id=branch.id)
    if error:
        return jsonify({"success": False, "error": error}), 400

    old_name, new_name = branch.name, fields["name"]
    try:
        for key, value in fields.items():
            setattr(branch, key, value)
        if new_name != old_name:
            # Records point to the branch by its name, so carry the new name everywhere
            for model, column in BRANCH_NAME_TABLES:
                db.session.execute(db.update(model).where(column == old_name).values({column.key: new_name}))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

    if new_name != old_name:
        move_notice_folder(old_name, new_name)
    return jsonify({"success": True})


def move_notice_folder(old_name, new_name):
    """Keep the branch's uploaded notices after a rename (merged if the new folder already exists)."""
    old_folder, new_folder = os.path.join(NOTICES_DIR, old_name), os.path.join(NOTICES_DIR, new_name)
    try:
        if not os.path.isdir(old_folder):
            os.makedirs(new_folder, exist_ok=True)
        elif not os.path.exists(new_folder) or old_name.lower() == new_name.lower():
            os.rename(old_folder, new_folder)  # also handles a change of letter case on Windows
        else:
            for name in os.listdir(old_folder):
                target = os.path.join(new_folder, name)
                if not os.path.exists(target):
                    os.rename(os.path.join(old_folder, name), target)
            if not os.listdir(old_folder):
                os.rmdir(old_folder)
    except OSError as e:
        app.logger.warning("Could not move notices from %s to %s: %s", old_folder, new_folder, e)


@app.route("/api/delete-branch/<int:id>", methods=["DELETE"])
@login_required
@roles_required(ADMIN_ROLE)
def delete_branch(id):
    branch = db.session.get(Branch, id)
    if branch is None:
        return jsonify({"success": False, "error": "Branch not found"}), 404

    # Users must belong to a branch (users.branch_id is NOT NULL), and students are
    # linked to the branch by name, so refuse instead of breaking or orphaning them.
    user_count = db.session.execute(
        db.select(func.count()).select_from(User).where(User.branch_id == branch.id)
    ).scalar()
    student_count = db.session.execute(
        db.select(func.count()).select_from(StudentRecord).where(StudentRecord.branch == branch.name)
    ).scalar()
    teacher_count = db.session.execute(
        db.select(func.count()).select_from(TeacherRecord).where(TeacherRecord.branch == branch.name)
    ).scalar()
    if user_count or student_count or teacher_count:
        return jsonify({
            "success": False,
            "error": f"এই ব্রাঞ্চে এখনও {user_count} জন ইউজার, {student_count} জন শিক্ষার্থী এবং "
                     f"{teacher_count} জন শিক্ষক আছে। মুছে ফেলার আগে তাদের অন্য ব্রাঞ্চে সরান বা মুছে ফেলুন।"
        }), 409

    try:
        db.session.delete(branch)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

    return jsonify({"success": True})


def serialize_student(student):
    return {
        "id": student.id,
        "roll": student.roll,
        "branch": student.branch,
        "student_name": student.student_name,
        "fathers_name": student.fathers_name,
        "guardian_phone": student.guardian_phone,
        "address": student.address,
        "class_name": student.class_name,
        "fixed_fee": student.fixed_fee,
        "fixed_exam_fee": student.fixed_exam_fee,
        "status": student.status,
    }


def read_student_form(data):
    """Validate the register/edit form. Returns (fields, error)."""
    # A service admin can only register students into their own branch; an admin picks one
    if current_user.role == ADMIN_ROLE:
        branch = (data.get("branch") or "").strip()
        if not branch or db.session.execute(db.select(Branch.id).where(Branch.name == branch)).first() is None:
            return None, "Please select a valid branch"
    else:
        branch = current_user.branch.name

    fields = {
        "branch": branch,
        "student_name": (data.get("student_name") or "").strip(),
        "fathers_name": (data.get("fathers_name") or "").strip(),
        "guardian_phone": (data.get("guardian_phone") or "").strip(),
        "address": (data.get("address") or "").strip(),
        "class_name": (data.get("class_name") or "").strip(),
        "roll": str(data.get("roll") or "").strip(),
        "fixed_fee": data.get("fixed_fee"),
        "fixed_exam_fee": data.get("fixed_exam_fee"),
    }
    fee_fields = {"fixed_fee": "Fixed fee", "fixed_exam_fee": "Fixed exam fee"}
    if not all(fields[key] for key in fields if key not in fee_fields) \
            or any(fields[key] in (None, "") for key in fee_fields):
        return None, "Missing required fields"

    for key, label in fee_fields.items():
        try:
            fields[key] = float(fields[key])
        except (TypeError, ValueError):
            return None, f"{label} must be a number"
        if fields[key] < 0:
            return None, f"{label} cannot be negative"
    return fields, None


@app.route("/api/add-student", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def add_student():
    fields, error = read_student_form(request.get_json(silent=True) or {})
    if error:
        return jsonify({"success": False, "error": error}), 400

    status = STUDENT_APPROVED if current_user.role == ADMIN_ROLE else STUDENT_PENDING
    student = StudentRecord(**fields, status=status)
    db.session.add(student)
    db.session.commit()
    return jsonify({"success": True, "student": serialize_student(student)})


@app.route("/api/update-student/<int:id>", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def update_student(id):
    student = db.session.get(StudentRecord, id)
    if student is None:
        return jsonify({"success": False, "error": "Student not found"}), 404

    fields, error = read_student_form(request.get_json(silent=True) or {})
    if error:
        return jsonify({"success": False, "error": error}), 400

    for key, value in fields.items():
        setattr(student, key, value)
    db.session.commit()
    return jsonify({"success": True, "student": serialize_student(student)})


@app.route("/api/approve-student/<int:id>", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def approve_student(id):
    student = db.session.get(StudentRecord, id)
    if student is None:
        return jsonify({"success": False, "error": "Student not found"}), 404
    student.status = STUDENT_APPROVED
    db.session.commit()
    return jsonify({"success": True, "student": serialize_student(student)})


@app.route("/api/delete-student/<int:id>", methods=["DELETE"])
@login_required
@roles_required(ADMIN_ROLE)
def delete_student(id):
    student = db.session.get(StudentRecord, id)
    if student is None:
        return jsonify({"success": False, "error": "Student not found"}), 404
    db.session.delete(student)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/search-students", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def search_students():
    filters = request.json or {}
    branch_name = filters.get("branch")
    # A service admin only sees their own branch's students
    if current_user.role != ADMIN_ROLE:
        branch_name = current_user.branch.name
    school_id = filters.get("id")  # coming from the client
    class_ = filters.get("studentClass")
    status = filters.get("status")
    stmt = db.select(StudentRecord)
    if status in (STUDENT_PENDING, STUDENT_APPROVED):
        stmt = stmt.where(StudentRecord.status == status)

    # filter by branch if provided
    if branch_name:
        # find branch first
        branch_obj = db.session.execute(
            db.select(Branch).where(Branch.name == branch_name)
        ).scalars().first()

        # if branch not found, return empty result
        if branch_obj is None:
            return jsonify({"users": []})

        stmt = stmt.where(StudentRecord.branch == branch_obj.name)

    # filter by school_id if provided
    if school_id:
        try:
            school_id_int = int(school_id)
            stmt = stmt.where(StudentRecord.roll == school_id_int)
        except ValueError:
            # invalid numeric id; return empty result or ignore
            return jsonify({"users": []})

    # Students waiting for approval first, then by branch in the order they were registered
    stmt = stmt.order_by(StudentRecord.status != STUDENT_PENDING, StudentRecord.branch, StudentRecord.id)
    students = db.session.execute(stmt).scalars().all()

    if class_:
        students = filter(lambda student: str(student.roll).startswith(class_), students)

    users_serialized = [serialize_student(student) for student in students]

    return jsonify({"users": users_serialized})


# Teacher registration -------------------------------------------------------------------------------------------------
def serialize_teacher(teacher):
    return {
        "id": teacher.id,
        "branch": teacher.branch,
        "staff_id": teacher.staff_id,
        "teacher_name": teacher.teacher_name,
        "designation": teacher.designation or "",
        "phone": teacher.phone or "",
        "address": teacher.address or "",
        "joining_date": teacher.joining_date.isoformat() if teacher.joining_date else "",
        "monthly_salary": teacher.monthly_salary,
        "salary_due": money(teacher.salary_due),
    }


def read_teacher_form(data):
    """Validate the add/edit form. Returns (fields, error)."""
    fields = {
        "branch": (data.get("branch") or "").strip(),
        "staff_id": str(data.get("staff_id") or "").strip(),
        "teacher_name": (data.get("teacher_name") or "").strip(),
        "designation": (data.get("designation") or "").strip(),
        "phone": (data.get("phone") or "").strip(),
        "address": (data.get("address") or "").strip(),
    }
    if not fields["branch"] or not fields["staff_id"] or not fields["teacher_name"]:
        return None, "Missing required fields"
    if db.session.execute(db.select(Branch.id).where(Branch.name == fields["branch"])).first() is None:
        return None, "Branch not found"

    try:
        fields["monthly_salary"] = float(data.get("monthly_salary"))
    except (TypeError, ValueError):
        return None, "Monthly salary must be a number"
    if fields["monthly_salary"] < 0:
        return None, "Monthly salary cannot be negative"

    joining_date = (data.get("joining_date") or "").strip()
    try:
        fields["joining_date"] = date.fromisoformat(joining_date) if joining_date else None
    except ValueError:
        return None, "Invalid joining date"

    return fields, None


def staff_id_taken(staff_id, except_id=None):
    stmt = db.select(TeacherRecord.id).where(TeacherRecord.staff_id == staff_id)
    if except_id is not None:
        stmt = stmt.where(TeacherRecord.id != except_id)
    return db.session.execute(stmt).first() is not None


@app.route("/api/add-teacher", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def add_teacher():
    fields, error = read_teacher_form(request.get_json(silent=True) or {})
    if error:
        return jsonify({"success": False, "error": error}), 400
    if staff_id_taken(fields["staff_id"]):
        return jsonify({"success": False, "error": f"স্টাফ আইডি {fields['staff_id']} আগে থেকেই আছে"}), 409

    teacher = TeacherRecord(**fields)
    db.session.add(teacher)
    db.session.commit()
    return jsonify({"success": True, "teacher": serialize_teacher(teacher)})


@app.route("/api/update-teacher/<int:id>", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def update_teacher(id):
    teacher = db.session.get(TeacherRecord, id)
    if teacher is None:
        return jsonify({"success": False, "error": "Teacher not found"}), 404

    fields, error = read_teacher_form(request.get_json(silent=True) or {})
    if error:
        return jsonify({"success": False, "error": error}), 400
    if staff_id_taken(fields["staff_id"], except_id=teacher.id):
        return jsonify({"success": False, "error": f"স্টাফ আইডি {fields['staff_id']} আগে থেকেই আছে"}), 409

    for key, value in fields.items():
        setattr(teacher, key, value)
    db.session.commit()
    return jsonify({"success": True, "teacher": serialize_teacher(teacher)})


@app.route("/api/delete-teacher/<int:id>", methods=["DELETE"])
@login_required
@roles_required(ADMIN_ROLE)
def delete_teacher(id):
    teacher = db.session.get(TeacherRecord, id)
    if teacher is None:
        return jsonify({"success": False, "error": "Teacher not found"}), 404
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/search-teachers", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def search_teachers():
    """Used by Teacher Registration and by the staff salary section of the expense page."""
    filters = request.get_json(silent=True) or {}
    branch = (filters.get("branch") or "").strip()
    text = (filters.get("q") or "").strip()

    # A service admin only sees their own branch's staff
    if current_user.role == SERVICE_ADMIN_ROLE:
        branch = current_user.branch.name

    stmt = db.select(TeacherRecord).order_by(TeacherRecord.branch, TeacherRecord.staff_id)
    if branch:
        stmt = stmt.where(TeacherRecord.branch == branch)
    if text:
        pattern = f"%{text}%"
        stmt = stmt.where(TeacherRecord.teacher_name.ilike(pattern) | TeacherRecord.staff_id.ilike(pattern))

    teachers = db.session.execute(stmt).scalars().all()
    return jsonify({"teachers": [serialize_teacher(teacher) for teacher in teachers]})


# Staff salary (expense page) ------------------------------------------------------------------------------------------
def latest_active_staff_payment(teacher_id):
    return db.session.execute(
        db.select(StaffPayment).where(StaffPayment.teacher_id == teacher_id, StaffPayment.cancelled_at.is_(None))
        .order_by(StaffPayment.id.desc()).limit(1)).scalars().first()


def serialize_staff_payment(payment, latest_id):
    return {
        "id": payment.id,
        "date": payment.date.isoformat(),
        "time": payment.created_at.strftime("%H:%M") if payment.created_at else "",
        "branch": payment.branch,
        "staff_name": payment.staff_name,
        "staff_id": payment.staff_id or "",
        "month": payment.month,
        "year": payment.year,
        "total": payment.total,
        "paid": payment.paid,
        "due_after": payment.due_after,
        "paid_by": payment.paid_by,
        "cancelled": payment.cancelled_at is not None,
        "cancelled_by": payment.cancelled_by,
        # A registered teacher's saves build on each other's due, so only the latest can be cancelled
        "can_cancel": payment.cancelled_at is None and (payment.teacher_id is None or payment.id == latest_id),
    }


def teacher_for_current_user(teacher_id):
    """A registered teacher the current user may pay (a Service Admin: own branch only), or None."""
    try:
        teacher = db.session.get(TeacherRecord, int(teacher_id))
    except (TypeError, ValueError):
        return None
    if teacher is None or (current_user.role != ADMIN_ROLE and teacher.branch != current_user.branch.name):
        return None
    return teacher


@app.route('/api/staff-salary-info', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def staff_salary_info():
    """A registered teacher's salary due, what was paid for each month of a year (default: this year),
    and their payments. Used by the expense page and by Teacher Registration's payment history."""
    data = request.get_json(silent=True) or {}
    teacher = teacher_for_current_user(data.get("teacher_id"))
    if teacher is None:
        return jsonify({"success": False, "error": "Teacher not found"}), 404
    this_year = today_in_dhaka().year
    try:
        year = int(data.get("year") or this_year)
    except (TypeError, ValueError):
        year = this_year

    payments = db.session.execute(
        db.select(StaffPayment).where(StaffPayment.teacher_id == teacher.id)
        .order_by(StaffPayment.id.desc())).scalars().all()

    # Per month of the year: total paid, how many payments, and the last payment date
    months = [{"paid": 0.0, "count": 0, "last_date": None} for _ in range(12)]
    for p in payments:
        if p.cancelled_at is None and p.year == year:
            month = months[p.month - 1]
            month["paid"] = round(month["paid"] + p.paid, 2)
            month["count"] += 1
            month["last_date"] = max(month["last_date"] or "", p.date.isoformat())
    years = sorted({p.year for p in payments} | {this_year}, reverse=True)

    latest = latest_active_staff_payment(teacher.id)
    return jsonify({
        "success": True,
        "year": year,
        "years": years,
        "teacher": serialize_teacher(teacher),
        "due": money(teacher.salary_due),
        "months": [month["paid"] for month in months],
        "month_details": months,
        "payments": [serialize_staff_payment(p, latest.id if latest else None) for p in payments],
    })


@app.route('/api/save-staff-salary', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def save_staff_salary():
    """Pay a staff member. The paid amount goes into the branch's data sheet (Staff Salary column).

    Registered teacher: total = their stored salary due + this month's salary (+ other salary), and
    total - paid becomes their new due (negative = advance). Anyone else: the previous due typed on
    the page is used and nothing is stored for them except this payment.
    """
    data = request.get_json(silent=True) or {}
    branch = attendance_branch_for_current_user(data.get("branch"))
    if branch is None:
        return jsonify({"success": False, "error": "Please select a branch"}), 400
    try:
        month = int(data.get("month"))
    except (TypeError, ValueError):
        month = 0
    if not 1 <= month <= 12:
        return jsonify({"success": False, "error": "Please select a month"}), 400

    teacher = None
    if data.get("teacher_id"):
        teacher = teacher_for_current_user(data.get("teacher_id"))
        if teacher is None or teacher.branch != branch:
            return jsonify({"success": False, "error": "Teacher not found in this branch"}), 404
    staff_name = teacher.teacher_name if teacher else (data.get("staff_name") or "").strip()
    staff_id = teacher.staff_id if teacher else (data.get("staff_id") or "").strip()
    if not staff_name:
        return jsonify({"success": False, "error": "Please enter the staff name"}), 400

    try:
        subtotal = read_amount(data, "subtotal")
        paid = read_amount(data, "paid")
        # Previous due and the total may be negative (an advance)
        typed = {}
        for key in ("previous_due", "total"):
            value = data.get(key)
            typed[key] = None if value in (None, "") else round(float(value), 2)
            if typed[key] is not None and not math.isfinite(typed[key]):
                raise ValueError(f"Invalid amount for {key}")
    except (TypeError, ValueError) as e:
        return jsonify({"success": False, "error": str(e)}), 400

    previous_due = money(teacher.salary_due) if teacher else (typed["previous_due"] or 0.0)
    # Total Amount is editable on the page; otherwise it is previous due + this payment's salary
    total = typed["total"] if typed["total"] is not None else round(previous_due + subtotal, 2)
    if paid <= 0 and total == previous_due:
        return jsonify({"success": False, "error": "Nothing to save, all amounts are empty"}), 400

    row = None
    if paid > 0:
        row = DataSheet(date=today_in_dhaka(), branch=branch, **dict.fromkeys(INCOME_FIELDS, 0.0),
                        total_income=0.0, daily_expense=0.0, all_rent_and_bills=0.0, staff_salary=paid,
                        other_expenses=0.0, total_expense=paid)
        db.session.add(row)
        db.session.flush()
        refresh_balance_sheet(branch, row.date)

    due_before = teacher.salary_due if teacher else None
    due_after = round(total - paid, 2)
    if teacher:
        teacher.salary_due = due_after

    payment = StaffPayment(
        date=today_in_dhaka(), branch=branch, teacher_id=teacher.id if teacher else None,
        staff_name=staff_name, staff_id=staff_id, month=month, year=today_in_dhaka().year,
        subtotal=subtotal, previous_due=previous_due, total=total, paid=paid,
        due_after=due_after, due_before=due_before, datasheet_id=row.id if row else None,
        paid_by=current_user.username,
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({"success": True, "branch": branch, "staff_name": staff_name, "paid": paid,
                    "due": due_after, "payment_id": payment.id})


@app.route('/api/cancel-staff-payment/<int:id>', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def cancel_staff_payment(id):
    """Undo a mistaken salary payment: remove its data sheet row and put the teacher's due back."""
    payment = db.session.get(StaffPayment, id)
    if payment is None or (current_user.role != ADMIN_ROLE and payment.branch != current_user.branch.name):
        return jsonify({"success": False, "error": "Payment not found"}), 404
    if payment.cancelled_at is not None:
        return jsonify({"success": False, "error": "This payment is already cancelled"}), 409
    if payment.teacher_id is not None:
        latest = latest_active_staff_payment(payment.teacher_id)
        if latest.id != payment.id:
            return jsonify({"success": False,
                            "error": "Only the latest payment of this staff member can be cancelled. Cancel the later ones first."}), 409

    if payment.datasheet_id:
        row = db.session.get(DataSheet, payment.datasheet_id)
        if row is not None:
            day = row.date
            db.session.delete(row)
            db.session.flush()
            refresh_balance_sheet(payment.branch, day)

    teacher = db.session.get(TeacherRecord, payment.teacher_id) if payment.teacher_id else None
    if teacher is not None and teacher.salary_due == payment.due_after:
        teacher.salary_due = payment.due_before

    payment.cancelled_at = datetime.now(ZoneInfo("Asia/Dhaka"))
    payment.cancelled_by = current_user.username
    db.session.commit()
    return jsonify({"success": True})


# Others ---------------------------------------------------------------------------------------------------------------
# Private video playback ------------------------------------------------------------------------------------------------
# The YouTube ID is never written into the page. The page gets a short-lived token bound to the
# logged-in user and the video, and swaps it for the ID only when the player starts.
VIDEO_TOKEN_MAX_AGE = 120  # seconds
video_token_signer = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="private-video-source")


def can_watch_video(video_id):
    # Students may only watch their own class's videos (both IDs start with the class number)
    return current_user.role != STUDENT_ROLE or str(current_user.school_id)[:1] == str(video_id)[:1]


def private_page_headers(response):
    """No caching, no embedding in other sites, no picture-in-picture, no referrer leaks."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "picture-in-picture=(), display-capture=()"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/video/<int:video_id>")
@login_required
def show_video(video_id):
    if not can_watch_video(video_id):
        page = render_template("video.html", error="এই ভিডিওটি আপনার শ্রেণীর জন্য নয়।", video_id=video_id)
        return private_page_headers(app.make_response((page, 403)))

    video = db.session.get(Video, video_id)
    if video is None:
        page = render_template("video.html", error="এই QR কোডের কোন ভিডিও পাওয়া যায়নি।", video_id=video_id)
        return private_page_headers(app.make_response((page, 404)))

    token = video_token_signer.dumps({"u": current_user.id, "v": video_id})
    page = render_template("video.html", video_id=video_id, class_name=video.class_name, token=token,
                           watermark=f"{current_user.username} · {current_user.school_id}")
    return private_page_headers(app.make_response(page))


@app.route("/api/video-source", methods=["POST"])
@login_required
def video_source():
    """Swap a fresh page token for the YouTube ID. Only works for the same logged-in user, for 2 minutes."""
    token = (request.get_json(silent=True) or {}).get("token") or ""
    try:
        data = video_token_signer.loads(token, max_age=VIDEO_TOKEN_MAX_AGE)
    except SignatureExpired:
        return private_page_headers(jsonify({"success": False, "error": "expired"})), 403
    except BadSignature:
        return private_page_headers(jsonify({"success": False, "error": "invalid"})), 403

    if data.get("u") != current_user.id or not can_watch_video(data.get("v")):
        return private_page_headers(jsonify({"success": False, "error": "forbidden"})), 403

    video = db.session.get(Video, data.get("v"))
    youtube_id = video.link.rstrip("/").rsplit("/", 1)[-1] if video and video.link else None
    if not youtube_id or not helpers.YOUTUBE_ID.match(youtube_id):
        return private_page_headers(jsonify({"success": False, "error": "not found"})), 404

    return private_page_headers(jsonify({"success": True, "id": youtube_id}))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Runs here, after refresh_balance_sheet is defined
with app.app_context():
    assign_sheet_branches()


if __name__ == "__main__":
    app.run(debug=env_flag("FLASK_DEBUG", True), host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT") or 5000))
