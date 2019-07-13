import os
import secrets
from flask import Flask
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
import random, copy
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.analytical_scraping import ans, answer_headings, answers1, answers2, questions1, questions2, questions3, sample_questions1, sample_questions2

oqs = {
 #Format is 'q':[options]
 'If the roots of the equation x2−16x−612=0 are a and b, what is the value of a+b?':['16','-16','0','-612'],
 'If x and y are non-negative integers such that 2x+3y=8 and z=x2+y2, what is the maximum value of z?':['16','0','5','20'],
 'If |x|=|y|, which of the following must be true?':['x4=y4','x>y','x<y','x3=y3'],
 'If −1<h<0, which of the following has the greatest value?':['1-1/h','1+1/h','1-h','1+h'],
 'If the average (arithmetic mean) of five distinct positive integers is 10, what is the difference between the largest possible value of the greatest integer and the least possible value of the greatest of the five integers?':['28','0','5','40'],
 'If a/b>c/d, and none of a, b, c, and d is equal to 0, which of the following must be true?':['(−a/b)<(−c/d)','−a/b<c/d','|a/b|>|c/d|','(b/a)<(d/c)'],
 'What could be the value of integer from 180 to 300, inclusive, that leave the remainder 2 when divided by 15 and by 9?':['182','191','197','242'],
 'A computer companys featured laptop cost $800 last year. This year, the laptop sold for 15 percent less than it did last year. Next year, after updates are made to the model, there will be a 25% price increase over this years price. What will be the price next year?':['$850','$810','$840','$845'],
 'Pipe A can fill a tank in 3 hours. If pipe B can fill the same tank in 2 hours, how many minutes will it take both pipes to fill 2/3 of a tank?':['54','30','48','60'],
 'How many milliliters of acid are ther in 350 mililiters of 4 percent acid?':['87.5','10','14','35']
}
#For advanced level quiz
org = {
 #Format is 'q':[options]
 'Astrid wrote down all the different three-digit numbers that can be written using each of the numeral 1, 2 and 3 exactly once. What is the median of the numbers Astrid wrote down?':['231','213','222','233'],
 'If a bookstore owner buys 15 books less for $900 when the price of each book goes up by $3, then find the original price of book.':['$12','$15','$18','$20'],
 'If m and n are the roots of the equation a2 - 6a + 8 = 0, then find the value of (m+n)(m-n)':['12','8','16','4'],
 'A train takes 10 seconds to cross a pole and 20 seconds to cross a platform of length 200 m. What is the length of train?':['200m','400m','600m','800m'],
 'The price of a pair of sneakers was $80 for the last six months of last year. On January first, the price increased 20%. After the price increase, an employee bought these sneakers with a 10 percent employee discount. What price did the employee pay?':['$86.40','$83.33','$82.00','$88.00'],
 'If 6k^2 + k = 2 and k > 0, then k must equal which of the following?':['1/2','1','3/2','2'],
 'In how many different ways can 3 identical green shirts and 3 identical red shirts be distributed among 6 children such that each child receives a shirt?':['20','40','216','720'],
 'If x > 0 which of the following expressions are equal to 3.6 percent of (5x)/12?':['x percent of 3/2','3 percent of 20x','3x percent of 0.2','0.05 percent of 3x'],
 'A popular website requires users to create a password consisting of digits only. If no digit may be repeated and each password must be at least 9 digits long, how many passwords are possible?':['2 × 10!','9! + 10!','9! × 10!','19!'],
 'In a certain shop, notebooks that normally sell for 59 cents each are on sale at 2 for 99 cents. How much can be saved by purchasing 10 of these notebooks at the sale price? ':['$0.95','$0.85','$1.00','$1.05']
}

