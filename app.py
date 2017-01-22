from flask import Flask
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from datetime import datetime
import watson
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import dateparser

import sqlite3

EMOTIONS = ['Joy', 'Sadness', 'Anger', 'Disgust', 'Fear']

EMOTIONS_COLORS = {
    'Joy': 'rgba(255, 239, 44, 0.5)',
    'Sadness': 'rgba(44, 181, 255, 0.5)',
    'Anger': 'rgba(255, 76, 44, 0.5)',
    'Disgust': 'rgba(89, 191, 100, 0.5)',
    'Fear': 'rgba(207, 82, 240, 0.5)'
}

app = Flask(__name__)

class ReusableForm(Form):
    name = TextAreaField('Name:', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def diary():
    form = ReusableForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        name = request.form['name']
        with open('data.txt', 'a') as outfile:
            outfile.write(name + '\n')
        if form.validate():
            # Save the comment here.
            compute_and_log_sentiment(name)
            return redirect(url_for('diary'))
        else:
            return 'All the form fields are required. '
    else:
        return render_template('diary.html', form=form)

@app.route("/emotions", methods=['GET'])
def graphs():
    conn = sqlite3.connect('sqlite3')
    cur = conn.cursor()
    data = cur.execute('SELECT * FROM emotions;').fetchall()
    conn.close()
    graph_data = [[] for emotions in EMOTIONS]
    positivity_data = []
    for datum in data:
        emotion_data = datum[1:-2]
        positivity = datum[-2]
        timestamp = datum[-1].split(' ')[0]
        for i in range(len(EMOTIONS)):
            graph_data[i].append(
                {
                    'date': timestamp,
                    'value': emotion_data[i]
                }
            )
        positivity_data.append(
            {
                'date': timestamp,
                'value': positivity
            }
        )
    view_data = {}
    for i in range(len(EMOTIONS)):
        emotion = EMOTIONS[i]
        view_data[emotion.lower()] = graph_data[i]
    view_data['positivity'] = positivity_data
    return render_template('scatter.html', bg=get_bg(), **view_data)

def get_bg():
    conn = sqlite3.connect('sqlite3')
    cur = conn.cursor()
    data = cur.execute('SELECT * FROM emotions;').fetchall()
    max_entry = max(data, key=lambda entry: dateparser.parse(entry[-1]))
    max_index = max(list(range(len(EMOTIONS))), key=lambda i: max_entry[1:-2][i])
    emotion = EMOTIONS[max_index]
    return EMOTIONS_COLORS[emotion]

@app.route("/wordcloud", methods=['GET'])
def wc():
    text = open('data.txt').read()
    wordcloud = WordCloud().generate(text)
    default_colors = wordcloud.to_array()
    plt.title("Your WordCloud")
    wordcloud.to_file("uploads/wc.png")
    filename = 'wc.png'
    return render_template('wordcloud.html', bg=get_bg(), filename=filename)

@app.route("/uploads/<filename>")
def send_file(filename):
    return send_from_directory('uploads', filename)

def compute_and_log_sentiment(entry):
    sentiment_response = watson.get_text_sentiment(entry)
    sentiment_score = watson.get_text_sentiment_score(entry)[1]
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
        str(sentiment_score),
        timestamp
    )
    conn = sqlite3.connect('sqlite3')
    cur = conn.cursor()
    cur.execute("""INSERT INTO emotions VALUES(?,?,?,?,?,?,?,?)""", data)
    conn.commit()


if __name__ == "__main__":
    app.run()
