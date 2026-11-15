# OS Command Injection — Variant 1 (In-band)

A small **local-only educational lab** for demonstrating in-band OS command injection and one mitigation.

## What this project demonstrates

- `vulnerable/`: a deliberately unsafe ping diagnostic endpoint. It builds a shell command by concatenating user input and executes it with `shell=True`.
- `secured/`: the same feature, but invokes `ping` with an argument list and `shell=False`, so shell separators are not interpreted.
- Both pages display command output in the HTTP response. This makes the vulnerable example **in-band**.

> Safety: Run this only on your own computer and test only this application, as required by the assignment. The vulnerable app intentionally permits shell command execution. Keep it bound to `127.0.0.1`; do not expose it to your network or the internet. Stop it when you are finished.

## Requirements

- Python 3.9+
- macOS or Linux
- `ping` available in the system PATH

## Setup

Open Terminal in this project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the vulnerable version

```bash
cd vulnerable
python3 app.py
```

Open http://127.0.0.1:5000

1. First submit `127.0.0.1` to show normal ping functionality.
2. Then, in this local lab only, submit `127.0.0.1; whoami`.
3. The response should contain the ping output and the output of `whoami`.

Stop the server with `Ctrl+C`.

## Run the secured version

From the project root:

```bash
cd secured
python3 app.py
```

Open http://127.0.0.1:5001

Submit the **same** input: `127.0.0.1; whoami`.

The semicolon is passed as an ordinary character in one argument; it is not treated as a shell command separator. The ping command may report that the hostname is invalid, but `whoami` should not run.

Stop the server with `Ctrl+C`.

## Code locations to explain in your viva

### Vulnerable implementation
`vulnerable/app.py`, function `run_ping()`:

```python
command = f"ping -c 1 {host}"
result = subprocess.run(command, shell=True, ...)
```

The input is concatenated into a command string and interpreted by a shell. A shell metacharacter such as `;` can terminate the ping command and start another command. Since stdout/stderr are returned to the page, the result is in-band.

### Implemented mitigation
`secured/app.py`, function `run_ping()`:

```python
result = subprocess.run(
    ["ping", "-c", "1", host],
    shell=False,
    ...
)
```

The program and its arguments are passed separately. No shell parses the semicolon, so it cannot chain another command.

The secured example also applies a basic hostname/IP character allow-list and a timeout. The central mitigation being demonstrated is **avoiding the shell by using argument-vector execution**.

## Other mitigation alternatives from the assignment

- **Allow-list validation:** accept only expected host/IP formats and reject unexpected characters.
- **Least privilege:** run the web service under an account with only the permissions it needs, limiting damage if it is compromised.

The assignment also names avoiding the shell and parameterised execution with an argument vector. This project demonstrates those together as the selected practical fix.

## Suggested evidence for your video

Capture your own screenshots:
1. Vulnerable app with `127.0.0.1` (normal use).
2. Vulnerable app with `127.0.0.1; whoami` (injected output visible).
3. Secured app with the exact same payload (no `whoami` output).

Explain the vulnerable line, the payload, the root cause, and the fixed line. Do not claim the secured version blocks every possible misuse: it demonstrates prevention of shell interpretation for this injection pattern.

## Project structure

```text
OS-Command-Injection-Variant-1/
├── README.md
├── requirements.txt
├── vulnerable/
│   ├── app.py
│   └── templates/
│       └── index.html
└── secured/
    ├── app.py
    └── templates/
        └── index.html
```
