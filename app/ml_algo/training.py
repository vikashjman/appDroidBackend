import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pandas as pd
import pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier


cmap = ListedColormap(['#FF0000','#00FF00','#0000FF'])

score_df = pd.read_csv('patient_data.csv', header=0)
for col in score_df.columns:
    if col != 'SCORE':
        
        score_df[col] = pd.to_numeric(score_df[col])
    else:
        score_df[col] = score_df[col].astype('int')
score_df = score_df.rename(columns={'SCORE ':'SCORE'})
X = score_df.drop('SCORE',axis=1)
y = score_df.SCORE

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1234)

X_train = X_train.to_numpy()
y_train= y_train.to_numpy()
X_test=X_test.to_numpy()
y_test=y_test.to_numpy()

# Initialize the k-NN classifier
knn_classifier = KNeighborsClassifier(n_neighbors=5)  # You can adjust the number of neighbors as needed

# Train the model on the training data
knn_classifier.fit(X_train, y_train)

# Predict on the test data
y_pred_knn = knn_classifier.predict(X_test)

# Calculate accuracy
accuracy_knn = accuracy_score(y_test, y_pred_knn)
print(f"k-NN Accuracy: {accuracy_knn:.4f}")

# Initialize the Decision Tree classifier
dt_classifier = DecisionTreeClassifier(random_state=1234)

# Train the model on the training data
dt_classifier.fit(X_train, y_train)

# Predict on the test data
y_pred_dt = dt_classifier.predict(X_test)

# Calculate accuracy
accuracy_dt = accuracy_score(y_test, y_pred_dt)
print(f"Decision Tree Accuracy: {accuracy_dt:.4f}")


# Save the k-NN model
with open('knn_model.pkl', 'wb') as knn_file:
    pickle.dump(knn_classifier, knn_file)

# Save the Decision Tree model
with open('dt_model.pkl', 'wb') as dt_file:
    pickle.dump(dt_classifier, dt_file)

# Load the models later
with open('knn_model.pkl', 'rb') as knn_file:
    loaded_knn_model = pickle.load(knn_file)

with open('dt_model.pkl', 'rb') as dt_file:
    loaded_dt_model = pickle.load(dt_file)

# Test the loaded models on sample data
loaded_knn_predictions = loaded_knn_model.predict(X_test)
loaded_dt_predictions = loaded_dt_model.predict(X_test)
