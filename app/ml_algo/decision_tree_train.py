import numpy as np
import pandas as pd
import pickle
from app.ml_algo import decision_tree

def train_test_split(X, y, random_state=41, test_size=0.2):
    """
    Splits the data into training and testing sets.

    Parameters:
        X (numpy.ndarray): Features array of shape (n_samples, n_features).
        y (numpy.ndarray): Target array of shape (n_samples,).
        random_state (int): Seed for the random number generator. Default is 41.
        test_size (float): Proportion of samples to include in the test set. Default is 0.2.

    Returns:
        Tuple[numpy.ndarray]: A tuple containing X_train, X_test, y_train, y_test.
    """
    n_samples = X.shape[0]
    np.random.seed(random_state)
    shuffled_indices = np.random.permutation(np.arange(n_samples))
    test_size = int(n_samples * test_size)
    test_indices = shuffled_indices[:test_size]
    train_indices = shuffled_indices[test_size:]
    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]

    return X_train, X_test, y_train, y_test

score_df = pd.read_csv('patient_data.csv', header=0)
score_df = score_df.rename(columns=lambda x: x.strip())  # This strips whitespace from all column headers

# Convert data to numeric types and handle conversion of all columns appropriately
for col in score_df.columns:
    if col != 'SCORE':
        score_df[col] = pd.to_numeric(score_df[col])
    else:
        score_df[col] = score_df[col].astype('int')

X = score_df.drop('SCORE', axis=1).values  # Convert to numpy array
y = score_df['SCORE'].values  # Convert to numpy array

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Train a decision tree model (assuming decision_tree.DecisionTree exists and is correctly implemented)
model = decision_tree.DecisionTree(2, 2)
model.fit(X_train, y_train)

# Use the trained model to make predictions on the test data
predictions = model.predict(X_test)

# Function to calculate accuracy
def accuracy(y_true, y_pred):
    correct_predictions = np.sum(y_true == y_pred)
    return correct_predictions / len(y_true)

# Calculate and print the model's accuracy
print(f"Model's Accuracy: {accuracy(y_test, predictions)}")

# Save the trained model to a file
model_pkl_file = "decision_tree_model.pkl"
with open(model_pkl_file, 'wb') as file:
    pickle.dump(model, file)