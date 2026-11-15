"""Attacker page for the local CSRF class demonstration.

This app only serves a page. The browser submits the form directly to the
victim app; this server never changes victim account data itself.
"""

from flask import Flask, render_template

app = Flask(__name__, template_folder="attacker")


@app.get("/")
def attack_page():
    return render_template("attack.html")


if __name__ == "__main__":
    # Keep the attacker simulation available only on this computer.
    app.run(host="127.0.0.1", port=5001, debug=True)
