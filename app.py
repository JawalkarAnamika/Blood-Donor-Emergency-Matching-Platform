from flask import Flask, redirect,render_template, request, url_for
import pymysql
from get_db_connection import get_db_connection
from flask import session 
from matching import compatible,distance
from admin import admin_bp
from flask import session


app=Flask(__name__)
app.secret_key="simple_secret_key"
app.register_blueprint(admin_bp)


@app.route('/')
def home():
    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        data=request.form
        db=get_db_connection()
        cur=db.cursor()
        cur.execute("""INSERT INTO donors(name,email,phone,blood_group,city,latitude,longitude,last_donation_date)VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",(data["name"],data["email"],data["phone"],data["blood_group"],data["city"],data["lat"],data["lng"],data["last_date"]))
        db.commit()
        return "Donor Rgistered Successfully"
    return render_template("register.html")

@app.route("/request")
def request_page():
    return render_template("request.html")

@app.route("/create_request",methods=["GET","POST"])
def create_request():
    if request.method=="GET":
        data=request.args
    else:
        data=request.form
    db=get_db_connection()
    cur=db.cursor()
    cur.execute(""" INSERT INTO requests(requester_name,hospital_name,
                    blood_group,units_required,city,latitude,longitude,
                    urgency, status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'OPEN')
                    """,(data["name"],data["hospital"],data["blood_group"],
                         data["units"],data["city"],data["lat"],data["lng"],
                         data["urgency"]))
    db.commit()
    last_id=cur.lastrowid
    return redirect(f"/match/{last_id}")
    

@app.route("/match/<int:rid>")
def match_donors(rid):
    db=get_db_connection()
    cur=db.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM requests WHERE request_id=%s",(rid,))
    req=cur.fetchone()
    if not req:
        return "Request not found"
    cur.execute("SELECT * FROM donors WHERE available=1")
    donors=cur.fetchall()
    results=[]
    for d in donors:
        if compatible(d["blood_group"],req["blood_group"]):
            dist=distance(req["latitude"],req["longitude"],d["latitude"],
                          d["longitude"])
            results.append({**d,"distance":round(dist,2)})
            results=sorted(results,key=lambda x:x["distance"])
            return render_template("results.html",donors=results,request=req)
    

@app.route("/users",methods=["POST","GET"])
def show_users():
    if "username" not in session:
        return redirect(url_for("login"))
    conn=get_db_connection()
    if conn is None:
        return"Database error"
    cursor=conn.cursor()


    cursor.execute("SELECT username,password FROM users")
    users=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("users.html",users=users)

@app.route("/add",methods=["GET","POST"])
def add_user():
    error=None
    if request.method=="POST":
        username=request.form["username"].strip()
        password=request.form["password"].strip()
        if not username or not password:
            error="Username and Password cannot be empty."
        else:
            conn=get_db_connection()
            cursor=conn.cursor()
            check_query="SELECT id FROM users WHERE username=%s"
            cursor.execute(check_query,(username,))
            existing_user=cursor.fetchone()

            if existing_user:
                error="Username already exists Choose another"
            else:
                insert_query="INSERT INTO users (username,password)VALUES(%s,%s)"
                cursor.execute(insert_query,(username,password))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for("dashboard"))
            cursor.close()
            conn.close()
    return render_template("add_user.html",error=error)

@app.route("/login",methods=["GET","POST"])
def login():
    error=None
    if request.method=="POST":
        username=request.form["username"].strip()
        password=request.form["password"].strip()
        conn=get_db_connection()
        if conn is None:
            error="Datbase connection error"
        else:
            cursor=conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s",(username,password))
            user=cursor.fetchone()
            cursor.close()
            conn.close()
            if user:
                session["username"]=username
                return redirect(url_for("dashboard"))
            else:
                error="Invalid username or password"
    return render_template("login.html",error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users=cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return render_template("dashboard.html",total_users=total_users)

if __name__=="__main__":
    app.run(debug=True)
