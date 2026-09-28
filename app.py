import os
import requests
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

load_dotenv()

app = Flask(__name__)

app.secret_key = "super-secret-session-key"

PARTICIPATE_API = os.getenv(
    "PARTICIPATE_SERVICE_URL"
)

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL"
)

SUBMISSIONS_SERVICE_URL = os.getenv(
    "SUBMISSIONS_SERVICE_URL"
)

PICKWINNER_SERVICE_URL = os.getenv(
    "PICKWINNER_SERVICE_URL"
)

SYNC_SERVICE_URL = os.getenv(
    "SYNC_SERVICE_URL"
)

def get_auth_headers():

    token = session.get("jwt_token")

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }

@app.route("/")
def home():

    winners = []

    try:

        response = requests.get(
            f"{PICKWINNER_SERVICE_URL}/pickwinner/api/v1/winners"
        )

        if response.status_code == 200:
            winners = response.json().get(
                "winners",
                []
            )

    except Exception:
        pass

    return render_template(
        "home.html",
        winners=winners
    )

@app.route("/participate", methods=["POST"])
def participate():

    payload = {
        "name": request.form.get("name"),
        "phone": request.form.get("phone"),
        "email": request.form.get("email")
    }

    response = requests.post(
        f"{PARTICIPATE_API}/participate/api/v1/register",
        json=payload
    )

    if response.status_code == 201:

        flash(
            "Participation submitted successfully",
            "success"
        )

    else:

        flash(
            "Failed to participate",
            "danger"
        )

    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template("login.html")

    payload = {
        "username": request.form.get("username"),
        "password": request.form.get("password")
    }

    response = requests.post(
        f"{AUTH_SERVICE_URL}/auth/api/v1/login",
        json=payload
    )

    if response.status_code != 200:

        flash(
            "Invalid credentials",
            "danger"
        )

        return redirect(url_for("login"))

    token = response.json().get("token")

    session["jwt_token"] = token

    return redirect(url_for("admin_dashboard"))

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))

@app.route("/admin")
def admin_dashboard():

    if "jwt_token" not in session:

        return redirect(url_for("login"))

    submissions = []
    winners = []

    try:

        submissions_response = requests.get(
            f"{SUBMISSIONS_SERVICE_URL}/submissions/api/v1/participants",
            headers=get_auth_headers()
        )

        if submissions_response.status_code == 200:

            submissions = submissions_response.json().get(
                "participants",
                []
            )

    except Exception:
        pass

    try:

        winners_response = requests.get(
            f"{PICKWINNER_SERVICE_URL}/pickwinner/api/v1/winners"
            #headers=get_auth_headers()
        )

        if winners_response.status_code == 200:

            winners = winners_response.json().get(
                "winners",
                []
            )

    except Exception:
        pass

    return render_template(
        "admin.html",
        submissions=submissions,
        winners=winners
    )

@app.route("/admin/hourly-winner", methods=["POST"])
def hourly_winner():

    response = requests.post(
        f"{PICKWINNER_SERVICE_URL}/pickwinner/api/v1/hourly",
        headers=get_auth_headers()
    )

    if response.status_code == 200:

        flash(
            "Hourly winner selected",
            "success"
        )

    else:

        flash(
            "Failed to select hourly winner",
            "danger"
        )

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/daily-first", methods=["POST"])
def daily_first():

    response = requests.post(
        f"{PICKWINNER_SERVICE_URL}/pickwinner/api/v1/daily/first",
        headers=get_auth_headers()
    )

    if response.status_code == 200:

        flash(
            "Daily first winner selected",
            "success"
        )

    else:

        flash(
            "Failed to select winner",
            "danger"
        )

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/daily-second", methods=["POST"])
def daily_second():

    response = requests.post(
        f"{PICKWINNER_SERVICE_URL}/pickwinner/api/v1/daily/second",
        headers=get_auth_headers()
    )

    if response.status_code == 200:

        flash(
            "Daily second winner selected",
            "success"
        )

    else:

        flash(
            "Failed to select winner",
            "danger"
        )

    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    app.run(host="0.0.0.0", port=args.port)