practice_questions={
 'If 6k^2 + k = 2 and k > 0, then k must equal which of the following?':['1/2','1','3/2','2'],
 'A tower casts a shadow of 6 meters at a certain time of the day. If at exactly the same time, a man stands at the top of the tower, the length of the shadow increases by 2 meters. What is the height of the man if the tower is 5 meters high?':['1.66','1.5','1','2'],
 'If x2 + 6x = –9, how many values of x are possible?':['one','none','two','infinite'],
 'In a certain parallelogram, the size of one interior angle exceeds that of another interior angle by D degrees. Which of the following expressions represents the degree measure of the smaller angle?':['90-D/2','90-D','180-D','120-D'],
 'The lengths of two sides of a triangle are 5 and 7. Which of the following could be the perimeter of the triangle?':['22','14','24','27'],
 'If a/b>c/d, and none of a, b, c, and d is equal to 0, which of the following must be true?':['(−a/b)<(−c/d)','−a/b<c/d','|a/b|>|c/d|','(b/a)<(d/c)'],
 'What could be the value of integer from 180 to 300, inclusive, that leave the remainder 2 when divided by 15 and by 9?':['182','191','197','242'],
 'A computer companys featured laptop cost $800 last year. This year, the laptop sold for 15 percent less than it did last year. Next year, after updates are made to the model, there will be a 25% price increase over this years price. What will be the price next year?':['$850','$810','$840','$845'],
 'Pipe A can fill a tank in 3 hours. If pipe B can fill the same tank in 2 hours, how many minutes will it take both pipes to fill 2/3 of a tank?':['54','30','48','60'],
 'How many milliliters of acid are ther in 350 mililiters of 4 percent acid?':['87.5','10','14','35']
}


practice = copy.deepcopy(practice_questions)

#For beginner level quiz
original_questions = {
 #Format is 'question':[options]
 'v. consider not very seriously; play':['dally','reciprocate','lionize','chronicle'],
 'adj. young and inexperienced':['callow','downlike','carnal','politic'],
 'n. playing a set of bells that are (usually) hung in a tower':['carillon','diffusion','repertoire','lucre'],
 'n.abstaining from excess':['sobriety','quirk','tepidity','din'],
 'n. foil in thin strips':['chaff','dicot','guck','stamina'],
 'adj. deep and harsh sounding as if from shouting or illness or emotion; husky':['	gruff','elated','adamant','deranged'],
 'n. attention and management implying responsibility for safety; guardianship':['tutelage','crescendo','regime','distortion'],
 'n. rotating mechanism in the form of a universally mounted spinning wheel that offers resistance to turns in any direction':['gyroscope','suffragist','satire','	hybrid'],
 'v. tease; drive':['goad','handbuild','upbraid','berate'],
 'adj. capable of being assigned or credited to; imputable; referable':['ascribable','discursive','parochial','specious']
}
#For advanced level quiz
original_question = {
 #Format is 'question':[options]
 'v. revoke formally':['abrogate','beget','undergird','befuddle'],
 'v. consider in a comprehensive way':['appraise','rout','exhort','beset'],
 'v. lose interest or become bored with something or somebody; weary; fatigue; jade':['pall','gestate','debunk','tantalize'],
 'v. form or shape by forcing through an opening':['extrude','nullify','accost','overhaul'],
 'v. dress or groom with elaborate care; plume; dress':['preen','foist','knit','domineer'],
 'v. put up with something or somebody unpleasant; endure; stick out':['brook','assent','collaborate','array'],
 'v. collect discarded or refused material':['salvage','demean','foist','harrow'],
 'v. receive a specified treatment (abstract); find; obtain':['incur','careen','grill','winnow'],
 'v. look down on with disdain; scorn; disdain':['contemn','manducate','placate','dislodge'],
 'v. tear down so as to make flat with the ground; dismantle; tear down; take down; pull down':['rase','maim','hopple','waft']
}
#For verbal quiz
o_q={
  ' The author of the passage is primarily concerned with':['Defending the criteria by which he chose the essays that appear in the collection.','Educating readers about literary genres.','Explaining what characteristics of writing interest him most.','Cataloguing the formal qualities of writing that coincide with traditional essays.'],
  ' The passage supports all of the following EXCEPT:':['Essays that vary in length, style, and formality are inferior to those that follow strict rules.','Conciseness and language use are only one aspect of what gives an essay worth.','Taxonomy cannot always apply to writing in the same way it does to scientific concepts.','The length of a piece cannot be considered in evaluating the merit of its ideas.'],
  ' In context, the author refers to causeries (informal writing or conversation) and propos (exchange of spoken words) primarily in order to':['Explain that an effective essay can have casual elements and need not always follow strict guidelines exactly.','Argue that spoken language is superior to written language.','Prove that essays, like conversation, are best when pithy and exact.','Demonstrate that all nonfiction essays are informal in their very nature.']
}

