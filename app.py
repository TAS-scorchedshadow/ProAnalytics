from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = "super secret"
bootstrap = Bootstrap(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

def bruh():
    return "Hello dylan"


if __name__ == '__main__':
    app.run()
