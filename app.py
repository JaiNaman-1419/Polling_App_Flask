from crypt import methods
from datetime import datetime
from random import choices
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Questions(db.Model):
    __tablename__ = 'questions'
    sno = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


class Choices(db.Model):
    __tablename__ = 'choices'
    sno = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question'))
    choice_text = db.Column(db.String(200), nullable=False)
    votes = db.Column(db.Integer, nullable=False)


@app.route('/')
def index_page():
    # return 'Hello World'
    questions_lst = Questions.query.all()
    return render_template('index.html', questions_lst=questions_lst)


@app.route('/poll/<int:sno>', methods={'GET', 'POST'})
def get_poll(sno):
    question = Questions.query.filter_by(sno=sno).first()
    choice_lst = Choices.query.filter_by(question_id=sno).all()
    if (request.method == 'POST'):
        try:
            selected_choice = request.form["choice"]

        except Exception:
            return render_template('poll.html', question=question, error_msg='Please select the choice!', choice_lst=choice_lst)

        else:
            choice = Choices.query.filter_by(sno=selected_choice).first()
            choice.votes = choice.votes+1
            db.session.add(choice)
            db.session.commit()
            return redirect('/')

    return render_template('poll.html', question=question, choice_lst=choice_lst)


@app.route('/result/')
def result_page():
    questions = Questions.query.all()
    choices_lst = Choices.query.all()
    return render_template('result.html', questions=questions, choices_lst=choices_lst)


@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    if number <= 1:
        return singular

    return plural


@app.template_filter('choices')
def return_choices(sno):
    return Choices.query.filter_by(sno=sno).all()


if __name__ == '__main__':
    app.run(debug=True, port=8000)
