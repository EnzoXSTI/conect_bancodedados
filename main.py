from flask import Flask, render_template, request, flash, redirect, url_for, session, send_from_directory
from flask_bcrypt import generate_password_hash, check_password_hash
import fdb


app = Flask(__name__)
app.secret_key = 'senhasupersecretaquenemumhakeralemaodescobre'

# Configuração do banco de dados

host = 'localhost'
database = r'C:\Users\Aluno\BANCO\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password)


# ROTAS RELACIONADAS A LIVROS

# Rota principal - listar livros

@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livro")
    livros = cursor.fetchall()
    cursor.close()
    return render_template('index.html', livros=livros)


# Rota para formulário de novo livro
@app.route('/novo')
def novo():
    if 'id_usuario' not in session:
        flash("precisa estar logado.", "erro")
        return redirect(url_for('login'))
    return render_template('novo.html', titulo='novo livro')


# Rota para criar novo livro
@app.route('/criar', methods=["POST"])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    cursor = con.cursor()
    try:
        # Verificar se o livro já existe
        cursor.execute('SELECT 1 FROM livro WHERE titulo = ?', (titulo,))
        if cursor.fetchone():
            flash('Esse livro já está cadastrado.')
            return redirect(url_for('novo'))

        # Inserir novo livro
        cursor.execute(
            "INSERT INTO livros (TITULO, AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?) RETURNING id_livro",
            (titulo, autor, ano_publicacao)
        )

        id_livro = cursor.fetchone()[0]
        con.commit()

        arquivo = request.files['arquivo']
        arquivo.save(f'uploads/capa{id_livro}.jpg')
    finally:
        cursor.close()
        flash('O livro foi cadastrado com sucesso!')
        return redirect(url_for('index'))


@app.route('/atualizar')
def atualizar():
    # A rota '/atualizar' não está sendo usada e não faz sentido sem um formulário ou lógica. Você pode removê-la ou adaptá-la.
    return render_template('editar.html', titulo='Editar livro')


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livro WHERE id_livro = ?", (id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash('Livro não encontrado.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicacao = request.form['ano_publicacao']

        cursor.execute("UPDATE livro SET titulo = ?, autor = ?, ano_publicacao = ? WHERE id_livro = ?",
                       (titulo, autor, ano_publicacao, id))
        con.commit()
        cursor.close()
        flash('Livro atualizado com sucesso!')
        return redirect(url_for('index'))

    cursor.close()
    return render_template('editar.html', livro=livro, titulo='Editar livro')


@app.route('/deletar/<int:id>', methods=('POST',))
def deletar(id):
    cursor = con.cursor()  # Abre o cursor

    try:
        cursor.execute('DELETE FROM livro WHERE id_livro = ?', (id,))
        con.commit()
        flash('Livro excluído com sucesso!', 'success')
    except Exception as e:
        con.rollback()
        flash('Erro ao excluir o livro.', 'error')
    finally:
        cursor.close()

    return redirect(url_for('index'))


# ROTAS RELACIONADAS A USUÁRIOS

# Listagem de usuários
@app.route('/usuarios')
def usuarios():
    cursor = con.cursor()
    cursor.execute("SELECT ID_USUARIO, NOME, EMAIL, SENHA FROM USUARIOS")
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('usuarios.html', usuarios=usuarios)


# Formulário de novo usuário
@app.route('/novousuario')
def novousuario():
    return render_template('novousuario.html', titulo="Novo Usuário")


# Criação de novo usuário
@app.route('/criarusuario', methods=["POST"])
def criarusuario():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM USUARIOS WHERE EMAIL = ?', (email,))
        if cursor.fetchone():
            flash('Esse usuário já está cadastrado.')
            return redirect(url_for('novousuario'))
        senha_cripto = generate_password_hash(senha).decode('utf-8')
        cursor.execute('INSERT INTO USUARIOS (NOME, EMAIL, SENHA) VALUES (?, ?, ?)',
                       (nome, email, senha_cripto))
        con.commit()
        flash('Usuário cadastrado com sucesso.')
    finally:
        cursor.close()

    return redirect(url_for('usuarios'))


# Edição de usuário
@app.route('/editarusuario/<int:id>', methods=['GET', 'POST'])
def editarusuario(id):
    cursor = con.cursor()
    cursor.execute("SELECT ID_USUARIO, NOME, EMAIL, SENHA FROM USUARIOS WHERE ID_USUARIO = ?", (id,))
    usuario = cursor.fetchone()
    cursor.close()

    if not usuario:
        flash("Usuário não encontrado.")
        return redirect(url_for('usuarios'))

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if senha:
            senha_cripto = generate_password_hash(senha).decode('utf-8')
        else:
            senha_cripto = usuario[3]

        cursor = con.cursor()
        cursor.execute("UPDATE USUARIOS SET NOME = ?, EMAIL = ?, SENHA = ? WHERE ID_USUARIO = ?",
                       (nome, email, senha_cripto, id))
        con.commit()
        cursor.close()
        flash("Usuário atualizado com sucesso.")
        return redirect(url_for('usuarios'))

    return render_template('editarusuario.html', usuario=usuario, titulo='Editar Usuário')


# Deletar usuário
@app.route('/deletarusuario/<int:id>', methods=['POST'])
def deletarusuario(id):
    cursor = con.cursor()
    cursor.execute("DELETE FROM USUARIOS WHERE ID_USUARIO = ?", (id,))
    con.commit()
    cursor.close()
    flash("Usuário excluído com sucesso.")
    return redirect(url_for('usuarios'))


@app.route('/nlogin')
def nlogin():
    return render_template('login.html', titulo="novo usuario")
# Login de usuário
@app.route('/login', methods=["POST"])
def login():
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()

    cursor.execute('SELECT ID_USUARIO, EMAIL, SENHA FROM USUARIOS WHERE EMAIL = ?', [email])
    usuario = cursor.fetchone()
    cursor.close()

    if usuario is None:
        flash('usuario nao encontrado')
        return redirect(url_for('login'))

    senha_hash = usuario[2]

    if check_password_hash(senha_hash, senha):
        flash('usuario logado')
        return redirect(url_for('usuarios'))
    else:
        flash('senha errada')
        return redirect(url_for('nlogin'))


if __name__ == '__main__':
    app.run(debug=True)