oq={
  'The author takes multiple perspectives when describing New York. What two tones are primarily utilized?':['Impressed and critical','Sardonic and optimistic','Detached and Jovial','Ominous and fanciful'],
  'With which of the following statements would the author of the passage most likely agree?':['A single location can have many facets, both positive and negative.','Oregon, Iowa, and Arizona do not have any geographical merit.','Every aspect of New York is unique and admirable.','Large cities tend to lack whimsical and artistic sights.'],
  ' Which of the following CANNOT be inferred about Werner from the passage?':['He is very biased in favor toward the Upper East Side of New York.','He is a creative and imagistic thinker.','He does not live at the same level of luxury as those he works for.','He is fascinated and intrigued by colors.']

}


qs = copy.deepcopy(oqs)

q = copy.deepcopy(org)

questions = copy.deepcopy(original_questions)

question = copy.deepcopy(original_question)

practice = copy.deepcopy(practice_questions)

ques1=copy.deepcopy(o_q)
ques2=copy.deepcopy(oq)

def shuffle(q):
 
 selected_keys = []
 i = 0
 while i < len(q):
  current_selection = random.choice(list(q.keys()))
  if current_selection not in selected_keys:
   selected_keys.append(current_selection)
   i = i+1
 return selected_keys

def shuffles(q):
 
 selected_key = []
 i = 0
 while i < len(q):
  current_selection = random.choice(list(q.keys()))
  if current_selection not in selected_key:
   selected_key.append(current_selection)
   i = i+1
 return selected_key

def shuf(q):
 
 selected_keys = []
 i = 0
 while i < len(q):
  current_selection = random.choice(list(q.keys()))
  if current_selection not in selected_keys:
   selected_keys.append(current_selection)
   i = i+1
 return selected_keys

def shuff(q):
 
 selected_keys = []
 i = 0
 while i < len(q):
  current_selection = random.choice(list(q.keys()))
  if current_selection not in selected_keys:
   selected_keys.append(current_selection)
   i = i+1
 return selected_keys



@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    return render_template('home.html', posts=posts)


@app.route("/analytical")
@login_required
def analytical():
    return render_template('analytical.html', title='Analytical', questions_ans = zip(questions1, ans))

@app.route("/analytical_solved_questions_analyze_issue")
@login_required
def solved1():
    return render_template('analytical2.html', title='Analytical',topic='Issue', headings_answers = zip(answer_headings, answers1), question=questions2)

@app.route("/analytical_solved_questions_analyze_argument")
@login_required
def solved2():
    return render_template('analytical2.html',topic='Argument', headings_answers = zip(answer_headings, answers2), question=questions3)

@app.route("/analytical_sample_questions_analyze_issue")
@login_required
def sample1():
    return render_template('analytical3.html', questions=sample_questions1, topic="Issue")


@app.route("/analytical_sample_questions_analyze_argument")
@login_required
def sample2():
    return render_template('analytical3.html', questions=sample_questions2, topic="Argument")


@app.route("/verbal")
@login_required
def verbal():
    return render_template('verbal.html', title='Verbal')

@app.route('/verbal/vocab')
@login_required
def vocab():
    return render_template('vocab.html')

@app.route('/verbal/flash_cards')
@login_required
def flash():
    return render_template('flash_cards.html')

@app.route('/verbal/voc_quiz_home')
@login_required
def voc_quiz():
    return render_template('voc_quiz_home.html')
    

@app.route('/verbal/voc_quiz_home/voc_quiz1')
@login_required
def voc_quiz1():
    questions_shuffled = shuffle(questions)
    for i in questions.keys():
        random.shuffle(questions[i])
    return render_template('voc_quiz1.html', q = questions_shuffled, o = questions)

@app.route('/verbal/voc_quiz_home/voc_quiz1/score', methods=['POST'])
@login_required
def quiz1_answers():
 correct = 0
 for i in questions.keys():
  answered = request.form[i]
  if original_questions[i][0] == answered:
   correct = correct+1
 return render_template('score.html',s=correct)
