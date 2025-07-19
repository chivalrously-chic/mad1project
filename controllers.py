from flask import Flask, render_template, request, redirect, url_for
from flask import current_app as app
from backend.models import *
from sqlalchemy import func

@app.route("/")
def home():
   return render_template('login.html')


@app.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        usr = user_info.query.filter_by(name=name, password=password).first()
        if usr and usr.role == 1:
            # return render_template("/admin_dashboard", name=usr.name, users=None)
            return redirect(url_for('admin_dashboard', name=usr.name))
        elif usr and usr.role == 1:
            # Fetch necessary data for the user dashboard
            available_subjects = Subject.query.all()  # Get all subjects
            # You need to create some quiz attempts data here, I am using dummy data
            # Replace this with actual database query
            quiz_attempts = []
            return render_template(
                "user_dashboard.html",
                name=usr.name,
                available_subjects=available_subjects,
                selected_subject_id=None,  # Initial state
                chapters=None,
                quiz_attempts = quiz_attempts
            )
        else:
            return render_template("login.html", msg="Invalid credentials!")
    return render_template("login.html", msg="")

@app.route('/logout')
def logout():
    # Redirect the user to the login page
    return redirect(url_for('user_login'))


@app.route("/register", methods=["GET", "POST"])
def user_signup():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        qualification = request.form.get("qualification")
        usr = user_info.query.filter_by(name=name).first()
        if not usr:
            new_user = user_info(email=email, name=name, qualification=qualification, password=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template("login.html")
        else:
            return render_template("signup.html", msg="User already exists!")
    return render_template("signup.html", msg="")

#logout

@app.route('/admin_dashboard', methods=["GET", "POST"])
def admin_dashboard(name = None):
    if request.method == "POST":
        subject_name = request.form.get("subject_name")
        description = request.form.get("desc")

        if subject_name and description:
            existing_subject = Subject.query.filter_by(subject_name=subject_name).first()
            if not existing_subject:
                new_subject = Subject(subject_name=subject_name, desc=description)
                db.session.add(new_subject)
                db.session.commit()
                

        all_subject = Subject.query.all()
        return render_template("admin_dashboard.html", all_subject=all_subject, name=name)

    all_subject = Subject.query.all()
    return render_template("admin_dashboard.html", all_subject=all_subject, name = name)


@app.route('/delete_subject/<int:subject_id>', methods=["POST"])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)  # Automatically handles "not found"
    AddChapter.query.filter_by(subject_id=subject.id).delete()
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_subject/<int:subject_id>', methods=["POST"])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)  # Automatically handles "not found"
    subject.subject_name = request.form['subject_name']
    subject.desc = request.form['desc']
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/add_chapter', methods=["POST"])
def add_chapter():
    chapterName = request.form.get("chapterName")
    qsn = request.form.get("qsn")
    subject_id = request.form.get("subject_id")
    subject = Subject.query.get_or_404(subject_id)  

    new_chapter = AddChapter(chapterName=chapterName, qsn=qsn, subject_id=subject_id)
    db.session.add(new_chapter)
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    chapter = AddChapter.query.get_or_404(chapter_id)
    Question.query.filter_by(chapter_id=chapter_id).delete()
    db.session.commit()  
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_chapter/<int:chapter_id>', methods=["POST"])
def edit_chapter(chapter_id):
    chapter = AddChapter.query.get_or_404(chapter_id)  # Automatically handles "not found"
    chapter.chapterName = request.form['chapterName']
    chapter.qsn = request.form['qsn']
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/subject/<int:subject_id>')
def show_chapters(subject_id):
    user_name = "John Doe"  # Replace with actual user retrieval
    available_subjects = Subject.query.all()
    selected_subject = Subject.query.get_or_404(subject_id)
    chapters = AddChapter.query.filter_by(subject_id=subject_id).all()
    quiz_attempts = []  # Replace with actual database query

    return render_template(
        'user_dashboard.html',
        name=user_name,
        available_subjects=available_subjects,
        selected_subject_id=subject_id,  # Pass the selected subject ID
        chapters=chapters,  # Pass the chapters to the template
        quiz_attempts=quiz_attempts
    )

@app.route("/quiz", methods=["GET"])
@app.route("/quiz/<int:subject_id>", methods=["GET"])
def quiz(subject_id=None):
    all_subjects = Subject.query.all()
    
    # Optionally filter by subject_id if provided
    if subject_id:
        # You can modify the query to filter by the subject_id
        # For example, assume that each subject has chapters:
        all_subjects = [subject for subject in all_subjects if subject.id == subject_id]

    return render_template('quiz.html', all_subjects=all_subjects)

@app.route('/add_question/<int:chapter_id>', methods=["POST"])
def add_question(chapter_id):
    question_text = request.form.get("question_text")
    option_a = request.form.get("option_a")
    option_b = request.form.get("option_b")
    option_c = request.form.get("option_c")
    option_d = request.form.get("option_d")
    correct_option = request.form.get("correct_option")

    if question_text and option_a and option_b and option_c and option_d and correct_option:
        new_question = Question(
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            chapter_id=chapter_id
        )
        db.session.add(new_question)
        db.session.commit()
    return redirect(url_for('quiz'))

@app.route('/delete_question/<int:question_id>', methods=["POST"])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('quiz'))

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        # Update the question and options
        question.question_text = request.form['question_text']
        question.option_a = request.form['option_a']
        question.option_b = request.form['option_b']
        question.option_c = request.form['option_c']
        question.option_d = request.form['option_d']
        question.correct_option = request.form['correct_option']

        db.session.commit()  # Commit the changes to the database

        # Redirect to quiz page of the subject of the question's chapter
        return redirect(url_for('quiz', subject_id=question.chapter.subject.id))  # Corrected here

    return render_template('quiz.html', question=question)  # Adjust template if necessary


@app.route('/user_dashboard')
def user_dashboard():
    user_name = "John Doe"  # Replace with actual user retrieval
    available_subjects = Subject.query.all()
    quiz_attempts = []  # Replace with the correct way to query the database for quiz attempts
    return render_template(
        'user_dashboard.html',
        name=user_name,
        available_subjects=available_subjects,
        selected_subject_id=None,  # Initial state
        chapters=None,
        quiz_attempts=quiz_attempts
    )


@app.route('/chapter/<int:chapter_id>/quiz', methods=['GET', 'POST'])
def take_quiz(chapter_id):
    chapter = AddChapter.query.get_or_404(chapter_id)
    questions = Question.query.filter_by(chapter_id=chapter_id).all()
    num_questions = len(questions)

    if request.method == 'POST':
        correct_answers = 0
        for question in questions:
            user_answer = request.form.get(f'answer[{question.id}]')
            if user_answer and user_answer == question.correct_option:
                correct_answers = correct_answers + 1

        # Directly render results without saving
        return render_template('quiz_attempt.html', chapter=chapter, results={
            'correct_answers': correct_answers,
            'num_questions': num_questions
        })

    # Fetch the current question index
    current_question_index = request.args.get('question_index', default=0, type=int)

    if current_question_index >= num_questions:
        return redirect(url_for('take_quiz', chapter_id=chapter_id, method='POST'))  # Redirect to results

    question = questions[current_question_index]

    return render_template(
        'quiz_attempt.html',
        chapter=chapter,
        question=question,
        question_index=current_question_index,
        num_questions=num_questions
    )