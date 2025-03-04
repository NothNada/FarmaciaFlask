from flask import Flask,session,request,redirect,url_for,render_template,g,jsonify
from sqlite3 import connect
from uuid import uuid4
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = b'12345678'
DATABASE = 'banco.db'

def get_db():
    if 'db' not in g:
        g.db = connect(DATABASE)
    return g.db

@app.before_request
def before_request():
    get_db()

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db',None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        verifica = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios';")
        if not verifica.fetchone():
            db.execute("CREATE TABLE usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, senha TEXT)")
        verifica.close()

        verifica = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produtos';")
        print("foi2")
        if not verifica.fetchone():
            print("foi")
            db.execute("CREATE TABLE produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, imagem TEXT, valor INTEGER, desc TEXT)")
        verifica.close()
init_db()

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html',usuario=session['username'])
    return render_template('index.html',usuario='Nao logado')

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username']
        senha = request.form['password']
        print(usuario)
        print(senha)

        db = get_db()
        consulta = db.execute('SELECT * FROM usuarios')
        for dados in consulta.fetchall():
            print(f'id {dados[0]} - usuario {dados[1]} - senha {dados[2]}')
            if dados[1] == usuario and dados[2] == senha:
                session['username'] = usuario
                return redirect(url_for('index'))
            elif dados[1] == usuario:
                return "Senha Errada!"
        db.execute(f"INSERT INTO usuarios (nome,senha) VALUES ('{usuario}','{senha}')")
        db.commit()
        session['username'] = usuario
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/edit/',methods=['GET','POST'])
def editar():
    if 'username' in session:
        if session['username'] == 'admin':
            if request.method == 'GET':
                return render_template('admin.html')
            else:
                file = request.files['imagem']

                if file.filename == '':
                    return 'Selecione um arquivo'
                
                nome_unico = str(uuid4()) + secure_filename(file.filename)

                file.save('static/imgs/'+nome_unico)

                db = get_db()
                db.execute(f"INSERT INTO produtos (imagem,valor,desc) VALUES ('{nome_unico}','{request.form['valor']}','{request.form['desc']}')")
                db.commit()
                return redirect('/edit/')
    return 'Nao'

@app.route('/prods/')
def prods():
    db = get_db()
    consulta = db.execute('SELECT * FROM produtos')
    imagems = []
    valores = []
    descs = []
    qntd = 0
    for dados in consulta.fetchall():
        qntd += 1
        imagems.append(dados[1])
        valores.append(dados[2])
        descs.append(dados[3])
    return jsonify({'imagem':imagems,'descricao':descs,'valor':valores,'qnts':qntd})

    

@app.route('/logout')
def logout():
    session.pop('username','')
    return redirect(url_for('index'))