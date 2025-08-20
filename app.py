from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import UserRecommendation, UserSearch, db, User, TVShow, UserTVShow
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import pandas as pd
from sqlalchemy.orm import joinedload
from sklearn.metrics import pairwise_distances_argmin_min
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from models import db, User, TVShow, UserTVShow
from werkzeug.security import generate_password_hash, check_password_hash
import joblib, re
import os
import pandas as pd
import plotly.express as px
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///instance/tv_recommendation_app.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db.init_app(app)

kmeans = joblib.load('kmeans_tv_shows_model_final.pkl')
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already taken')
            return redirect(url_for('register'))
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('profile', user_id=user.id))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = db.session.get(User, user_id)
    return render_template('profile.html', user=user)

@app.route('/add_tv_show/<int:user_id>', methods=['GET', 'POST'])
def add_tv_show(user_id):
    if request.method == 'POST':
        season_name = request.form['season_name']
        total_episodes = request.form['total_episodes']
        cast_main_roles = request.form['cast_main_roles']
        genre = request.form['genre']
        year_released = request.form['year_released']
        platform = request.form['platform']
        new_show = TVShow(
            season_name=season_name, 
            total_episodes=total_episodes, 
            cast_main_roles=cast_main_roles, 
            genre=genre, 
            year_released=year_released, 
            platform=platform
        )
        db.session.add(new_show)
        db.session.commit()
        user_tv_show = UserTVShow(user_id=user_id, tv_show_id=new_show.id)
        db.session.add(user_tv_show)
        db.session.commit()
        return redirect(url_for('profile', user_id=user_id))
    return render_template('add_tv_show.html', user_id=user_id)

    
@app.route('/admin_dashboard')
def admin_dashboard():
    users = User.query.filter_by(is_admin=False).all()  # Get all non-admin users
    return render_template('admin_dashboard.html', users=users)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, is_admin=True).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin username or password')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/recommend_from_profile/<int:user_id>', methods=['POST'])
