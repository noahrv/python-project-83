import os
from datetime import datetime
from urllib.parse import urlparse

import psycopg
import validators
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    return psycopg.connect(database_url)


def normalize_url(raw_url):
    parsed = urlparse(raw_url)
    return f"{parsed.scheme}://{parsed.netloc}"


def validate_url(url):
    errors = {}

    if not url:
        errors["url"] = "URL обязателен"
        return errors

    if len(url) > 255:
        errors["url"] = "URL не должен превышать 255 символов"
        return errors

    if not validators.url(url):
        errors["url"] = "Некорректный URL"
        return errors

    return errors


def find_url_by_name(name):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, created_at FROM urls WHERE name = %s;",
                (name,),
            )
            row = cur.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "created_at": row[2],
    }


def insert_url(name):
    created_at = datetime.now()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s)
                RETURNING id, name, created_at;
                """,
                (name, created_at),
            )
            row = cur.fetchone()
        conn.commit()

    return {
        "id": row[0],
        "name": row[1],
        "created_at": row[2],
    }


def find_all_urls():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    urls.id,
                    urls.name,
                    checks.created_at AS last_check_created_at,
                    checks.status_code AS last_check_status_code
                FROM urls
                LEFT JOIN (
                    SELECT DISTINCT ON (url_id)
                        id,
                        url_id,
                        status_code,
                        created_at
                    FROM url_checks
                    ORDER BY url_id, id DESC
                ) AS checks ON urls.id = checks.url_id
                ORDER BY urls.id DESC;
                """
            )
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "last_check_created_at": row[2],
            "last_check_status_code": row[3],
        }
        for row in rows
    ]


def find_url_by_id(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, created_at
                FROM urls
                WHERE id = %s;
                """,
                (url_id,),
            )
            row = cur.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "created_at": row[2],
    }


def insert_url_check(url_id):
    created_at = datetime.now()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO url_checks (url_id, created_at)
                VALUES (%s, %s)
                RETURNING id, url_id, status_code, h1, title, description, created_at;
                """,
                (url_id, created_at),
            )
            row = cur.fetchone()
        conn.commit()

    return {
        "id": row[0],
        "url_id": row[1],
        "status_code": row[2],
        "h1": row[3],
        "title": row[4],
        "description": row[5],
        "created_at": row[6],
    }


def find_url_checks(url_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, url_id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC;
                """,
                (url_id,),
            )
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "url_id": row[1],
            "status_code": row[2],
            "h1": row[3],
            "title": row[4],
            "description": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]


@app.get("/")
def index():
    return render_template("index.html", url="", errors={})


@app.post("/urls")
def create_url():
    raw_url = request.form.get("url", "").strip()
    errors = validate_url(raw_url)

    if errors:
        return render_template(
            "index.html",
            url=raw_url,
            errors=errors,
        ), 422

    normalized_url = normalize_url(raw_url)
    existing_url = find_url_by_name(normalized_url)

    if existing_url is not None:
        flash("Страница уже существует", "info")
        return redirect(url_for("show_url", id=existing_url["id"]))

    new_url = insert_url(normalized_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("show_url", id=new_url["id"]))


@app.get("/urls")
def urls_index():
    urls = find_all_urls()
    return render_template("urls/index.html", urls=urls)


@app.get("/urls/<int:id>")
def show_url(id):
    url = find_url_by_id(id)

    if url is None:
        flash("Страница не найдена", "danger")
        return redirect(url_for("urls_index"))

    checks = find_url_checks(id)
    return render_template("urls/show.html", url=url, checks=checks)


@app.post("/urls/<int:id>/checks")
def create_url_check(id):
    url = find_url_by_id(id)

    if url is None:
        flash("Страница не найдена", "danger")
        return redirect(url_for("urls_index"))

    try:
        insert_url_check(id)
        flash("Страница успешно проверена", "success")
    except Exception:
        flash("Произошла ошибка при проверке", "danger")

    return redirect(url_for("show_url", id=id))