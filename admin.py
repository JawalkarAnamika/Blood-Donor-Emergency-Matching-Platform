from flask import Blueprint,render_template,request,redirect,session
import pymysql
from get_db_connection import get_db_connection

admin_bp=Blueprint("admin",__name__)
@admin_bp.route("/admin",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"].strip()
        p=request.form["password"].strip()
        db=get_db_connection()
        cur=db.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM admins WHERE username=%s AND password=%s",
                    (u,p))
        admin=cur.fetchone()
        if admin:
            session["admin"]=admin["admin_id"]
            return redirect("/admin/dashboard")
        else:
            return render_template("admin_login.html",error="Invalid username or Password")
    return render_template("admin_login.html")
        
@admin_bp.route("/admin/dashboard")
def dashboard():
    db=get_db_connection()
    cur=db.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT COUNT(*)c FROM donors")
    donors=cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*)c FROM requests")
    requests=cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*)c FROM matches")
    matches=cur.fetchone()["c"]
    return render_template("admin_dashboard.html",donors=donors,requests=requests,matches=matches)

@admin_bp.route("/admin/donors")
def donors():
    db=get_db_connection()
    cur=db.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM donors")
    return render_template("donors.html",donors=cur.fetchall())

@admin_bp.route("/admin/verify/<int:did>")
def verify(did):
    db=get_db_connection()
    cur=db.cursor()
    cur.execute("UPDATE donors SET verified=1 WHERE donor_id=%s",(did,))
    db.commit()
    return redirect("/admin/donors")



@admin_bp.route("/admin/requests")
def view_requests():
    db=get_db_connection()
    cur=db.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT * FROM requests")
    return render_template("requests_admin.html",requests=cur.fetchall())  