def recommend_from_profile(user_id):
    user = db.session.get(User, user_id)

    # Get all TV shows for this user
    user_tv_shows = UserTVShow.query.filter_by(user_id=user_id).all()

    if not user_tv_shows:
        flash('No TV shows found for recommendation.')
        return redirect(url_for('profile', user_id=user_id))

    # Prepare the data for the user's TV shows
    tv_show_data = []

    for user_tv_show in user_tv_shows:
        show = user_tv_show.tv_show
        tv_show_data.append({
            'genre': show.genre,
            'total_episodes': show.total_episodes,
            'release_year': show.year_released,
            'ratings': show.year_released,
            'name': show.season_name    

        })

    # Create a DataFrame for the user's TV shows
    user_tv_shows_df = pd.DataFrame(tv_show_data)

    # Predict clusters for user's TV shows
    user_clusters = kmeans.predict(user_tv_shows_df)

    # Fetch all TV shows from the database
    all_tv_shows = TVShow.query.all()

    # Prepare the data for all TV shows
    all_tv_show_data = []
    for show in all_tv_shows:
        all_tv_show_data.append({
            'genre': show.genre,
            'total_episodes': show.total_episodes,
            'release_year': show.year_released,
            'ratings': show.year_released,
            'show': show  # Keep a reference to the original show object
        })

    # Create a DataFrame for all TV shows
    all_tv_shows_df = pd.DataFrame(all_tv_show_data)

    # Predict clusters for all TV shows
    all_clusters = kmeans.predict(all_tv_shows_df[['genre', 'total_episodes', 'release_year', 'ratings']])

    # Find TV shows in the same clusters as the user's shows
    recommended_shows = []
    for i, cluster in enumerate(all_clusters):
        if cluster in user_clusters:
            recommended_shows.append(all_tv_show_data[i]['show'])

    # Remove the user's own shows from the recommendations
    recommended_shows = [show for show in set(recommended_shows) if show.id not in [tv_show.tv_show_id for tv_show in user_tv_shows]]
     
    # if recommended_shows:

    #     print("------------")
    #     return render_template('recommendations.html', recommendations=recommended_shows)
    # else:
    # If no recommendations are found, use the CSV file to find shows with the same genre
    csv_file_path = 'Shuffled_Unique_Simple_Complete_Popular_Tv_shows.csv'  # Update with the actual path to your CSV file
    csv_df = pd.read_csv(csv_file_path)

    # Get the genre of the user's first TV show as an example (you can improve this logic)
    user_genre = tv_show_data[0]['genre']



    # Split the user's genre into individual genres
    genre_list = [genre.strip() for genre in user_genre.split(',')]

    # Filter the CSV for shows with any matching genre
    similar_shows = csv_df[csv_df['genre'].apply(lambda x: any(genre in x for genre in genre_list))]

    print("similar_shows: ", similar_shows)

    # Select up to 3 random shows from the filtered list
    similar_shows = similar_shows.sample(min(3, len(similar_shows)))

    # Convert to a list of show names or any relevant information
    similar_shows_list = similar_shows['name'].tolist()

    if similar_shows_list:
        user_search = UserSearch(user_id=user_id, search_query=';'.join([show['name'] for show in tv_show_data]))
        db.session.add(user_search)
        db.session.commit()

        # Save the recommendations
        user_recommendation = UserRecommendation(user_id=user_id, recommended_shows=';'.join(similar_shows_list))
        db.session.add(user_recommendation)
        db.session.commit()
        # flash(f"Recommendation Found: {', '.join(similar_shows_list)}")
        return render_template('recommendations.html', recommendations=similar_shows_list)
    else:
        flash('No recommendations found.')

    return redirect(url_for('profile', user_id=user_id))
        
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        flash("Please enter a search query.")
        return redirect(request.referrer or url_for('home'))

    # Search for users
    users = User.query.filter(User.username.ilike(f'%{query}%')).all()

    # Search for TV shows
    tv_shows = TVShow.query.filter(
        db.or_(
            TVShow.season_name.ilike(f'%{query}%'),
            TVShow.genre.ilike(f'%{query}%'),
            TVShow.cast_main_roles.ilike(f'%{query}%'),
        )
    ).all()

    # Check if the request is for JSON data (API request)
    if request.is_json:
        return jsonify({
            "users": [
                {"id": user.id, "username": user.username}
                for user in users
            ],
            "tv_shows": [
                {
                    "id": show.id,
                    "season_name": show.season_name,
                    "total_episodes": show.total_episodes,
                    "cast_main_roles": show.cast_main_roles,
                    "genre": show.genre,
                    "year_released": show.year_released,
                    "platform": show.platform,
                }
                for show in tv_shows
            ]
        })

    # Render the search results page for web requests
    return render_template('search_results.html', query=query, users=users, tv_shows=tv_shows)




@app.route('/gantt_chart')
def gantt_chart():
    # Fetch the search and recommendation data
    searches = UserSearch.query.all()
    recommendations = UserRecommendation.query.all()

    # Prepare the data for the Gantt chart
    tasks = []
    for search in searches:
        tasks.append({
            'Task': f'Search: {search.search_query}',
            'Start': search.timestamp,
            'Finish': search.timestamp + timedelta(seconds=10),  # Add a small duration
            'Resource': f'User {search.user.username}'
        })

    for recommendation in recommendations:
        tasks.append({
            'Task': f'Recommendation: {recommendation.recommended_shows}',
            'Start': recommendation.timestamp,
            'Finish': recommendation.timestamp + timedelta(seconds=10),  # Add a small duration
            'Resource': f'User {recommendation.user.username}'
        })

    # Create a DataFrame for the tasks
    df = pd.DataFrame(tasks)

    # Generate the Gantt chart
    fig = px.timeline(
        df, 
        x_start="Start", 
        x_end="Finish", 
        y="Resource", 
        title="User Search and Recommendations", 
        color="Task", 
        labels={"Task": "Search/Recommendation"}
    )
    fig.update_yaxes(categoryorder="total ascending")  # Sort by user
    fig.show()

    return render_template('gantt_chart.html', plot=fig.to_html())

   
@app.route('/init_db')
def init_db():
    db.create_all()
    return "Database initialized!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
