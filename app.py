
from database import Question,Score,User
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request, flash, redirect,session
from ar import start_quiz
app = Flask(__name__)
app.secret_key = 'thisisaverysecretkey'

def opendb():
    engine = create_engine("sqlite:///db.sqlite")
    Session = sessionmaker(bind=engine)
    return Session()

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        question = request.form.get('question')
        op1  = request.form.get('op1')
        op2  = request.form.get('op2')
        op3  = request.form.get('op3')
        op4  = request.form.get('op4')
        ans = request.form.get('ans')
        category = request.form.get('category')
        if not question or len(question) < 10:
            flash('Question is required and should be at least 10 characters long', 'danger')
            return redirect('/')
        elif not op1:
            flash('Option 1 is required', 'danger')
            return redirect('/')
        # more like this
        else:
            try:
                db = opendb()
                q = Question(title=question, op1=op1, op2=op2, op3=op3, op4=op4, ans=ans, category=category)
                db.add(q)
                db.commit()
                db.close()
                flash('Question added successfully', 'success')
                return redirect('/')
            except Exception as e:
                print("---------------->",e)
                flash("Question could not be added, check console for logs",'danger')

    return render_template('index.html') 
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/result')
def result():
    db=opendb()
    ques=db.query(Question).all()
    db.close()
    return render_template('result.html',ques=ques)

@app.route('/delete/<int:id>')
def delete(id):
    sess=opendb()
    try:
        sess.query(Question).filter(Question.id==id).delete()
        sess.commit()
        sess.close()
        return redirect('/result')
    except Exception as e:
        return f"There was a problem while deleting {e}"

@app.route('/play', methods=['GET','POST'])
def play():
    if request.method == "POST":
        category = request.form.get("category")
        db = opendb()
        questions = db.query(Question).filter(Question.category==category)
        score = start_quiz(questions)
        db.add(Score(session.get('id',1),score))
        db.commit()
        db.close()
        session['score'] = score
        return redirect('/result')
    return render_template('play.html')

@app.route('/result')
def result():
    return render_template('result.html')

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000, debug=True)