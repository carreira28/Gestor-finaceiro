from flask import Flask, render_template, request, redirect, session, send_from_directory, jsonify
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'segredo_muito_forte'
app.config['UPLOAD_FOLDER'] = 'static'

def conexao_bd():
    return mysql.connector.connect(
        host="db4free.net",
        user="rcarreira",
        password="Aluno21491",
        database="db_rcarreira"
    )

def obter_nome_utilizador(login_id):
    conexao = conexao_bd()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT nome FROM login WHERE id = %s", (login_id,))
    user = cursor.fetchone()
    conexao.close()
    return user["nome"] if user else "Utilizador"

def obter_dados_editar(login_id):
    conexao = conexao_bd()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT titulo, logo_nome, cor_titulo, cor_header, fundo_nome FROM editar WHERE login_id = %s", (login_id,))
    dados = cursor.fetchone()
    conexao.close()
    return dados

def verificar_nivel(login_id, nivel_requerido):
    conexao = conexao_bd()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT nivel FROM login WHERE id = %s", (login_id,))
    user = cursor.fetchone()
    conexao.close()
    return user and user["nivel"] >= nivel_requerido

@app.context_processor
def inject_verificar_nivel():
    def verificar_nivel_template(login_id, nivel_requerido):
        return verificar_nivel(login_id, nivel_requerido)
    return dict(verificar_nivel=verificar_nivel_template)

# Rotas principais
@app.route("/")
def index():
    if "login_id" not in session:
        return redirect("/login")

    dados = obter_dados_editar(session["login_id"])
    nome_utilizador = obter_nome_utilizador(session["login_id"])
    return render_template("index.html", 
        titulo=dados["titulo"],
        logo_nome=dados["logo_nome"],
        cor_titulo=dados["cor_titulo"],
        cor_header=dados.get("cor_header", "#333333"),
        fundo_nome=dados.get("fundo_nome", "default_fundo.png"),
        nome=nome_utilizador)


@app.route("/gestor_empresarial")
def gestor_empresarial():
    if "login_id" not in session:
        return redirect("/login")
    
    dados = obter_dados_editar(session["login_id"])
    nome_utilizador = obter_nome_utilizador(session["login_id"])
    return render_template("gestor_empresarial.html", 
        titulo=dados["titulo"], 
        logo_nome=dados["logo_nome"], 
        cor_titulo=dados["cor_titulo"],
        cor_header=dados.get("cor_header", "#333333"),

        fundo_nome=dados.get("fundo_nome", "default_fundo.png"),
        nome=nome_utilizador)


@app.route("/gestor_pessoal")
def gestor_pessoal():
    if "login_id" not in session:
        return redirect("/login")

    dados = obter_dados_editar(session["login_id"])
    nome_utilizador = obter_nome_utilizador(session["login_id"])
    return render_template("gestor_pessoal.html", 
        titulo=dados["titulo"], 
        logo_nome=dados["logo_nome"], 
        cor_titulo=dados["cor_titulo"],
        cor_header=dados.get("cor_header", "#333333"),
        fundo_nome=dados.get("fundo_nome", "default_fundo.png"),
        nome=nome_utilizador)


# Rotas de autenticação
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        conexao = conexao_bd()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id FROM login WHERE nome = %s AND email = %s", (nome, email))
        user = cursor.fetchone()
        conexao.close()
        if user:
            session["login_id"] = user["id"]
            return redirect("/")
        return "Login inválido"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/criar_conta", methods=["GET", "POST"])
def criar_conta():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        conexao = conexao_bd()
        cursor = conexao.cursor()
        
        # Verificar se email já existe
        cursor.execute("SELECT id FROM login WHERE email = %s", (email,))
        if cursor.fetchone():
            conexao.close()
            return "Email já está em uso."

        # Criar nova conta com nível padrão 1
        cursor.execute("INSERT INTO login (nome, email, nivel) VALUES (%s, %s, %s)", 
                      (nome, email, 1))  # Nível 1 por padrão
        login_id = cursor.lastrowid
        cursor.execute("INSERT INTO editar (login_id, titulo, logo_nome, cor_titulo) VALUES (%s, %s, %s, %s)", 
                      (login_id, "Escolher Nome do Gestor", "default_logo.png", "#007bff"))
        conexao.commit()
        conexao.close()
        return redirect("/login")
    return render_template("registo.html")

