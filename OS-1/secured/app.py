from flask import Flask, render_template, request
import re
import subprocess

app = Flask(__name__)

# Simple hostname/IP allow-list for this demonstration.
HOST_PATTERN = re.compile(r"^[A-Za-z0-9.-]{1,253}$")

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    submitted_host = ""

    if request.method == "POST":
        submitted_host = request.form.get("host", "").strip()

        if not submitted_host:
            output = "Please enter a hostname or IP address."
        elif not HOST_PATTERN.fullmatch(submitted_host):
            output = "Input rejected: use only letters, numbers, dots, and hyphens."
        else:
            try:
                # MITIGATION: pass executable and arguments separately.
                # shell=False means shell metacharacters are not interpreted.
                result = subprocess.run(
                    ["ping", "-c", "1", submitted_host],
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=8
                )
                output = (result.stdout or "") + (result.stderr or "")
            except subprocess.TimeoutExpired:
                output = "Ping timed out after 8 seconds."
            except Exception as exc:
                output = f"Error: {exc}"

    return render_template(
        "index.html",
        output=output,
        submitted_host=submitted_host,
        mode="SECURED"
    )

if __name__ == "__main__":
    # Keep this local-only. Do not change host to 0.0.0.0.
    app.run(host="127.0.0.1", port=5001, debug=False)
