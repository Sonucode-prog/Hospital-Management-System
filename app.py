# import python_file.module as module
from flask import Flask, redirect, url_for

app=None

def created_app():                                   
    app = Flask(__name__)
    app.debug=True
    app.app_context().push() 
    return app
    
    
app= created_app()
import app1
    
    
if __name__ == "__main__":
    app.run(debug=True)
    