#'<h1>Correct Answers: <u>'+str(correct)+'</u></h1>'

@app.route('/verbal/voc_quiz_home/voc_quiz2')
@login_required
def voc_quiz2():
    question_shuffled = shuffles(question)
    for i in question.keys():
        random.shuffle(question[i])
    return render_template('voc_quiz2.html', q = question_shuffled, o = question)

@app.route('/verbal/voc_quiz_home/voc_quiz2/score', methods=['POST'])
@login_required
def quiz2_answers():
 correct = 0
 for i in question.keys():
  answered = request.form[i]
  if original_question[i][0] == answered:
   correct = correct+1
 return render_template('score.html',s=correct)

@app.route('/verbal/verbal_prac/prac1')
@login_required
def prac1():
    questions_shuffled = shuf(ques1)
    for i in ques1.keys():
        random.shuffle(ques1[i])
    return render_template('prac1.html', q = questions_shuffled, o = ques1)

@app.route('/verbal/verbal_prac/prac1/score', methods=['POST'])
@login_required
def prac1_answers():
 correct = 0
 for i in ques1.keys():
  answered = request.form[i]
  if o_q[i][0] == answered:
   correct = correct+1
 return render_template('score.html',s=correct)


@app.route('/verbal/verbal_prac/prac2')
@login_required
def prac2():
    questions_shuffled = shuff(ques2)
    for i in ques2.keys():
        random.shuffle(ques2[i])
    return render_template('prac2.html', q = questions_shuffled, o = ques2)

@app.route('/verbal/verbal_prac/prac2/score', methods=['POST','GET'])
@login_required
def prac2_answers():
 correct = 0
 for i in ques2.keys():
  answered = request.form[i]
  if oq[i][0] == answered:
   correct = correct+1
 return render_template('score.html',s=correct)
def home_redirect():
  return redirect(url_for('home'))

@app.route('/verbal/verbal_prac')
@login_required
def verbal_prac():
    return render_template('verbal_prac.html')

@app.route('/quantitative')
@login_required
def quant():
    return render_template('quant.html')


@app.route("/quantitative")
@login_required
def quantitative():
    return render_template('quantitative.html', title='Quantitative')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your review has been posted!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Review',
                           form=form, legend='New Review')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your review has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update review',
                           form=form, legend='Update review')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your review has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@app.route('/quant/quant_quiz_home')
def quant_quiz():
    return render_template('quant_quiz_home.html')
    

@app.route('/quant/quant_quiz_home/quant_quiz1')
def quant_quiz1():
    questions_shuffled = shuffle(qs)
    for i in qs.keys():
        random.shuffle(qs[i])
    return render_template('quant_quiz1.html', q = questions_shuffled, o = qs)

@app.route('/quant/quant_quiz_home/quant_quiz1/score', methods=['POST'])
def quiz_answers():
 correct = 0
 for i in qs.keys():
  answered = request.form[i]
  if oqs[i][0] == answered:
   correct = correct+1
 return render_template('score.html',s=correct)
#'<h1>Correct Answers: <u>'+str(correct)+'</u></h1>'

@app.route('/quant/quant_quiz_home/quant_quiz2')
def quant_quiz2():
    question_shuffled = shuffles(q)
    for i in q.keys():
        random.shuffle(q[i])
    return render_template('quant_quiz2.html', q = question_shuffled, o = q)

@app.route('/quant/quant_quiz_home/quant_quiz2/score', methods=['POST'])
def q2_answers():
 correct = 0
 for i in q.keys():
  answered = request.form[i]
  if org[i][0] == answered:
   correct = correct+1
 return render_template('score.html',s=correct)


@app.route('/quant/quant_prac')
def quant_prac():
  practice_shuffled = shuffle(practice)
  for i in practice.keys():
    random.shuffle(practice[i])
  return render_template('quant_prac.html', q = practice_shuffled, o = practice)


@app.route('/quant/quant_prac/score', methods=['POST'])
def prac_answers():
 correct = 0
 for i in practice.keys():
  answered = request.form[i]
  if practice[i][0] == answered:
   correct = correct+1
 return render_template('score.html',s=correct)


 
@app.errorhandler(400)
def page_not_found(error):
  return render_template('page_not_found.html'), 400