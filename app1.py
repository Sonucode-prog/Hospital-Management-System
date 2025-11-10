from flask import Flask, render_template, request, redirect, url_for
from flask import current_app as app  #when we run app.py then create proxy(intermediate server) in current_app as app and we can use anywhere
                                       # also avoid circular import error at this place

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        role=request.form.get("role")
        
        if username=="admin" and password=="1" and role=="admin":
            return redirect(url_for("admin"))
        else:
            return render_template("login.html")
    return render_template("login.html")

@app.route("/registration")
def registration():
    return render_template("registration.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/new_doct")
def new_doct():
    return render_template("new_doctor.html")

@app.route("p_history")
def p_history():
    return render_template("patient_history.html")