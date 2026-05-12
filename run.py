import os
from app import create_app

app = create_app()

@app.route("/")
def home():
    return "Backend Connected Successfully"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )