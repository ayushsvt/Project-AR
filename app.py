from database import Question,Score,User
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify, render_template, request, flash, redirect,session
from ar import start_quiz
app = Flask(__name__)
app.secret_key = 'thisisaverysecretkey'

def opendb():
    engine = create_engine("sqlite:///db.sqlite",echo=True)
    Session = sessionmaker(bind=engine)
    return Session()

@app.route('/', methods=['GET','POST'])
def index():
    if 'is_auth' in session and session['is_auth']:
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
    else:
        return redirect('/login')
    
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/display')
def display():
    sess=opendb()
    records= sess.query(Question).all()
    sess.close()
    return render_template('display.html',records=records)


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        if email and password:
            db = opendb()
            user = db.query(User).filter_by(email=email,password=password).first()
            if user:
                session['is_auth'] = True
                session['email'] = user.email
                session['name'] = user.name
                flash('Login successfully','success')
                return redirect('/play')
            else:
                flash('Invalid credentials','danger')
                return redirect('/login')
        else:
            flash('Enter all details','danger')
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'is_auth' in session and session['is_auth']:
        session.pop('is_auth')
        return redirect('/')
    return redirect('/')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        form=request.form
        name=form.get('name')
        email=form.get('email')
        password=form.get('password')
        cpassword=form.get('cpassword')
        print(name,email,password,cpassword)
        if name and email and password and cpassword:
            if password!=cpassword:
                flash('password & confirm password does not match','danger')
                return redirect('/register')
            else:
                db=opendb()
                user = User(name=name,email=email,password=password)
                db.add(user)
                db.commit()
                db.close()
                flash('Register successfully','success')
                return redirect('/')
        else:
            flash('Enter all the details','danger')
            return redirect('/register')
    return render_template('register.html')

@app.route('/score')
def score():
    db=opendb()
    scores=db.query(Score).filter(Score.user_id==session.get('user_id',1)).order_by(Score.score)
    db.close()
    return render_template('score.html',scores=scores)


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
    if 'is_auth' in session and session['is_auth']:
        if request.method == "POST":
            category = request.form.get("category")
            db = opendb()
            print(category)
            questions = db.query(Question).filter(Question.category==category)
            score = start_quiz(questions)
            db.add(Score(user_id=session.get('id',1),score=score))
            db.commit()
            db.close()
            session['score'] = score
            return redirect('/score')
        return render_template('play.html')
    return redirect('/')



if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000, debug=True)
