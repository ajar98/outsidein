from flask import Flask
from flask import Flask, render_template, flash, request, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from datetime import datetime
import watson

import sqlite3

app = Flask(__name__)

class ReusableForm(Form):
    name = TextAreaField('Name:', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def diary():
    form = ReusableForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        name = request.form['name']
        print(name)
        if form.validate():
            # Save the comment here.
            compute_and_log_sentiment(name)
            return redirect(url_for('diary'))
        else:
            return 'All the form fields are required. '
    else:
        return render_template('diary.html', form=form)

def compute_and_log_sentiment(entry):
    sentiment_response = watson.get_text_sentiment(entry)
    sentiment_score = watson.get_text_sentiment_score(entry)
    emotions = watson.avg_sentiment(sentiment_response)
    most_extreme_sentence = watson.max_sentiment(sentiment_response)[0]
    timestamp = str(datetime.now())
    data = (
        most_extreme_sentence,
        emotions['Joy'],
        emotions['Anger'],
        emotions['Sadness'],
        emotions['Disgust'],
        emotions['Fear'],
        timestamp
    )
    conn = sqlite3.connect('sqlite3')
    cur = conn.cursor()
    cur.execute("""INSERT INTO emotions VALUES(?,?,?,?,?,?,?)""", data)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    app.run()
