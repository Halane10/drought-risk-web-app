import html
from textwrap import dedent
import streamlit as st
from datetime import datetime, timedelta
import streamlit.components.v1 as components
from backend.auth_db import (
    authenticate_user,
    create_password_reset_token,
    create_session,
    create_user,
    logout_session,
    password_strength,
    reset_password,
    validate_session,
)
COOKIE_NAME = "drought_auth_session"


def get_cookie_token():
    try:
        return st.context.cookies.get(COOKIE_NAME)
    except Exception:
        return None


def save_cookie_token_and_reload(session_token):
    components.html(
        f"""
        <script>
        document.cookie = "{COOKIE_NAME}={session_token}; path=/; max-age=28800; SameSite=Lax";
        window.parent.location.reload();
        </script>
        """,
        height=0
    )
    st.stop()


def clear_cookie_token_and_reload():
    components.html(
        f"""
        <script>
        document.cookie = "{COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax";
        window.parent.location.href = window.parent.location.origin + window.parent.location.pathname;
        </script>
        """,
        height=0
    )
    st.stop()

# -----------------------------
# Auth CSS Design
# -----------------------------
def load_auth_css():
    # Authentication design is now handled by assets/styles.css
    return


# -----------------------------
# Session State
# -----------------------------
def init_auth_state():
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"

    if "session_token" not in st.session_state:
        st.session_state.session_token = get_cookie_token()
 
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None


def go_to_login():
    st.session_state.auth_page = "login"
    st.rerun()


def go_to_signup():
    st.session_state.auth_page = "signup"
    st.rerun()


def go_to_forgot_password():
    st.session_state.auth_page = "forgot_password"
    st.rerun()


def go_to_reset_password():
    st.session_state.auth_page = "reset_password"
    st.rerun()


