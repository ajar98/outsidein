from flask import Flask
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

app = Flask(__name__)

class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def diary():
    form = ReusableForm(request.form)
    print(form.errors)
    if request.method == 'POST':
        name = request.form['name']
        print(name)

        if form.validate():
            # Save the comment here.
            return name
        else:
            return 'All the form fields are required. '
    else:
        return render_template('diary.html', form=form)

if __name__ == "__main__":
    app.run()
