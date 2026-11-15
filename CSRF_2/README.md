# CSRF Demonstration: Auto-Submitting POST Form

A local, two-app Flask project for demonstrating a POST-based Cross-Site Request Forgery (CSRF) attack and blocking it with a synchronizer token. Use this only as a classroom demonstration against these local apps.

## Ownership Declaration

| Member Name | Roll Number | Category | Variant Implemented |
|---|---|---|---|
| Aditya Bhatnagar | IIT2024072 | CSRF | POST-based CSRF demonstration with synchronizer-token protection |

## Project files

```text
Cybersec/
├── app.py                    # Victim app: vulnerable and token-protected modes
├── attacker.py               # Serves the local forged-form page
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   └── csrf_error.html
└── attacker/
    └── attack.html
```

The account is `aditya` with password `12345`. Its initial email is `aditya@example.com`. Email state is held in memory and resets when the victim app restarts.

## Setup on macOS

In Terminal, from the project folder:

```bash
cd "/Users/adi/Desktop/Cybersec"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Activate `.venv` in each new Terminal window before starting an app.

## Run the vulnerable demonstration

Open two Terminal windows.

**Terminal 1 — victim app, CSRF protection off (the default):**

```bash
cd "/Users/adi/Desktop/Cybersec"
source .venv/bin/activate
python3 app.py
```

**Terminal 2 — attacker page:**

```bash
cd "/Users/adi/Desktop/Cybersec"
source .venv/bin/activate
python3 attacker.py
```

In one browser, open `http://localhost:5000`, sign in as `aditya` / `12345`, and note the email. Then open `http://localhost:5001`. Its JavaScript submits the hidden email `attacker-controlled@example.com` to the victim's `/change-email` endpoint. The vulnerable app accepts the POST because the browser includes the logged-in session cookie and the server does not require proof that the request came from its own form. The victim dashboard displays the changed email. The attack page builds its target URL from its own hostname, so if you use `127.0.0.1` for one app, use it for both apps and the victim page too.

The attacker app only serves HTML. The victim browser sends the forged POST directly to the victim app; the attacker server does not change account state.

## Run the protected demonstration

Stop both apps with **Control-C**. Start them again using the following commands.

**Terminal 1 — victim app, synchronizer-token protection on:**

```bash
cd "/Users/adi/Desktop/Cybersec"
source .venv/bin/activate
CSRF_PROTECTION=1 python3 app.py
```

**Terminal 2 — attacker page, unchanged:**

```bash
cd "/Users/adi/Desktop/Cybersec"
source .venv/bin/activate
python3 attacker.py
```

Log in again at `http://localhost:5000` and visit `http://localhost:5001`. The same form still submits, but the victim responds with HTTP 400 and a CSRF rejection message. Return to the dashboard: the email remains `aditya@example.com` (the victim restart reset the in-memory value).

To switch back to the vulnerable mode, stop the victim app and run `python3 app.py` without the `CSRF_PROTECTION=1` prefix. Restarting the victim also resets its in-memory email.

## Why the local cookie is sent

Both URLs must use the same scheme and host; only the ports differ. Ports separate origins but do not make these URLs cross-site. The victim sets its Flask session cookie to `SameSite=Lax` and `HttpOnly`. A same-site POST from port 5001 to port 5000 can therefore include the victim cookie. The attack form derives its target host from the attacker page URL. This local setup shows why authentication alone does not stop CSRF: the browser attaches the cookie automatically, while the server needs a separate CSRF defense.

## Root cause and fix

In vulnerable mode, `/change-email` checks that a user is logged in and then trusts the submitted `email`. It does not check whether the request was created by the victim site's own page. A hostile page can cause the user's browser to submit a cross-origin form; the browser supplies the victim's session cookie.

With `CSRF_PROTECTION=1`, the victim generates a random token and stores it in the Flask session. It places the token in legitimate POST forms and checks it on every POST request, including login, email change, and logout. The attacker page does not know the session token, so its POST is rejected. The token is not an authentication credential; it is evidence that the POST form came from a page that could read the victim session's token.

Other defenses include `SameSite` cookies (as a useful additional layer), asking the user to re-authenticate for sensitive actions, and never using GET requests for actions that change data. A CSRF token remains valuable because cookie and browser policy details can vary.

## Video outline (about 2–3 minutes)

1. **0:00–0:15 — Intro:** “CSRF tricks a browser that is already signed in to send an unwanted request. This demo changes an account email using a POST form.”
2. **0:15–0:35 — Sign in:** Show the victim app, log in as `aditya`, and point out `aditya@example.com` on the dashboard.
3. **0:35–1:00 — Attack:** Open the attacker app. Explain that its hidden form auto-submits a POST to the victim app; no click is needed. Show the resulting `attacker-controlled@example.com` value.
4. **1:00–1:20 — Root cause:** Point to the vulnerable `/change-email` handler. It checks login but accepts the email without a CSRF token. The browser automatically attaches its session cookie.
5. **1:20–1:40 — Enable defense:** Stop the apps. Restart the victim with `CSRF_PROTECTION=1` and restart the attacker app unchanged.
6. **1:40–2:05 — Repeat:** Sign in, show the original email, and open the attacker page. Show the rejection response and confirm the dashboard email did not change.
7. **2:05–2:30 — Mitigations:** Explain the synchronizer token, then briefly mention `SameSite` cookies, re-authentication for sensitive actions, and avoiding state-changing GET requests.

## Screenshot checklist

Capture these from the browser or editor for the assignment report:

1. Victim login page with the demo username visible (do not show the password field filled in).
2. Vulnerable dashboard showing `aditya@example.com` before the attack.
3. Attacker page before/while it submits, showing the local demonstration message.
4. Vulnerable dashboard after the attack showing `attacker-controlled@example.com`.
5. `app.py` highlighting the intentionally vulnerable `/change-email` handler and its no-token comment.
6. Protected login/dashboard with CSRF protection enabled; show the legitimate hidden token input in the editor if the token is not visible on the page.
7. CSRF rejection page after the same attacker form submits in protected mode.
8. Protected dashboard showing `aditya@example.com` remains unchanged.

## Safety and demo limits

Both Flask servers bind to `127.0.0.1` and are intended for this local exercise. The included Flask secret key is for demonstration only. Do not expose the development servers to a network or reuse this configuration for a real service. Data is in memory; restarting the victim returns the email to its initial value.
