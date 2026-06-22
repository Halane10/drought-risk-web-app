import re
import secrets as py_secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import streamlit as st
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


SESSION_TIMEOUT_MINUTES = 30
PASSWORD_RESET_MINUTES = 30


# -----------------------------
# Database Connection
# -----------------------------
@st.cache_resource
def get_engine():
    database_url = st.secrets.get("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL was not found in .streamlit/secrets.toml")

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )


def test_connection():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True


def now_utc():
    return datetime.now(timezone.utc)


def make_datetime_aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


# -----------------------------
# Input Validation
# -----------------------------
def validate_username(username):
    username = username.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if len(username) > 50:
        return False, "Username must not exceed 50 characters."

    if not re.match(r"^[A-Za-z0-9_.-]+$", username):
        return False, "Username can only contain letters, numbers, underscore, dot, or dash."

    return True, ""


def validate_user_email(email):
    email = email.strip().lower()

    try:
        validate_email(email, check_deliverability=False)
        return True, ""
    except EmailNotValidError:
        return False, "Invalid email address."


def password_strength(password):
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_number = bool(re.search(r"[0-9]", password))
    has_special = bool(re.search(r"[^A-Za-z0-9]", password))

    if len(password) < 8:
        return "Weak"

    if password.isalpha() or password.isdigit():
        return "Weak"

    if len(password) >= 12 and has_lower and has_upper and has_number and has_special:
        return "Strong"

    if len(password) >= 8 and (has_lower or has_upper) and has_number:
        return "Normal"

    return "Weak"


# -----------------------------
# Password Hashing
# -----------------------------
def hash_password(password):
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(password, password_hash):
    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_bytes)


# -----------------------------
# User Functions
# -----------------------------
def get_user_by_username(username):
    engine = get_engine()

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT user_id, username, email, password_hash, created_at
                FROM users
                WHERE username = :username
            """),
            {"username": username.strip()}
        ).fetchone()

    if result:
        return dict(result._mapping)

    return None


def get_user_by_email(email):
    engine = get_engine()

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT user_id, username, email, password_hash, created_at
                FROM users
                WHERE email = :email
            """),
            {"email": email.strip().lower()}
        ).fetchone()

    if result:
        return dict(result._mapping)

    return None


def create_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    valid_username, username_error = validate_username(username)
    if not valid_username:
        return False, username_error

    valid_email, email_error = validate_user_email(email)
    if not valid_email:
        return False, email_error

    if not password:
        return False, "Password is required."

    if get_user_by_username(username):
        return False, "Username already exists."

    if get_user_by_email(email):
        return False, "Email already exists."

    password_hash = hash_password(password)
    engine = get_engine()

    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO users (username, email, password_hash)
                    VALUES (:username, :email, :password_hash)
                """),
                {
                    "username": username,
                    "email": email,
                    "password_hash": password_hash
                }
            )

        return True, "Account created successfully."

    except IntegrityError:
        return False, "Username or email already exists."

    except SQLAlchemyError as e:
        return False, f"Database error: {str(e)}"


def authenticate_user(username, password):
    user = get_user_by_username(username)

    if not user:
        return False, "Invalid username or password.", None

    if not verify_password(password, user["password_hash"]):
        return False, "Invalid username or password.", None

    return True, "Login successful.", user


# -----------------------------
# Session Management
# -----------------------------
def create_session(user_id):
    session_token = py_secrets.token_urlsafe(48)
    created_at = now_utc()
    expires_at = created_at + timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE user_sessions
                SET is_active = FALSE
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        )

        conn.execute(
            text("""
                INSERT INTO user_sessions
                (user_id, session_token, created_at, last_active_at, expires_at, is_active)
                VALUES
                (:user_id, :session_token, :created_at, :last_active_at, :expires_at, TRUE)
            """),
            {
                "user_id": user_id,
                "session_token": session_token,
                "created_at": created_at,
                "last_active_at": created_at,
                "expires_at": expires_at
            }
        )

    return session_token


def validate_session(session_token):
    if not session_token:
        return None

    engine = get_engine()

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                SELECT
                    s.session_id,
                    s.session_token,
                    s.expires_at,
                    u.user_id,
                    u.username,
                    u.email
                FROM user_sessions s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.session_token = :session_token
                AND s.is_active = TRUE
            """),
            {"session_token": session_token}
        ).fetchone()

        if not result:
            return None

        session_data = dict(result._mapping)
        expires_at = make_datetime_aware(session_data["expires_at"])

        if now_utc() > expires_at:
            conn.execute(
                text("""
                    UPDATE user_sessions
                    SET is_active = FALSE
                    WHERE session_token = :session_token
                """),
                {"session_token": session_token}
            )
            return None

        new_expiry = now_utc() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)

        conn.execute(
            text("""
                UPDATE user_sessions
                SET last_active_at = :last_active_at,
                    expires_at = :expires_at
                WHERE session_token = :session_token
            """),
            {
                "last_active_at": now_utc(),
                "expires_at": new_expiry,
                "session_token": session_token
            }
        )

    return {
        "user_id": session_data["user_id"],
        "username": session_data["username"],
        "email": session_data["email"]
    }


def logout_session(session_token):
    if not session_token:
        return

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE user_sessions
                SET is_active = FALSE
                WHERE session_token = :session_token
            """),
            {"session_token": session_token}
        )


# -----------------------------
# Password Reset
# -----------------------------
def create_password_reset_token(email):
    email = email.strip().lower()

    valid_email, email_error = validate_user_email(email)
    if not valid_email:
        return False, email_error, None

    user = get_user_by_email(email)

    # For security, do not reveal if email exists or not
    if not user:
        return True, "If this email exists, a reset link will be sent.", None

    reset_token = py_secrets.token_urlsafe(48)
    created_at = now_utc()
    expires_at = created_at + timedelta(minutes=PASSWORD_RESET_MINUTES)

    engine = get_engine()

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO password_reset
                (user_id, email, reset_token, expires_at, used, created_at)
                VALUES
                (:user_id, :email, :reset_token, :expires_at, FALSE, :created_at)
            """),
            {
                "user_id": user["user_id"],
                "email": email,
                "reset_token": reset_token,
                "expires_at": expires_at,
                "created_at": created_at
            }
        )

    return True, "If this email exists, a reset link will be sent.", reset_token


def reset_password(reset_token, new_password):
    if not reset_token:
        return False, "Invalid reset token."

    if not new_password:
        return False, "New password is required."

    engine = get_engine()

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                SELECT reset_id, user_id, expires_at, used
                FROM password_reset
                WHERE reset_token = :reset_token
                AND used = FALSE
            """),
            {"reset_token": reset_token}
        ).fetchone()

        if not result:
            return False, "Invalid or expired reset token."

        reset_data = dict(result._mapping)
        expires_at = make_datetime_aware(reset_data["expires_at"])

        if now_utc() > expires_at:
            conn.execute(
                text("""
                    UPDATE password_reset
                    SET used = TRUE
                    WHERE reset_id = :reset_id
                """),
                {"reset_id": reset_data["reset_id"]}
            )
            return False, "Reset token has expired."

        new_password_hash = hash_password(new_password)

        conn.execute(
            text("""
                UPDATE users
                SET password_hash = :password_hash
                WHERE user_id = :user_id
            """),
            {
                "password_hash": new_password_hash,
                "user_id": reset_data["user_id"]
            }
        )

        conn.execute(
            text("""
                UPDATE password_reset
                SET used = TRUE
                WHERE reset_id = :reset_id
            """),
            {"reset_id": reset_data["reset_id"]}
        )

    return True, "Password reset successfully."