# Rotas de edição
@app.route("/editar", methods=["GET", "POST"])
def editar():
    if "login_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        novo_titulo = request.form["titulo"]
        logo_file = request.files["logo"]
        fundo_file = request.files["fundo"]

        dados_atuais = obter_dados_editar(session["login_id"])
        logo_nome = logo_file.filename if logo_file and logo_file.filename else dados_atuais["logo_nome"]
        fundo_nome = fundo_file.filename if fundo_file and fundo_file.filename else dados_atuais.get("fundo_nome", "default_fundo.png")

        if logo_file and logo_file.filename:
            logo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_nome))
        
        if fundo_file and fundo_file.filename:
            fundo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fundo_nome))

        conexao = conexao_bd()
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE editar 
            SET titulo = %s, logo_nome = %s, fundo_nome = %s 
            WHERE login_id = %s
        """, (novo_titulo, logo_nome, fundo_nome, session["login_id"]))
        conexao.commit()
        conexao.close()
        return redirect("/")

    dados = obter_dados_editar(session["login_id"])
    return render_template("editar.html", titulo=dados["titulo"], logo_nome=dados["logo_nome"])


@app.route("/salvar_cores", methods=["POST"])
def salvar_cores():
    if "login_id" not in session:
        return jsonify({"success": False, "error": "Não autenticado"}), 401
    
    try:
        cor_titulo = request.form.get("cor_titulo", "#007bff")
        cor_header = request.form.get("cor_header", "#333333")
        conexao = conexao_bd()
        cursor = conexao.cursor()
        cursor.execute("UPDATE editar SET cor_titulo = %s, cor_header = %s WHERE login_id = %s", 
        (cor_titulo, cor_header, session["login_id"]))
        conexao.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

# Rotas para a agenda
@app.route("/api/eventos", methods=["GET", "POST"])
def eventos():
    if "login_id" not in session:
        return jsonify({"error": "Não autenticado"}), 401
    
    try:
        conexao = conexao_bd()
        cursor = conexao.cursor(dictionary=True)
        
        if request.method == "GET":
            cursor.execute("""
                SELECT id, titulo, descricao, 
                       data_inicio, data_fim, localizacao, 
                       lembrete, data_lembrete, cor_evento 
                FROM eventos 
                WHERE login_id = %s
            """, (session["login_id"],))
            eventos = cursor.fetchall()
            return jsonify(eventos)
        
        elif request.method == "POST":
            dados = request.get_json()
            print("Dados recebidos:", dados)  # Debug
            
            cursor.execute("""
                INSERT INTO eventos 
                (login_id, titulo, descricao, data_inicio, data_fim, 
                 localizacao, lembrete, data_lembrete, cor_evento)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session["login_id"],
                dados.get("titulo"),
                dados.get("descricao"),
                dados.get("data_inicio"),
                dados.get("data_fim"),
                dados.get("localizacao"),
                dados.get("lembrete", False),
                dados.get("data_lembrete"),
                dados.get("cor_evento", "#3788d8")
            ))
            conexao.commit()
            evento_id = cursor.lastrowid
            return jsonify({"success": True, "id": evento_id}), 201
            
    except mysql.connector.Error as err:
        print("Erro MySQL:", err)  # Debug
        return jsonify({"error": str(err)}), 500
    except Exception as e:
        print("Erro geral:", e)  # Debug
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

@app.route("/api/eventos/<int:evento_id>", methods=["PUT", "DELETE"])
def evento_individual(evento_id):
    if "login_id" not in session:
        return jsonify({"error": "Não autenticado"}), 401
    
    conexao = conexao_bd()
    cursor = conexao.cursor(dictionary=True)
    
    if request.method == "PUT":
        # Atualizar evento
        dados = request.get_json()
        cursor.execute("""
            UPDATE eventos 
            SET titulo = %s, descricao = %s, data_inicio = %s, 
                data_fim = %s, localizacao = %s, lembrete = %s, 
                data_lembrete = %s, cor_evento = %s
            WHERE id = %s AND login_id = %s
        """, (
            dados.get("titulo"),
            dados.get("descricao"),
            dados.get("data_inicio"),
            dados.get("data_fim"),
            dados.get("localizacao"),
            dados.get("lembrete", False),
            dados.get("data_lembrete"),
            dados.get("cor_evento", "#3788d8"),
            evento_id,
            session["login_id"]
        ))
        conexao.commit()
        conexao.close()
        return jsonify({"success": True})
    
    elif request.method == "DELETE":
        # Eliminar evento
        cursor.execute("DELETE FROM eventos WHERE id = %s AND login_id = %s", (evento_id, session["login_id"]))
        conexao.commit()
        conexao.close()
        return jsonify({"success": True})

