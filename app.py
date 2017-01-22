from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route("/")
def diary():
    return render_template('templates/diary.html', name=name)

if __name__ == "__main__":
    app.run()
