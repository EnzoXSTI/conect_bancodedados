from flask import Flask, render_template, request, flash, redirect, url_for
import fdb

app = Flask(__name__)
app.secret_key = 'senhasupersecretaquenemumhakeralemaodescobre'

# Configuração do banco de dados
host = 'localhost'
database = r'C:\Users\Aluno\BANCO\BANCO.fdb'
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
            "INSERT INTO livro (titulo, autor, ano_publicacao) VALUES (?, ?, ?)",
            (titulo, autor, ano_publicacao)
        )
        con.commit()

    finally:
        cursor.close()
    flash('O livro foi cadastrado com sucesso!')
    return redirect(url_for('index'))


@app.route('/atualizar')
def atualizar():
    return render_template('editar.html', titulo='Editar livro')


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cusor = con.cursor()
    cusor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livro WHERE id_livro = ?", (id,))
    livro = cusor.fetchone()

    if not livro:
        cusor.close()
        flash('Livro não encontrado.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicacao = request.form['ano_publicacao']
        
        cusor.execute("UPDATE livro SET titulo = ?, autor = ?, ano_publicacao = ? WHERE id_livro = ?",
                      (titulo, autor, ano_publicacao, id))
        con.commit()
        cusor.close()
        flash('Livro atualizado com sucesso!')
        return redirect(url_for('index'))
    cusor.close()
    return render_template('editar.html', livro=livro , titulo='Editar livro')



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

        cursor.execute('INSERT INTO USUARIOS (NOME, EMAIL, SENHA) VALUES (?, ?, ?)',
                       (nome, email, senha))
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

        cursor = con.cursor()
        cursor.execute("UPDATE USUARIOS SET NOME = ?, EMAIL = ?, SENHA = ? WHERE ID_USUARIO = ?",
                       (nome, email, senha, id))
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

# Login de usuário
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # O resto do seu código POST permanece igual
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM USUARIOS WHERE EMAIL = ? AND SENHA = ?', (email, senha))
        if cursor.fetchone():
            flash('Login realizado com sucesso.')
            return redirect(url_for('usuarios'))
        else:
            flash('Email ou senha incorretos.')
            return render_template('login.html')
    finally:
        cursor.close()



if __name__ == '__main__':
    app.run(debug=True)
