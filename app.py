from flask import Flask, render_template, request
import base64, os, requests
from datetime import datetime

app = Flask(__name__)

# --- Telegram setup (from environment variables) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUR_TELEGRAM_ID = os.getenv("OWNER_ID")

# Safety check
if not BOT_TOKEN or not YOUR_TELEGRAM_ID:
    raise ValueError("BOT_TOKEN or OWNER_ID is not set in environment variables!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit_signature', methods=['POST'])
def submit_signature():
    sig_type = request.form.get('type')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if sig_type == "typed":
        typed_name = request.form.get('typed_name')
        file_name = f"typed_signature_{timestamp}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(f"Typed Signature: {typed_name}")

        # Send to Telegram
        with open(file_name, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                data={"chat_id": YOUR_TELEGRAM_ID},
                files={"document": f}
            )
        os.remove(file_name)
        return "✅ Typed signature sent successfully!"

    elif sig_type == "drawn":
        data_url = request.form.get('signature')
        img_data = data_url.split(',')[1]
        image_bytes = base64.b64decode(img_data)

        file_name = f"drawn_signature_{timestamp}.png"
        with open(file_name, "wb") as f:
            f.write(image_bytes)

        # Send to Telegram
        with open(file_name, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                data={"chat_id": YOUR_TELEGRAM_ID},
                files={"document": f}
            )
        os.remove(file_name)
        return "✅ Drawn signature sent successfully!"

    return "⚠️ Invalid request"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
