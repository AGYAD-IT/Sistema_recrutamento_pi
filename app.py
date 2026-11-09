
from flask import Flask, render_template, request, redirect, send_from_directory
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

def conectar_banco():
    conexao = sqlite3.connect("recrutamento.db")
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS candidatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            nacionalidade TEXT,
            idade INTEGER,
            cpf TEXT,
passaporte TEXT,
identificacao TEXT
        )
    """)
    colunas = [coluna[1] for coluna in conexao.execute("PRAGMA table_info(candidatos)").fetchall()]

    if "passaporte" not in colunas:
        conexao.execute("ALTER TABLE candidatos ADD COLUMN passaporte TEXT")

    if "identificacao" not in colunas:
        conexao.execute("ALTER TABLE candidatos ADD COLUMN identificacao TEXT")
    conexao.commit()
    conexao.close()


@app.route("/")
def inicio():
    return render_template("index.html")
@app.route("/uploads/<nome_arquivo>")
def visualizar_documento(nome_arquivo):
    return send_from_directory(app.config["UPLOAD_FOLDER"], nome_arquivo)
@app.route("/candidatos")
def listar_candidatos():
    conexao = conectar_banco()

    candidatos = conexao.execute(
        "SELECT * FROM candidatos ORDER BY id DESC"
    ).fetchall()

    conexao.close()

    return render_template(
        "candidatos.html",
        candidatos=candidatos
    )



def salvar_documento(arquivo):
    if arquivo and arquivo.filename:
        nome_seguro = secure_filename(arquivo.filename)
        extensao = nome_seguro.rsplit(".", 1)[-1].lower()

        if extensao not in ["pdf", "png", "jpg", "jpeg"]:
            return None

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        nome_unico = f"{uuid.uuid4().hex}_{nome_seguro}"
        caminho = os.path.join(app.config["UPLOAD_FOLDER"], nome_unico)

        arquivo.save(caminho)
        return nome_unico

    return None


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    email = request.form.get("email")
    nacionalidade = request.form.get("nacionalidade")
    idade = request.form.get("idade")
    cpf = request.form.get("cpf")

    passaporte = salvar_documento(request.files.get("passaporte"))
    identificacao = salvar_documento(request.files.get("identificacao"))

    conexao = conectar_banco()

    conexao.execute("""
        INSERT INTO candidatos
        (nome, telefone, email, nacionalidade, idade, cpf, passaporte, identificacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome,
        telefone,
        email,
        nacionalidade,
        int(idade) if idade else None,
        cpf,
        passaporte,
        identificacao
    ))

    conexao.commit()
    conexao.close()

    return redirect("/")



if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)
