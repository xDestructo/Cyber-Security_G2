"""Victim website for the local CSRF class demonstration.

Set CSRF_PROTECTION=1 to enable synchronizer-token protection. The default
keeps the vulnerable mode available for the first half of the demonstration.
"""

import hmac
import os
import secrets

from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)

# Demo-only secret. Replace this with a private random value outside this local
# classroom exercise. Flask uses it to sign the session cookie.
app.config["SECRET_KEY"] = "local-csrf-class-demo-only-change-me"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["CSRF_PROTECTION"] = os.environ.get("CSRF_PROTECTION", "0") == "1"

DEMO_USERNAME = "aditya"
DEMO_PASSWORD = "12345"

# In-memory state resets whenever this Flask process restarts.
current_email = "aditya@example.com"


@app.before_request
def enforce_csrf_token():
    """Create a session token and validate every POST when protection is on."""
    if not app.config["CSRF_PROTECTION"]:
        return None

    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token

    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")
        if not submitted_token or not hmac.compare_digest(submitted_token, token):
            return render_template("csrf_error.html"), 400
    return None


@app.context_processor
def provide_csrf_template_values():
    return {
        "csrf_protection": app.config["CSRF_PROTECTION"],
        "csrf_token": session.get("csrf_token", ""),
    }


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == DEMO_USERNAME and password == DEMO_PASSWORD:
            session.clear()
            session["username"] = username
            if app.config["CSRF_PROTECTION"]:
                # Start a fresh synchronizer token for the authenticated session.
                session["csrf_token"] = secrets.token_urlsafe(32)
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.", "error")

    return render_template("login.html")


@app.get("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template(
        "dashboard.html", username=session["username"], email=current_email
    )


@app.post("/change-email")
def change_email():
    global current_email

    if "username" not in session:
        return "Please log in first.", 401

    # INTENTIONALLY VULNERABLE: this authenticated state-changing POST accepts
    # any submitted email and does not validate a CSRF token.
    new_email = request.form.get("email", "").strip()
    if not new_email:
        flash("Enter an email address.", "error")
        return redirect(url_for("dashboard"))

    current_email = new_email
    flash("Email address updated.", "success")
    return redirect(url_for("dashboard"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    # localhost is used by both demo apps so browser cookie behavior is
    # consistent across their different ports.
    app.run(host="127.0.0.1", port=5000, debug=True)
