from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Database model
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<QuizResult {self.username} - {self.score}%>'


# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def show_quiz():
    if request.method == 'POST':
        # Retrieve form data
        answers = {
            'question1': request.form.get('question1'),
            'question2': request.form.get('question2'),
            'question3': request.form.get('question3'),
            'question4': request.form.get('question4'),
            'question5': request.form.get('question5'),
        }

        # Define correct answers
        correct_answers = {
            'question1': 'scikit-learn',
            'question2': 'tensorflow',
            'question3': 'natural-language-processing',
            'question4': 'image-recognition',
            'question5': 'k-means',
        }

        # Calculate score
        total_questions = len(correct_answers)
        score = sum(1 for q in correct_answers if answers.get(q) == correct_answers[q])
        percentage_score = (score / total_questions) * 100

        # Save result to database
        username = request.form.get('username', 'Anonymous')  # Default to 'Anonymous' if not provided
        result = QuizResult(username=username, score=percentage_score)
        db.session.add(result)
        db.session.commit()

        # Redirect to result page (or you can render a template to show results directly)
        return redirect(url_for('result', username=username, score=percentage_score))

        # Fetch the best score
    best_score_record = QuizResult.query.order_by(QuizResult.score.desc()).first()
    best_score = best_score_record.score if best_score_record else None
    best_score_author = best_score_record.username if best_score_record else None

    return render_template('quiz_template.html', best_score=best_score, best_score_author=best_score_author)


@app.route('/result')
def result():
    username = request.args.get('username', 'Anonymous')
    score = request.args.get('score', 0)
    return render_template('result_template.html', username=username, score=score)


@app.route('/all_scores')
def all_scores():
    scores = QuizResult.query.order_by(QuizResult.score.desc()).all()
    return render_template('all_scores_template.html', scores=scores)

