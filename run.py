from flask import Flask, request, render_template, url_for, redirect, session
import sqlite3
import datetime
from functools import wraps
import secrets


app = Flask(__name__)

DBNAME = "gunluk.db"
curDateTime = datetime.datetime.now() #rookie mistake. i was using this in /ekle. commented it out as a reminder

app.secret_key = secrets.token_hex(32)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        return render_template("login.html")
    return decorated_function


@app.route('/')
@login_required
def index():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute("select id, tarih, icerik from gunluk order by id desc")
    data = c.fetchall()
    output = []
    for d in data:
        mydict = {}
        mydict['post_id'] = d[0]
        mydict['post_date'] = d[1].split(" ")[0]
        mydict['post_hour'] = d[1].split(" ")[-1].split(".")[0]
        mydict['text'] = d[2][0:10]
        output.append(mydict)
    print(output)
    return render_template("liste.html", data=output)



@app.route('/login', methods=['POST'])
def login():
    if 'user' in session:
        return redirect(url_for("index"))
    user = request.form['username']
    password = request.form['password']
    if user == 'test' and password == 'test':
        session['user'] = user
        return redirect(url_for('index'))
    else:
        return "404"


@app.route('/ekle', methods=['POST'])
@login_required
def ekle():
    icerik = request.form['icerik']
    #tarih = curDateTime  #does not recalculate. tarih was set when the app is run.
    tarih = datetime.datetime.now()
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute("insert into gunluk(tarih, icerik) values(?, ?)", (tarih, icerik))
    conn.commit()
    return redirect(url_for("index"))



@app.route('/oku/<post_id>')
@login_required
def oku(post_id):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute("select id, tarih, icerik from gunluk where id = %s" % post_id)
    data = c.fetchall()
    mydict = {}
    mydict['post_id'] = data[0][0]
    mydict['post_date'] = str(data[0][1]).split(" ")[0]
    mydict['post_hour'] = str(data[0][1]).split(" ")[-1].split(".")[0]
    mydict['post_icerik'] = data[0][2].replace("\r\n","<br>")
    return render_template("read.html", data=mydict)




@app.route('/sil/<post_id>')
@login_required
def sil(post_id):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute('delete from gunluk where id = %s' % post_id)
    conn.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
