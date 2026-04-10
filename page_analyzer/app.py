import os

from dotenv import load_dotenv
from flask import Flask, render_template_string

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")


@app.get("/")
def index():
    return render_template_string(
        """
        <!doctype html>
        <html lang="ru">
          <head>
            <meta charset="UTF-8">
            <title>Page Analyzer</title>
          </head>
          <body>
            <h1>Анализатор страниц</h1>
            <p>Приложение успешно запущено</p>
          </body>
        </html>
        """
    )