# -----------------------------
# Header
# -----------------------------
def auth_header(title, subtitle, badge="Secure Access"):
    st.markdown(
        f"""
        <div class="auth-page-title">
            <div class="auth-badge">{badge}</div>
            <div class="auth-title">{title}</div>
            <div class="auth-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_strength(password):
    if not password:
        return

    strength = password_strength(password)

    if strength == "Weak":
        css_class = "strength-weak"
    elif strength == "Normal":
        css_class = "strength-normal"
    else:
        css_class = "strength-strong"

    st.markdown(
        f"""
        <div class="strength-box {css_class}">
            Password Strength: {strength}
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Login Page
# -----------------------------
def login_page():
    _, center, _ = st.columns([1, 1.4, 1])

    with center:
        auth_header(
            title="Drought Risk Prediction System",
            subtitle="Login to access the drought risk prediction dashboard.",
            badge="Secure Login",
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("Login", use_container_width=True)

            if login_btn:
                if not username.strip() or not password:
                    st.error("Please enter username and password.")
                else:
                    success, message, user = authenticate_user(username, password)

                    if success:
                        session_token = create_session(user["user_id"])
                        st.session_state.session_token = session_token
                        
                        st.session_state.auth_user = {
                            "user_id": user["user_id"],
                            "username": user["username"],
                            "email": user["email"],
                        }
                        st.session_state.auth_page = "dashboard"
                        st.success(message)
                        save_cookie_token_and_reload(session_token)
                    else:
                        st.error(message)
                        

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create account", use_container_width=True):
                go_to_signup()
        with col2:
            if st.button("Forgot Password?", use_container_width=True):
                go_to_forgot_password()


# -----------------------------
# Sign Up Page
# -----------------------------
def signup_page():
    _, center, _ = st.columns([1, 1.4, 1])

    with center:
        auth_header(
            title="Create New Account",
            subtitle="Register to use the drought risk prediction system.",
            badge="Sign Up",
        )

        username = st.text_input("Username", placeholder="Example: halane")
        email = st.text_input("Email", placeholder="Example: user@gmail.com")
        password = st.text_input("Password", type="password", placeholder="Create password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password")

        show_strength(password)

        if st.button("Create Account", use_container_width=True):
            if not username.strip() or not email.strip() or not password or not confirm_password:
                st.error("Please fill all fields.")
            elif password != confirm_password:
                st.error("Password and Confirm Password do not match.")
            else:
                success, message = create_user(username, email, password)
                if success:
                    st.success(message)
                    st.info("You can now login using your username and password.")
                    st.session_state.auth_page = "login"
                    st.rerun()
                else:
                    st.error(message)

        if st.button("Back to Login", use_container_width=True):
            go_to_login()


# -----------------------------
# Forgot Password Page
# -----------------------------
def forgot_password_page():
    _, center, _ = st.columns([1, 1.4, 1])

    with center:
        auth_header(
            title="Forgot Password",
            subtitle="Enter your email address. A reset token will be generated for your account.",
            badge="Password Recovery",
        )

        email = st.text_input("Email", placeholder="Enter your registered email")

        if st.button("Request Password Reset", use_container_width=True):
            if not email.strip():
                st.error("Please enter your email address.")
            else:
                success, message, reset_token = create_password_reset_token(email)
                if success:
                    st.success(message)

                    # Temporary for local testing.
                    # Later this token can be sent by SMTP email.
                    if reset_token:
                        st.session_state.demo_reset_token = reset_token
                        st.info("Reset token generated for testing. Email sending will be added later.")
                        st.code(reset_token)

                    st.session_state.auth_page = "reset_password"
                else:
                    st.error(message)

        if st.button("Back to Login", use_container_width=True):
            go_to_login()


# -----------------------------
# Reset Password Page
# -----------------------------
def reset_password_page():
    _, center, _ = st.columns([1, 1.4, 1])

    with center:
        auth_header(
            title="Reset Password",
            subtitle="Enter your reset token and create a new password.",
            badge="Reset Password",
        )

        default_token = st.session_state.get("demo_reset_token", "")
        reset_token = st.text_input("Reset Token", value=default_token, type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")

        show_strength(new_password)

        if st.button("Reset Password", use_container_width=True):
            if not reset_token or not new_password or not confirm_password:
                st.error("Please fill all fields.")
            elif new_password != confirm_password:
                st.error("New password and confirm password do not match.")
            else:
                success, message = reset_password(reset_token, new_password)
                if success:
                    st.success(message)
                    st.session_state.demo_reset_token = ""
                    st.session_state.auth_page = "login"
                    st.rerun()
                else:
                    st.error(message)

        if st.button("Back to Login", use_container_width=True):
            go_to_login()


# -----------------------------
# Main Auth Router
# -----------------------------
def show_auth_pages():
    load_auth_css()
    init_auth_state()

    if st.session_state.auth_page == "signup":
        signup_page()
    elif st.session_state.auth_page == "forgot_password":
        forgot_password_page()
    elif st.session_state.auth_page == "reset_password":
        reset_password_page()
    else:
        login_page()


# -----------------------------
# Protect Dashboard
# -----------------------------
def require_authentication():
    load_auth_css()
    init_auth_state()

    session_token = st.session_state.get("session_token")

    if not session_token:
        session_token = get_cookie_token()
        st.session_state.session_token = session_token

    if session_token:
        user = validate_session(session_token)

        if user:
            st.session_state.auth_user = user
            return user

        st.session_state.session_token = None
        st.session_state.auth_user = None
        clear_cookie_token_and_reload()

    show_auth_pages()
    st.stop()

# -----------------------------
# Top Right Username Logout
# -----------------------------
def render_top_user_logout():
    user = st.session_state.get("auth_user")

    if not user:
        return

    if st.query_params.get("logout") == "1":
        logout_session(st.session_state.get("session_token"))
        st.session_state.session_token = None
        st.session_state.auth_user = None
        st.session_state.auth_page = "login"
        clear_cookie_token_and_reload()

    username = html.escape(user.get("username", "User"))
    email = html.escape(user.get("email", ""))
    initials = username[:1].upper()

    profile_html = (
        f'<div class="custom-profile-fixed">'
        f'<details class="custom-profile-dropdown">'
        f'<summary class="custom-profile-button">'
        f'<div class="custom-profile-avatar">{initials}</div>'
        f'<div class="custom-profile-text">'
        f'<div class="custom-profile-name">{username}</div>'
        f'<div class="custom-profile-email">{email}</div>'
        f'</div>'
        f'<i class="fa-solid fa-chevron-down custom-profile-arrow"></i>'
        f'</summary>'
        f'<div class="custom-profile-menu">'
        f'<div class="custom-profile-menu-header">'
        f'<div class="custom-profile-avatar big">{initials}</div>'
        f'<div>'
        f'<div class="custom-profile-name">{username}</div>'
        f'<div class="custom-profile-email">{email}</div>'
        f'</div>'
        f'</div>'
        f'<div class="custom-profile-divider"></div>'
        f'<a class="custom-profile-item" href="?profile=1" target="_self">'
        f'<i class="fa-solid fa-user"></i><span>My Profile</span>'
        f'</a>'
        f'<a class="custom-profile-item" href="?secure_session=1" target="_self">'
        f'<i class="fa-solid fa-lock"></i><span>Secure Session</span>'
        f'</a>'
        f'<div class="custom-profile-item">'
        f'<i class="fa-solid fa-clock"></i><span>Session expires after 30 minutes</span>'
        f'</div>'
        f'<div class="custom-profile-divider"></div>'
        f'<a class="custom-profile-logout" href="?logout=1" target="_self">'
        f'<i class="fa-solid fa-right-from-bracket"></i><span>Log out</span>'
        f'</a>'
        f'</div>'
        f'</details>'
        f'</div>'
    )

    st.markdown(profile_html, unsafe_allow_html=True)

def render_auth_menu_page():
    user = st.session_state.get("auth_user")

    if not user:
        return False

    username = html.escape(user.get("username", "User"))
    email = html.escape(user.get("email", ""))
    initials = username[:1].upper()

    if st.query_params.get("profile") == "1":
        profile_html = (
            f'<div class="auth-info-card">'
            f'<div class="auth-info-header">'
            f'<div class="custom-profile-avatar big">{initials}</div>'
            f'<div>'
            f'<h2>My Profile</h2>'
            f'<p>Account information for the logged-in user.</p>'
            f'</div>'
            f'</div>'
            f'<div class="auth-info-row">'
            f'<span>Username</span>'
            f'<strong>{username}</strong>'
            f'</div>'
            f'<div class="auth-info-row">'
            f'<span>Email</span>'
            f'<strong>{email}</strong>'
            f'</div>'
            f'<div class="auth-info-row">'
            f'<span>Account Type</span>'
            f'<strong>Authenticated User</strong>'
            f'</div>'
            f'</div>'
        )

        st.html(profile_html)

        if st.button("Back to Dashboard", use_container_width=True):
            st.query_params.clear()
            st.rerun()

        return True

    if st.query_params.get("secure_session") == "1":
        session_html = (
            f'<div class="auth-info-card">'
            f'<div class="auth-info-header">'
            f'<div class="custom-profile-avatar big">'
            f'<i class="fa-solid fa-lock"></i>'
            f'</div>'
            f'<div>'
            f'<h2>Secure Session</h2>'
            f'<p>Your session is protected using a secure session token.</p>'
            f'</div>'
            f'</div>'
            f'<div class="auth-info-row">'
            f'<span>Logged-in User</span>'
            f'<strong>{username}</strong>'
            f'</div>'
            f'<div class="auth-info-row">'
            f'<span>Session Status</span>'
            f'<strong>Active</strong>'
            f'</div>'
            f'<div class="auth-info-row">'
            f'<span>Inactivity Expiry</span>'
            f'<strong>30 minutes</strong>'
            f'</div>'
            f'<div class="auth-info-row">'
            f'<span>Security Method</span>'
            f'<strong>Session Token + bcrypt Password Hashing</strong>'
            f'</div>'
            f'</div>'
        )

        st.html(session_html)

        if st.button("Back to Dashboard", use_container_width=True):
            st.query_params.clear()
            st.rerun()

        return True

    return False
    user = st.session_state.get("auth_user")

    if not user:
        return False

    username = html.escape(user.get("username", "User"))
    email = html.escape(user.get("email", ""))
    initials = username[:1].upper()

    if st.query_params.get("profile") == "1":
        st.markdown(
            f"""
            <div class="auth-info-card">
                <div class="auth-info-header">
                    <div class="
                    -avatar big">{initials}</div>
                    <div>
                        <h2>My Profile</h2>
                        <p>Account information for the logged-in user.</p>
                    </div>
                </div>

                <div class="auth-info-row">
                    <span>Username</span>
                    <strong>{username}</strong>
                </div>

                <div class="auth-info-row">
                    <span>Email</span>
                    <strong>{email}</strong>
                </div>

                <div class="auth-info-row">
                    <span>Account Type</span>
                    <strong>Authenticated User</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Back to Dashboard", use_container_width=True):
            st.query_params.clear()
            st.rerun()

        return True

    if st.query_params.get("secure_session") == "1":
        st.markdown(
            f"""
            <div class="auth-info-card">
                <div class="auth-info-header">
                    <div class="custom-profile-avatar big">
                        <i class="fa-solid fa-lock"></i>
                    </div>
                    <div>
                        <h2>Secure Session</h2>
                        <p>Your session is protected using a secure session token.</p>
                    </div>
                </div>

                <div class="auth-info-row">
                    <span>Logged-in User</span>
                    <strong>{username}</strong>
                </div>

                <div class="auth-info-row">
                    <span>Session Status</span>
                    <strong>Active</strong>
                </div>

                <div class="auth-info-row">
                    <span>Inactivity Expiry</span>
                    <strong>30 minutes</strong>
                </div>

                <div class="auth-info-row">
                    <span>Security Method</span>
                    <strong>Session Token + bcrypt Password Hashing</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Back to Dashboard", use_container_width=True):
            st.query_params.clear()
            st.rerun()

        return True

    return False