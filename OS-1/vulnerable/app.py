from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    submitted_host = ""

    if request.method == "POST":
        submitted_host = request.form.get("host", "").strip()

        if not submitted_host:
            output = "Please enter a hostname or IP address."
        else:
            try:
                # INTENTIONALLY VULNERABLE:
                # User input is concatenated into a shell command.
                command = f"ping -c 1 {submitted_host}"
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=8
                )
                output = (result.stdout or "") + (result.stderr or "")
            except subprocess.TimeoutExpired:
                output = "Command timed out after 8 seconds."
            except Exception as exc:
                output = f"Error: {exc}"

    return render_template(
        "index.html",
        output=output,
        submitted_host=submitted_host,
        mode="VULNERABLE"
    )

if __name__ == "__main__":
    # Keep this local-only. Do not change host to 0.0.0.0.
    app.run(host="127.0.0.1", port=5000, debug=False)
