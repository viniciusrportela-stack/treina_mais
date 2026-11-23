import os
import secrets
from pathlib import Path
from flask import Flask, jsonify, render_template, request, session
import bd_exec

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = os.environ.get("SECRET_KEY", "treina-mais-chave-secreta-2026")

ADMIN_USUARIO = "admin"
ADMIN_SENHA = "treina2026"

bd_exec.criar_tabela()


def is_admin():
    return bool(session.get("admin"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/login", methods=["POST"])
def login():
    dados = request.get_json(silent=True) or {}
    usuario = str(dados.get("usuario", "")).strip()
    senha = str(dados.get("senha", ""))

    if secrets.compare_digest(usuario, ADMIN_USUARIO) and secrets.compare_digest(senha, ADMIN_SENHA):
        session["admin"] = True
        return jsonify({"ok": True})

    return jsonify({"ok": False, "erro": "Usuário ou senha incorretos."}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("admin", None)
    return jsonify({"ok": True})


@app.route("/api/academias", methods=["GET"])
def listar_academias():
    linhas = bd_exec.exec(
        "SELECT id, name, city, uf, hood, tags, url, desc, img FROM academias ORDER BY name COLLATE NOCASE ASC",
        fetch="all",
    )
    for item in linhas:
        item["tags"] = [t.strip() for t in (item["tags"] or "").split(",") if t.strip()]

    return jsonify({"admin": is_admin(), "academias": linhas})


@app.route("/api/academias", methods=["POST"])
def adicionar_academia():
    if not is_admin():
        return jsonify({"erro": "Acesso negado. Faça login como administrador."}), 403

    dados = request.get_json(silent=True) or {}
    name = str(dados.get("name", "")).strip()[:80]
    city = str(dados.get("city", "")).strip()[:60]
    uf = str(dados.get("uf", "")).strip().upper()[:2]
    hood = str(dados.get("hood", "")).strip()[:60]
    url = str(dados.get("url", "")).strip()
    img = str(dados.get("img", "")).strip()
    desc = str(dados.get("desc", "")).strip()[:220]

    raw_tags = dados.get("tags", "")
    if isinstance(raw_tags, str):
        raw_tags = raw_tags.split(",")
    tags_list = [
        t.strip()[0].upper() + t.strip()[1:].lower()
        for t in raw_tags
        if str(t).strip()
    ]

    if not name or not city or len(uf) != 2:
        return jsonify({"erro": "Preencha nome, cidade e UF corretamente."}), 400

    if not (url.startswith("http://") or url.startswith("https://")):
        return jsonify({"erro": "O link do site precisa começar com http:// ou https://"}), 400

    if img and not (img.startswith("http://") or img.startswith("https://")):
        return jsonify({"erro": "O link da foto precisa começar com http:// ou https://"}), 400

    novo_id = bd_exec.exec(
        """
        INSERT INTO academias (name, city, uf, hood, tags, url, desc, img)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, city, uf, hood, ", ".join(tags_list), url, desc, img),
    )

    return jsonify({
        "id": novo_id,
        "name": name,
        "city": city,
        "uf": uf,
        "hood": hood,
        "tags": tags_list,
        "url": url,
        "desc": desc,
        "img": img,
    }), 201


@app.route("/api/academias/<int:gym_id>", methods=["DELETE"])
def remover_academia(gym_id):
    if not is_admin():
        return jsonify({"erro": "Acesso negado."}), 403

    bd_exec.exec("DELETE FROM academias WHERE id = ?", (gym_id,))
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)