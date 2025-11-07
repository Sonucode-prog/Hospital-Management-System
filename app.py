from flask import Flask, render_template, request, redirect, url_for
import module



app = Flask(__name__)



@app.route("/")
def login():
    return render_template("login.html")

@app.route("/registration")
def registration():
    return render_template("registration.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")



if __name__ == "__main__":
    app.run(debug=True)
    
