import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib

# Step 1: Load the CSV data
data = pd.read_csv('tv_shows.csv')

# Step 2: Preprocess the data
# Assume 'cast' and 'genre' are the features, and 'episode' is the target variable (adjust as needed)
X = data[['cast', 'genre']]
y = data['episode']

# If you need to combine 'cast' and 'genre' into a single feature, you can do something like this:
X['combined_features'] = X['cast'] + ' ' + X['genre']

# Step 3: Create a machine learning pipeline
# Vectorize the text data and then apply a logistic regression model
pipeline = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', LogisticRegression())
])

# Step 4: Train the model
X_train, X_test, y_train, y_test = train_test_split(X['combined_features'], y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

# Step 5: Save the model to a .pkl file
model_filename = 'tv_show_model.pkl'
joblib.dump(pipeline, model_filename)

print(f"Model trained and saved as {model_filename}")
