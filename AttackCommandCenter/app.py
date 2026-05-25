from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import subprocess

app = Flask(__name__)
app.secret_key = 'SECRETKEY123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    credit_card = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    cve_id = db.Column(db.String(50))
    date = db.Column(db.String(50))
    impact = db.Column(db.Text)
    description = db.Column(db.Text)
    technical_details = db.Column(db.Text)
    affected_systems = db.Column(db.Text)
    solution = db.Column(db.Text)
    source = db.Column(db.String(200))
    image_url = db.Column(db.String(200))


with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        users = [
            User(username="admin", password="admin123", email="admin@nestyk.it", credit_card="4111-1111-1111-1111",
                 role="admin"),
            User(username="mario_rossi", password="password123", email="mario@gmail.com",
                 credit_card="5500-0000-0000-0004", role="user"),
            User(username="luca_bianchi", password="luca123", email="luca@gmail.com",
                 credit_card="3400-0000-0000-0000", role="user")
        ]
        for u in users:
            db.session.add(u)
        db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/acc')
def acc_index():
    return render_template('acc/dashboard.html')


@app.route('/acc/login')
def acc_login():
    return render_template('acc/login.html')


@app.route('/acc/dashboard')
def acc_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('acc_login'))
    return render_template('acc/dashboard.html')


@app.route('/acc/profile/<int:user_id>')
def acc_profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('acc_login'))

    query = f"SELECT * FROM user WHERE id = {user_id}"
    user = db.session.execute(text(query)).first()
    if user:
        user_data = User.query.get(user[0])
        return render_template('acc/profile.html', user=user_data)
    return "Utente non trovato", 404


@app.route('/acc/comments', methods=['GET', 'POST'])
def acc_comments():
    if 'user_id' not in session:
        return redirect(url_for('acc_login'))

    if request.method == 'POST':
        content = request.form.get('content')
        username = session.get('username')
        comment = Comment(username=username, content=content)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('acc_comments'))

    all_comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template('acc/comments.html', comments=all_comments)


@app.route('/acc/files')
def acc_files():
    if 'user_id' not in session:
        return redirect(url_for('acc_login'))

    filename = request.args.get('file', 'documenti.txt')
    filepath = f"data/{filename}"

    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return render_template('acc/files.html', content=content, filename=filename)
    except:
        return render_template('acc/files.html', error="File non trovato", filename=filename)
@app.route('/login')
def login_page():
    return render_template('acc/login.html')


@app.route('/do_login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')

    query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
    print(query)
    try:
        result = db.session.execute(text(query)).first()
        if result:
            user = User.query.get(result[0])
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
    except Exception as e:
        print(e)


    return render_template('acc/login.html', error="Credenziali errate")

#DEBUG
@app.route('/debug_check')
def debug_check():
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    result = f"Tabelle nel database: {tables}<br><br>"

    if 'user' in tables:
        users = db.session.execute(text("SELECT * FROM user")).fetchall()
        result += f"Utenti trovati: {len(users)}<br>"
        for u in users:
            result += f"ID: {u[0]}, Username: {u[1]}, Password: {u[2]}<br>"
    else:
        result += "Tabella 'user' non trovata! Devi creare il database."

    return result
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('acc/dashboard.html')



@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    query = f"SELECT * FROM user WHERE id = {user_id}"
    user = db.session.execute(text(query)).first()
    if user:
        user_data = User.query.get(user[0])
        return render_template('acc/profile.html', user=user_data)
    return "Utente non trovato", 404

@app.route('/404', methods=['GET'])
def notfound_page():
    return render_template('acc/404.html')
@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        content = request.form.get('content')
        username = session.get('username')
        comment = Comment(username=username, content=content)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('comments'))

    all_comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template('acc/comments.html', comments=all_comments)


@app.route('/files')
def files():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    filename = request.args.get('file', 'documenti.txt')
    filepath = f"data/{filename}"

    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return render_template('acc/files.html', content=content, filename=filename)
    except:
        return render_template('acc/files.html', error="File non trovato", filename=filename)



@app.route('/ping')
def ping():
    return render_template('acc/ping.html')


@app.route('/do_ping', methods=['POST'])
def do_ping():

    ip = request.form.get('ip', '')

    command = f"ping -c 4 {ip}"

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        output = "Comando timeout (10 secondi)"
    except Exception as e:
        output = f"Errore: {e}"

    return render_template('acc/ping.html', ip=ip, output=output)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)