from flask import Flask, render_template
import fdb

app = Flask(__name__)

host = 'localhost'
database = r'C:\Users\Aluno\Downloads\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("select id_livro,titulo,autor,ano_publicacao from livro")
    livros = cursor.fetchall()
    cursor.close()

    return render_template('livros.html', livros=livros)

if __name__ == '__main__':
        app.run(debug=True)