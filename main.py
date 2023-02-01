from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies-data-two.db'
db = SQLAlchemy(app)

# -------------------API section ------------#
Bootstrap(app)
#-------------------GET YOUR API KEY FROM themoviedb.org----------# 
API_KEY = "YOUR API KEY"



# -------------------- Creating form using WTforms ------------------#
class Form(FlaskForm):
    rating_out = StringField('your rating out of')
    review = StringField('your review')
    submit = SubmitField('submit')


class Add_Form(FlaskForm):
    movie_title = StringField('movie title', validators=[DataRequired()])
    submit = SubmitField('done')


# -----------------------Creating database using sqlite----------------#
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(80), nullable=True)
    img_url = db.Column(db.String(80), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_movie_data = db.session.query(Movie).order_by('rating').all()
    for i in range(len(all_movie_data)):
        all_movie_data[i].ranking = len(all_movie_data) - i
    db.session.commit()

    return render_template("index.html", movie=all_movie_data)


@app.route("/add", methods=["GET", "POST"])
def addmovie():
    form = Add_Form()
    if form.validate_on_submit():
        responce = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&query={form.movie_title.data}&page=1&include_adult=false")
        data = responce.json()["results"]
        return render_template('select.html', options=data)
    return render_template("add.html", form=form)


@app.route('/find')
def find():
    movie_id = request.args.get('id')
    responce = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US")
    description = responce.json()['overview']
    title = responce.json()['title']
    img_url = responce.json()['poster_path']
    year = responce.json()['release_date']
    new_movie = Movie(
        title=title,
        year=year,
        description=description,
        review="My favourite character was the caller.",
        img_url=f"https://image.tmdb.org/t/p/w500{img_url}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit'))


@app.route('/edit', methods=["GET", "POST"])
def edit():
    all_movie_data = db.session.query(Movie).all()
    form = Form()
    movie_id = request.args.get('id')
    movie_to_update = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie_to_update.rating = float(form.rating_out.data)
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=all_movie_data, form=form)


@app.route('/delete')
def delete_movie():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

