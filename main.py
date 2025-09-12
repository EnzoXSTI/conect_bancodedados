from flask import Flask, render_template, request, flash, redirect, url_for
import fdb

app = Flask(__name__)
app.secret_key = 'chaveultrasecretaparaquenemumrakeralemaoinvada'  # Necessário para usar flash

# Configuração do banco
host = 'localhost'
database = r'C:\Users\Aluno\Downloads\BANCO\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'

# Conexão com o banco
con = fdb.connect(host=host, database=database, user=user, password=password)

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

# Iniciar o servidor
if __name__ == '__main__':
    app.run(debug=True)