@app.route("/gestor_pessoal/agenda")
def agenda():
    if "login_id" not in session:
        return redirect("/login")
    
    dados = obter_dados_editar(session["login_id"])
    nome_utilizador = obter_nome_utilizador(session["login_id"])
    return render_template("agenda.html", 
        titulo=dados["titulo"], 
        logo_nome=dados["logo_nome"], 
        cor_titulo=dados["cor_titulo"],
        cor_header=dados.get("cor_header", "#333333"),
        fundo_nome=dados.get("fundo_nome", "default_fundo.png"),
        nome=nome_utilizador)

# Rotas para comentários
@app.route("/comentarios", methods=["GET", "POST"])
def comentarios():
    if "login_id" not in session:
        return redirect("/login")
    
    conexao = conexao_bd()
    cursor = conexao.cursor(dictionary=True)
    
    if request.method == "POST":
        comentario = request.form["comentario"]
        cursor.execute("INSERT INTO comentarios (login_id, comentario) VALUES (%s, %s)", 
                      (session["login_id"], comentario))
        conexao.commit()
    
    # Obter todos os comentários com os nomes dos usuários
    cursor.execute("""
        SELECT c.id, c.comentario, c.data_comentario, l.nome 
        FROM comentarios c
        JOIN login l ON c.login_id = l.id
        ORDER BY c.data_comentario DESC
    """)
    comentarios = cursor.fetchall()
    
    conexao.close()
    
    dados = obter_dados_editar(session["login_id"])
    nome_utilizador = obter_nome_utilizador(session["login_id"])
    
    return render_template("comentarios.html", 
        titulo=dados["titulo"], 
        logo_nome=dados["logo_nome"], 
        cor_titulo=dados["cor_titulo"],
        cor_header=dados.get("cor_header", "#333333"),
        fundo_nome=dados.get("fundo_nome", "default_fundo.png"),
        nome=nome_utilizador,
        comentarios=comentarios)

@app.route("/admin/comentarios")
def admin_comentarios():
    if "login_id" not in session:
        return redirect("/login")
    
    if not verificar_nivel(session["login_id"], 2):
        return "Acesso não autorizado", 403
    
    conexao = conexao_bd()
    cursor = conexao.cursor(dictionary=True)
    
    # Obter todos os comentários com informações dos usuários
    cursor.execute("""
        SELECT c.id, c.comentario, c.data_comentario, l.nome, l.email, l.id as user_id, l.nivel
        FROM comentarios c
        JOIN login l ON c.login_id = l.id
        ORDER BY c.data_comentario DESC
    """)
    comentarios = cursor.fetchall()
    
    conexao.close()
    
    dados = obter_dados_editar(session["login_id"])
    nome_utilizador = obter_nome_utilizador(session["login_id"])
    
    return render_template("admin_comentarios.html", 
        titulo=dados["titulo"], 
        logo_nome=dados["logo_nome"], 
        cor_titulo=dados["cor_titulo"],
        cor_header=dados.get("cor_header", "#333333"),
        fundo_nome=dados.get("fundo_nome", "default_fundo.png"),
        nome=nome_utilizador,
        comentarios=comentarios)

@app.route("/admin/comentarios/<int:comentario_id>/delete", methods=["POST"])
def admin_deletar_comentario(comentario_id):
    if "login_id" not in session:
        return redirect("/login")
    
    if not verificar_nivel(session["login_id"], 2):
        return "Acesso não autorizado", 403
    
    conexao = conexao_bd()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM comentarios WHERE id = %s", (comentario_id,))
    conexao.commit()
    conexao.close()
    
    return redirect("/admin/comentarios")

# Serviço PWA
@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')

if __name__ == "__main__":
    app.run(debug=True)