import pickle
import numpy as np
import random
import math
from app.arduino.ar import *

def load_model(model_file):
    """Utility function to load a pickle model."""
    with open(model_file, 'rb') as file:
        model = pickle.load(file)
    return model

def get_score(model, arr):
    """General function to get the model score."""
    arr = np.array(arr)
    arr = arr.reshape(1, -1)
    return model.predict(arr)[0]

def prepare_data():
    """Generates random data for model input."""
    p=arduino()
    arr=[]
    arr.append(p[2])
    arr.append(p[0])
    arr.append(round(random.uniform(12,16),2))
    arr.append(round(random.uniform(100,120),2))
    arr.append(round(random.uniform(60,80),2))
    arr.append(p[1])

    print(arr)
    return arr

def hybrid_score():
    print("In hybrid_score")
    # Load both models
    dt_model = load_model("decision_tree_model.pkl")
    print("Decision Tree Model loaded")
    knn_model = load_model("knn_weight.pkl")
    print("Models loaded")

    # Prepare data
    data = prepare_data()
    
    # Get scores from both models
    dt_score = get_score(dt_model, data)
    knn_score = get_score(knn_model, data)

    # # Print individual model scores
    # print("Decision Tree Score:", dt_score)
    # print("KNN Score:", knn_score)

    # Calculate and print the hybrid score
    hybrid_score = math.floor((dt_score + knn_score) / 2)
    print("Hybrid Score:", hybrid_score)

