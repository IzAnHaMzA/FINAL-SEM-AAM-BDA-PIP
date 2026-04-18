from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from datetime import date, datetime, time
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "aam_pdf"
IMAGE_DIR = BASE_DIR / "aam_images"
SAVED_DIAGRAMS_FILE = IMAGE_DIR / "saved_diagrams.json"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    return jsonify({"error": "Image is too large. Please upload an image smaller than 8 MB."}), 413


def load_saved_diagrams() -> dict[str, str]:
    if not SAVED_DIAGRAMS_FILE.exists():
        return {}
    try:
        data = json.loads(SAVED_DIAGRAMS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_diagram_mapping(question_id: str, image_url: str) -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    diagrams = load_saved_diagrams()
    diagrams[str(question_id)] = image_url
    SAVED_DIAGRAMS_FILE.write_text(json.dumps(diagrams, indent=2), encoding="utf-8")

EXAM_TIMETABLE = {
    "season": "MSBTE Summer 2026 - YOUR SUBJECTS",
    "time_label": "Time (All Papers)",
    "time_value": "09:30 AM to 12:30 PM (Morning Session)",
    "schedule": [
        {"date": "24-04-2026", "paper": "316318", "subject": "Big Data Analytics (BDA)"},
        {"date": "29-04-2026", "paper": "316320", "subject": "Advanced Algorithm in AI & ML (AAM)"},
        {"date": "04-05-2026", "paper": "316319", "subject": "Principles of Image Processing (PIP)"},
    ],
    "final_order": [
        "BDA -> 24 April",
        "AAM -> 29 April",
        "PIP -> 4 May",
    ],
}


ML_UNITS = [
    {
        "id": "unit-1",
        "number": 1,
        "title": "ML Basics & Feature Engineering",
        "questions": [
            {"id": 1, "star": "⭐", "question": "What is ML Model and features", "definition": "Machine learning model is program that learns patterns from data to make predictions.", "points": ["Identifies patterns from historical data", "Predicts future values or classifications", "Improves performance with more data", "Reduces manual effort and time"], "example": "Prediction", "type": "standard"},
            {"id": 2, "star": "⭐", "question": "Components of Machine Learning", "definition": "Machine learning components control training process and improve model performance and accuracy.", "points": ["Hyperparameters control learning process", "Loss function measures prediction error", "Optimization reduces error step by step", "Metrics evaluate performance quality"], "example": "Accuracy", "type": "standard"},
            {"id": 3, "star": "⭐", "question": "Types of ML Algorithms", "definition": "Machine learning algorithms are categorized based on data and learning type used.", "points": ["Supervised uses labelled training data", "Unsupervised finds hidden patterns", "Semi supervised uses mixed data", "Reinforcement uses reward based learning"], "example": "Clustering", "type": "standard"},
            {"id": 4, "star": "⭐", "question": "Model Selection", "definition": "Model selection is process of choosing best model suitable for given problem.", "points": ["Compares different models performance", "Considers hyperparameters and data type", "Selects most accurate predictive model", "Improves reliability of predictions"], "example": "Selection", "type": "standard"},
            {"id": 5, "star": "⭐", "question": "Choosing Best Model", "definition": "Best model depends on data type task and evaluation results.", "points": ["Images use CNN models", "Text uses RNN models", "Numerical uses SVM models", "Choose based on accuracy"], "example": "CNN", "type": "standard"},
            {"id": 6, "star": "⭐", "question": "Model Selection Techniques", "definition": "Model selection techniques evaluate and compare models to choose best performing one.", "points": ["Cross validation splits data repeatedly", "Bootstrap sampling uses replacement", "AIC compares model performance", "BIC considers performance and complexity"], "example": "AIC", "type": "standard"},
            {"id": 7, "star": "⭐", "question": "Regression Metrics", "definition": "Regression metrics measure difference between predicted values and actual values.", "points": ["MAE calculates absolute error", "MSE squares error values", "RMSE gives root error", "R2 shows variance explained"], "example": "MAE", "type": "standard"},
            {"id": 8, "star": "⭐", "question": "Supervised Model Training", "definition": "Supervised training learns from labelled data to make accurate predictions.", "points": ["Perform data analysis and visualization", "Extract and select relevant features", "Train model using training data", "Evaluate and fine tune model"], "example": "Classification", "type": "standard"},
            {"id": 9, "star": "⭐", "question": "Feature Engineering", "definition": "Feature engineering transforms raw data into meaningful features for better model performance.", "points": ["Select important features from dataset", "Transform data into useful format", "Create new features from existing", "Improves accuracy and efficiency"], "example": "Preprocessing", "type": "standard"},
            {"id": 10, "star": "", "question": "Numerical Feature Engineering", "definition": "Numerical feature engineering transforms numeric values to improve model learning.", "points": ["Scaling normalizes feature values", "Binning groups numerical data", "Polynomial captures nonlinear relations", "Log transform handles skewed data"], "example": "Scaling", "type": "standard"},
            {"id": 11, "star": "", "question": "Categorical Feature Engineering", "definition": "Categorical feature engineering converts categories into numerical form for models.", "points": ["One hot encoding creates binary values", "Label encoding assigns numeric labels", "Target encoding uses mean values", "Frequency encoding counts occurrences"], "example": "Encoding", "type": "standard"},
            {"id": 12, "star": "", "question": "Text Feature Engineering", "definition": "Text feature engineering converts text into numerical features usable by models.", "points": ["Tokenization splits text into words", "TF-IDF measures word importance", "Word embeddings create vectors", "Bag of words counts frequency"], "example": "NLP", "type": "standard"},
            {"id": 13, "star": "⭐", "question": "Feature Scaling", "definition": "Feature scaling normalizes values to bring features into same range.", "points": ["Normalization scales between zero and one", "Standardization gives mean zero variance", "Improves distance based algorithms", "Prevents feature dominance"], "example": "Normalization", "type": "standard"},
            {"id": 14, "star": "⭐", "question": "Feature Selection", "definition": "Feature selection chooses important features to improve model performance.", "points": ["Removes irrelevant noisy features", "Reduces dimensionality of data", "Improves model accuracy", "Reduces training time"], "example": "Selection", "type": "standard"},
        ],
    },
    {
        "id": "unit-2",
        "number": 2,
        "title": "Algorithms (Most Important)",
        "questions": [
            {"id": 15, "star": "⭐⭐⭐", "question": "SVM (VERY IMPORTANT)", "definition": "SVM is supervised algorithm that separates data using optimal hyperplane.", "points": ["Finds hyperplane between classes", "Uses support vectors near boundary", "Maximizes margin for accuracy", "Kernel handles nonlinear data"], "example": "Classification", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/7/72/SVM_margin.png", "diagram_caption": "SVM separating classes with maximum margin."},
            {"id": 16, "star": "⭐⭐⭐", "question": "K-Medoids", "definition": "K medoids clustering uses actual data points as cluster centers.", "points": ["Select initial medoids", "Assign points to nearest medoid", "Update medoids based on cost", "Repeat until stable"], "example": "Clustering", "type": "standard"},
            {"id": 17, "star": "⭐", "question": "KMeans vs KMedoids", "definition": "K Means and K Medoids differ in center choice and robustness.", "differences": [["Mean value", "Actual data point"], ["Sensitive", "Less sensitive"], ["Faster", "Slower"], ["Less stable", "More stable"]], "difference_headers": ["K-Means", "K-Medoids"], "difference_basis": ["Center", "Outliers", "Speed", "Stability"], "example": "Clustering", "type": "difference"},
            {"id": 18, "star": "⭐⭐", "question": "Dimensionality Reduction", "definition": "Dimensionality reduction reduces features while keeping important information.", "points": ["Reduces complexity of data", "Avoids overfitting problem", "Improves computation speed", "Enables better visualization"], "example": "PCA", "type": "standard"},
            {"id": 19, "star": "⭐⭐", "question": "PCA", "definition": "PCA transforms data into components preserving maximum variance.", "points": ["Converts data into components", "Captures maximum variance", "Reduces noise and redundancy", "Improves efficiency"], "example": "PCA", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/f/f5/GaussianScatterPCA.svg", "diagram_caption": "PCA projects data along principal components."},
            {"id": 20, "star": "⭐⭐", "question": "Association Rule Learning", "definition": "Association rule learning finds relationships between items in datasets.", "points": ["Identifies hidden patterns", "Uses support confidence metrics", "Useful in market analysis", "Generates rules"], "example": "Retail", "type": "standard"},
            {"id": 21, "star": "⭐⭐⭐", "question": "Apriori Algorithm", "definition": "Apriori finds frequent itemsets using support and confidence.", "points": ["Generates candidate itemsets", "Removes low support items", "Builds larger itemsets", "Generates association rules"], "example": "Market", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/5/59/Association_rules.svg", "diagram_caption": "Association rule mining flow used for Apriori-style study."},
            {"id": 22, "star": "⭐", "question": "Eclat Algorithm", "definition": "Eclat finds frequent itemsets using transaction ID sets.", "points": ["Uses depth first search", "Uses TID intersections", "Faster than apriori", "Efficient for dense data"], "example": "Mining", "type": "standard"},
            {"id": 23, "star": "⭐⭐", "question": "Generative Models", "definition": "Generative models learn data distribution and generate new data samples.", "points": ["Learns patterns from dataset", "Generates realistic new data", "Uses probability models", "Used in AI generation"], "example": "GAN", "type": "standard"},
            {"id": 24, "star": "⭐⭐⭐", "question": "GAN", "definition": "GAN uses generator and discriminator networks to create realistic data.", "points": ["Generator creates fake data", "Discriminator detects fake data", "Both compete and improve", "Produces realistic outputs"], "example": "Images", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/9/99/GANs.svg", "diagram_caption": "GAN with generator and discriminator flow."},
            {"id": 25, "star": "⭐⭐⭐", "question": "VAE", "definition": "VAE learns latent representation and generates new data.", "points": ["Uses encoder and decoder", "Maps data to latent space", "Generates new samples", "Uses probability distribution"], "example": "Generation", "type": "standard"},
            {"id": 26, "star": "⭐⭐⭐", "question": "VAE vs GAN", "definition": "VAE and GAN differ in generation goal, training, and output style.", "differences": [["Smooth but blurry", "Sharp realistic"], ["Stable", "Difficult"], ["Probabilistic", "Adversarial"], ["Reconstruction", "Realistic generation"]], "difference_headers": ["VAE", "GAN"], "difference_basis": ["Output", "Training", "Method", "Goal"], "example": "Generation", "type": "difference"},
        ],
    },
    {
        "id": "unit-3",
        "number": 3,
        "title": "ANN (Important)",
        "questions": [
            {"id": 27, "star": "⭐⭐⭐", "question": "ANN", "definition": "ANN is computational model inspired by human brain used for pattern recognition.", "points": ["Contains input hidden output layers", "Uses neurons with weights and bias", "Applies activation functions", "Learns using backpropagation"], "example": "Recognition", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/4/46/Colored_neural_network.svg", "diagram_caption": "Basic ANN layer diagram."},
            {"id": 28, "star": "⭐⭐", "question": "Perceptron", "definition": "Perceptron is single layer neural network used for binary classification.", "points": ["Takes weighted sum of inputs", "Applies step activation function", "Produces binary output", "Updates weights using rule"], "example": "Binary", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Perceptron_example.svg", "diagram_caption": "Perceptron input-weight-output diagram."},
            {"id": 29, "star": "⭐⭐", "question": "Gradient Descent", "definition": "Gradient descent minimizes loss by updating weights in direction of negative gradient.", "points": ["Initializes weights randomly", "Calculates loss function", "Updates weights iteratively", "Stops when error minimized"], "example": "Optimization", "type": "standard"},
            {"id": 30, "star": "⭐", "question": "AdaGrad", "definition": "AdaGrad adapts learning rate for each parameter based on past gradients.", "points": ["Uses adaptive learning rate", "Stores squared gradients", "Works well for sparse data", "Learning rate decreases over time"], "example": "NLP", "type": "standard"},
            {"id": 31, "star": "⭐", "question": "Adam", "definition": "Adam optimizer combines momentum and RMSProp for faster convergence.", "points": ["Uses first moment gradients", "Uses second moment gradients", "Applies bias correction", "Fast and stable optimization"], "example": "Training", "type": "standard"},
        ],
    },
    {
        "id": "unit-4",
        "number": 4,
        "title": "CNN",
        "questions": [
            {"id": 32, "star": "⭐⭐⭐", "question": "CNN", "definition": "CNN is neural network designed for image processing using convolution layers.", "points": ["Convolution extracts feature maps", "Pooling reduces spatial size", "Fully connected gives output", "Uses filters for detection"], "example": "Images", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Typical_cnn.png", "diagram_caption": "CNN pipeline from image to feature maps and output."},
            {"id": 33, "star": "⭐⭐", "question": "Pooling", "definition": "Pooling reduces feature map size while preserving important information.", "points": ["Reduces dimensionality", "Decreases computation cost", "Prevents overfitting", "Provides translation invariance"], "example": "Max", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Max_pooling.png", "diagram_caption": "Pooling operation over feature maps."},
        ],
    },
    {
        "id": "unit-5",
        "number": 5,
        "title": "RNN / LSTM",
        "questions": [
            {"id": 34, "star": "⭐⭐⭐", "question": "RNN", "definition": "RNN processes sequential data using previous outputs as memory.", "points": ["Handles sequential data", "Maintains internal memory", "Uses previous state", "Suffers vanishing gradient"], "example": "Text", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Recurrent_neural_network_unfold.svg", "diagram_caption": "Unfolded RNN sequence flow."},
            {"id": 35, "star": "⭐⭐", "question": "LSTM", "definition": "LSTM improves RNN using gates to store and forget information.", "points": ["Uses forget input output gates", "Stores long term dependencies", "Solves vanishing gradient", "Used in sequence prediction"], "example": "Sequence", "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/3/3b/The_LSTM_cell.png", "diagram_caption": "LSTM cell with gates and memory path."},
            {"id": 36, "star": "⭐⭐", "question": "GPT basics", "definition": "GPT is transformer based language model that predicts next token using self attention.", "points": ["Uses transformer decoder blocks", "Learns from large text data", "Generates text token by token", "Useful for chat summarization and writing"], "example": "Text generation", "type": "standard"},
        ],
    },
]

ML_MUST_STUDY = [
    {"label": "SVM", "unit": "Unit 2", "question_id": 15, "priority": "⭐⭐⭐ HIGH PRIORITY"},
    {"label": "K-Medoids", "unit": "Unit 2", "question_id": 16, "priority": "⭐⭐⭐ HIGH PRIORITY"},
    {"label": "PCA", "unit": "Unit 2", "question_id": 19, "priority": "⭐⭐⭐ HIGH PRIORITY"},
    {"label": "Apriori Algorithm", "unit": "Unit 2", "question_id": 21, "priority": "⭐⭐⭐ HIGH PRIORITY"},
    {"label": "GAN vs VAE", "unit": "Unit 2", "question_id": 26, "priority": "⭐⭐⭐ HIGH PRIORITY"},
    {"label": "Feature Engineering (all types)", "unit": "Unit 1", "question_id": 9, "priority": "⭐⭐ IMPORTANT"},
    {"label": "Feature Scaling vs Feature Selection", "unit": "Unit 1", "question_id": 13, "priority": "⭐⭐ IMPORTANT"},
    {"label": "Perceptron + Activation Functions", "unit": "Unit 3", "question_id": 28, "priority": "⭐⭐ IMPORTANT"},
    {"label": "CNN Architecture + Layers", "unit": "Unit 4", "question_id": 32, "priority": "⭐⭐ IMPORTANT"},
    {"label": "RNN / LSTM + GPT basics", "unit": "Unit 5", "question_id": 34, "priority": "⭐⭐ IMPORTANT"},
]

ML_IMPORTANT_QUESTION_BANK = [
    {
        "unit": "Unit 2",
        "priority": "Most Important",
        "color": "red",
        "items": [
            {"stars": "⭐⭐⭐", "text": "Q.1 Explain Support Vector Machines. Explain the working, types and Python code", "question_id": 15},
            {"stars": "⭐⭐⭐", "text": "Q.2 Explain K-Mediod Algorithm, working and implementation", "question_id": 16},
            {"stars": "⭐⭐⭐", "text": "Q.3 Difference between K-Means Clustering and K-Mediod Algorithm", "question_id": 17},
            {"stars": "⭐⭐", "text": "Q.4 Explain Dimensionality Reduction", "question_id": 18},
            {"stars": "⭐⭐", "text": "Q.10 Explain PCA (Principal Component Analysis)", "question_id": 19},
            {"stars": "⭐⭐", "text": "Q.11 Explain Association Rule Learning", "question_id": 20},
            {"stars": "⭐⭐⭐", "text": "Q.12 Explain Apriori Algorithm", "question_id": 21},
            {"stars": "⭐⭐", "text": "Q.13 Explain Eclat Algorithm", "question_id": 22},
            {"stars": "⭐⭐", "text": "Q.11 (Generative) What is Generative Models", "question_id": 23},
            {"stars": "⭐⭐⭐", "text": "Q.15 Explain Generative Adversarial Networks (GANs)", "question_id": 24},
            {"stars": "⭐⭐⭐", "text": "Q.16 Explain Variational AutoEncoders (VAE)", "question_id": 25},
            {"stars": "⭐⭐⭐", "text": "Q.17 Compare VAE and GAN", "question_id": 26},
        ],
    },
    {
        "unit": "Unit 1",
        "priority": "Important",
        "color": "green",
        "items": [
            {"stars": "⭐⭐", "text": "Q.1 What is ML Model and explain the features of ML Model", "question_id": 1},
            {"stars": "⭐⭐", "text": "Q.2 Explain the components of Machine Learning", "question_id": 2},
            {"stars": "⭐⭐", "text": "Q.3 Explain the Types of ML algorithm", "question_id": 3},
            {"stars": "⭐⭐", "text": "Q.6 Explain Model Selection Techniques", "question_id": 6},
            {"stars": "⭐⭐", "text": "Q.8 Explain training a model for supervised learning", "question_id": 8},
            {"stars": "⭐⭐", "text": "Q.9 Explain Feature Engineering", "question_id": 9},
            {"stars": "⭐⭐", "text": "Q.13 Explain Feature Scaling", "question_id": 13},
            {"stars": "⭐⭐", "text": "Q.14 Explain Feature Selection", "question_id": 14},
        ],
    },
    {
        "unit": "Unit 3",
        "priority": "Important",
        "color": "yellow",
        "items": [
            {"stars": "⭐⭐⭐", "text": "Q.1 Explain ANN", "question_id": 27},
            {"stars": "⭐⭐⭐", "text": "Q.5 Explain Perceptron, components, working, types and training rule", "question_id": 28},
            {"stars": "⭐⭐", "text": "Q.6 Explain Gradient descent and types", "question_id": 29},
            {"stars": "⭐⭐", "text": "Q.7 Explain Stochastic Gradient Descent", "question_id": None},
            {"stars": "⭐⭐", "text": "Q.8 Explain Mini-Batch Gradient Descent", "question_id": None},
            {"stars": "⭐", "text": "Q.9 Explain AdaGrad (Adaptive Gradient)", "question_id": 30},
            {"stars": "⭐", "text": "Q.10 Explain Adam (Adaptive Moment Estimation)", "question_id": 31},
            {"stars": "⭐⭐", "text": "Q.11 Explain Sigmoid Function", "question_id": None},
            {"stars": "⭐⭐", "text": "Q.12 Explain ReLU", "question_id": None},
            {"stars": "⭐", "text": "Q.13 Explain Tanh", "question_id": None},
            {"stars": "⭐", "text": "Q.14 Explain Softmax", "question_id": None},
        ],
    },
    {
        "unit": "Unit 4",
        "priority": "Important",
        "color": "yellow",
        "items": [
            {"stars": "⭐⭐⭐", "text": "Q.1 Explain CNN", "question_id": 32},
            {"stars": "⭐⭐", "text": "Q.2 Explain Padding", "question_id": None},
            {"stars": "⭐⭐", "text": "Q.3 Explain Strided Convolution", "question_id": None},
            {"stars": "⭐⭐", "text": "Q.4 Explain Pooling", "question_id": 33},
            {"stars": "⭐", "text": "Q.5 Explain LeNet", "question_id": None},
            {"stars": "⭐", "text": "Q.6 Explain AlexNet", "question_id": None},
            {"stars": "⭐", "text": "Q.7 Explain VGGNet", "question_id": None},
            {"stars": "⭐", "text": "Q.8 Explain ResNet", "question_id": None},
            {"stars": "⭐", "text": "Q.9 Explain GoogleNet", "question_id": None},
        ],
    },
    {
        "unit": "Unit 5",
        "priority": "Important",
        "color": "yellow",
        "items": [
            {"stars": "⭐⭐⭐", "text": "Q.1 Explain Sequential Data: Recurrent Neural Networks", "question_id": 34},
            {"stars": "⭐⭐⭐", "text": "Q.2 What is Long Short-Term Memory (LSTM)", "question_id": 35},
            {"stars": "⭐⭐", "text": "Q.3 Explain Gated Recurrent Units (GRU)", "question_id": None},
        ],
    },
]

COMPLETE_QUESTION_TEXTS = {
    1: "What is ML Model and explain the features of ML Model",
    2: "Explain the components of Machine Learning",
    3: "Explain the Types of ML algorithm",
    6: "Explain Model Selection Techniques",
    8: "Explain training a model for supervised learning",
    9: "Explain Feature Engineering",
    13: "Explain Feature Scaling",
    14: "Explain Feature Selection",
    15: "Explain Support Vector Machines. Explain the working, types and Python code",
    16: "Explain K-Mediod Algorithm, working and implementation",
    17: "Difference between K-Means Clustering and K-Mediod Algorithm",
    18: "Explain Dimensionality Reduction",
    19: "Explain PCA (Principal Component Analysis)",
    20: "Explain Association Rule Learning",
    21: "Explain Apriori Algorithm",
    22: "Explain Eclat Algorithm",
    23: "What is Generative Models",
    24: "Explain Generative Adversarial Networks (GANs)",
    25: "Explain Variational AutoEncoders (VAE)",
    26: "Compare VAE and GAN",
    27: "Explain ANN",
    28: "Explain Perceptron, components, working, types and training rule",
    29: "Explain Gradient descent and types",
    30: "Explain AdaGrad (Adaptive Gradient)",
    31: "Explain Adam (Adaptive Moment Estimation)",
    32: "Explain CNN",
    33: "Explain Pooling",
    34: "Explain Sequential Data: Recurrent Neural Networks",
    35: "What is Long Short-Term Memory (LSTM)",
}


IMPORTANT_EXTRA_POINTS = {
    1: ["Helps automate decision making in real world tasks", "Can generalize learned patterns to unseen data", "Works with classification regression and recommendation tasks", "Supports data driven problem solving in business and research"],
    2: ["Training data provides learning examples to the model", "Features act as inputs used for prediction", "Validation data helps tune model settings", "Test data checks final model performance fairly"],
    3: ["Classification predicts category labels", "Regression predicts continuous values", "Clustering groups similar records together", "Recommendation systems suggest relevant items to users"],
    4: ["Avoids underfitting and overfitting problems", "Balances model complexity with performance", "Uses validation results for comparison", "Chooses model suitable for deployment needs"],
    5: ["Consider size and quality of available data", "Compare model speed and memory cost", "Prefer interpretable models when explanation matters", "Validate using unseen data before final choice"],
    6: ["Holdout method uses separate train and test split", "Grid search tests multiple hyperparameter combinations", "Random search samples configurations efficiently", "Validation score guides final model choice"],
    7: ["Lower metric values usually mean better regression fit", "Different metrics highlight different error behavior", "RMSE penalizes large errors strongly", "R2 closer to one indicates strong fit"],
    8: ["Split dataset into training validation and test sets", "Encode labels into usable machine format", "Tune hyperparameters after first training run", "Monitor model performance to avoid overfitting"],
    9: ["Improves data quality before model training", "Handles missing noisy and inconsistent values", "Makes patterns easier for models to learn", "Directly affects final model accuracy and speed"],
    13: ["Important for KNN SVM and K means algorithms", "Makes gradient based training more stable", "Helps faster convergence during optimization", "Keeps large scale features from dominating distance calculations"],
    14: ["Can use filter wrapper and embedded methods", "Helps reduce storage and memory needs", "Makes models easier to interpret", "Improves generalization on unseen data"],
    15: ["Works well for high dimensional datasets", "Can perform both classification and regression", "Linear and nonlinear kernels are available", "Effective when margin between classes is clear"],
    16: ["Uses real samples as cluster representatives", "More robust than K means for noisy data", "Cost function is based on pairwise distance", "Useful when outliers affect mean values"],
    17: ["K medoids works better on noisy datasets", "K means updates centroids using averages", "K medoids selects actual objects as centers", "Choice depends on speed versus robustness needs"],
    18: ["Removes redundant correlated features", "Simplifies visualization of complex data", "Useful before clustering or classification", "Often used in preprocessing pipelines"],
    19: ["Eigenvectors define principal component directions", "Eigenvalues measure amount of variance captured", "Principal components are uncorrelated with each other", "Often applied after scaling the data"],
    20: ["Common in retail recommendation analysis", "Rules help discover items bought together", "Lift shows strength beyond random chance", "Useful for cross selling strategies"],
    21: ["Based on downward closure property", "Frequent subsets help generate larger candidate sets", "Confidence evaluates rule reliability", "Widely used in market basket analysis"],
    22: ["Uses vertical database layout for mining", "Intersects transaction lists to find support", "Can be memory intensive on very large sparse data", "Useful when dense datasets are available"],
    23: ["Can generate images text audio or other content", "Often trained using deep neural networks", "Useful in simulation augmentation and creativity tools", "Learns underlying probability distribution of data"],
    24: ["Training is a minimax optimization process", "Generator learns to fool the discriminator", "Discriminator learns to separate real and fake samples", "Used in image synthesis super resolution and style transfer"],
    25: ["Latent space allows smooth interpolation between samples", "Decoder reconstructs output from latent representation", "Useful for anomaly detection and data generation", "Optimization includes reconstruction and KL divergence losses"],
    26: ["VAE focuses on structured latent representation", "GAN often creates sharper outputs for images", "VAE is easier to train in many settings", "GAN is popular for realistic media synthesis"],
    27: ["Hidden layers help model complex nonlinear patterns", "Weights are adjusted during training", "Bias shifts neuron activation threshold", "Used in speech image and text tasks"],
    28: ["It is the basic building block of neural networks", "Works only when classes are linearly separable", "Activation decides whether neuron fires", "Perceptron learning rule updates weights after mistakes"],
    29: ["Learning rate controls update step size", "Too large learning rate may overshoot minima", "Too small learning rate slows training", "Used in most neural network optimization methods"],
    30: ["Useful for sparse features in NLP tasks", "Each parameter gets its own adjusted step size", "Large historical gradients reduce future updates", "Can slow too much after many updates"],
    31: ["Combines benefits of momentum and adaptive rates", "Common default optimizer in deep learning", "Works well on noisy gradients", "Usually converges faster than plain SGD"],
    32: ["Local receptive fields capture nearby patterns", "Shared weights reduce number of parameters", "Deep layers learn higher level visual features", "Used in classification detection and segmentation"],
    33: ["Max pooling takes strongest activation value", "Average pooling computes mean value in region", "Helps reduce sensitivity to small shifts", "Shrinks feature maps for faster processing"],
    34: ["Useful for language speech and time series data", "Output depends on current input and previous hidden state", "Weight sharing happens across time steps", "Basic RNN struggles with long term dependencies"],
    35: ["Cell state carries long term information forward", "Forget gate removes unneeded information", "Input gate controls new information storage", "Widely used in sequence modeling and forecasting"],
    36: ["GPT uses self attention to relate tokens in context", "Pretraining happens on massive text corpora", "Fine tuning or prompting adapts it to tasks", "Used for chat summarization coding and writing support"],
}

QUESTION_EXAMPLES = {
    1: ["Prediction", "Fraud detection", "Spam filtering", "Sales forecasting", "Disease diagnosis"],
    2: ["Accuracy", "Precision", "Recall", "F1 score", "ROC AUC"],
    3: ["Clustering", "Classification", "Regression", "Recommendation", "Anomaly detection"],
    4: ["Selection", "Cross validation choice", "Hyperparameter tuning", "Best classifier pick", "Best regressor pick"],
    5: ["CNN", "RNN", "SVM", "Random Forest", "K Means"],
    6: ["AIC", "BIC", "Cross validation", "Bootstrap", "Grid search"],
    7: ["MAE", "MSE", "RMSE", "R2", "Adjusted R2"],
    8: ["Classification", "Sentiment analysis", "Email spam detection", "Loan approval", "Disease prediction"],
    9: ["Preprocessing", "Scaling", "Encoding", "Feature creation", "Transformation"],
    10: ["Scaling", "Binning", "Polynomial features", "Log transform", "Normalization"],
    11: ["Encoding", "One hot encoding", "Label encoding", "Target encoding", "Frequency encoding"],
    12: ["NLP", "TF IDF", "Bag of words", "Word2Vec", "Tokenization"],
    13: ["Normalization", "Standardization", "Min max scaling", "Z score scaling", "Robust scaling"],
    14: ["Selection", "Filter method", "Wrapper method", "Embedded method", "Recursive elimination"],
    15: ["Classification", "Text classification", "Image classification", "Spam detection", "Margin based separation"],
    16: ["Clustering", "Customer segmentation", "Document grouping", "Gene clustering", "Outlier robust grouping"],
    17: ["Clustering", "Customer grouping", "Robust clustering", "Fast clustering", "Partitioning"],
    18: ["PCA", "Feature compression", "Data visualization", "Noise reduction", "Preprocessing"],
    19: ["PCA", "Face recognition", "Data compression", "Visualization", "Noise reduction"],
    20: ["Retail", "Basket analysis", "Product recommendation", "Cross selling", "Purchase patterns"],
    21: ["Market", "Shopping basket", "Product bundles", "Association rules", "Frequent itemsets"],
    22: ["Mining", "Frequent itemsets", "Dense transaction analysis", "TID set mining", "Pattern discovery"],
    23: ["GAN", "VAE", "Diffusion", "Language generation", "Image synthesis"],
    24: ["Images", "Face generation", "Super resolution", "Style transfer", "Synthetic data"],
    25: ["Generation", "Anomaly detection", "Latent sampling", "Image generation", "Representation learning"],
    26: ["Generation", "Image synthesis", "Reconstruction", "Latent modeling", "Media generation"],
    27: ["Recognition", "Handwriting recognition", "Speech recognition", "Pattern detection", "Prediction"],
    28: ["Binary", "AND gate", "OR gate", "Binary classifier", "Linearly separable data"],
    29: ["Optimization", "Neural network training", "Loss minimization", "Weight updates", "Gradient based learning"],
    30: ["NLP", "Sparse features", "Text classification", "Online learning", "Adaptive optimization"],
    31: ["Training", "Deep learning", "Image classification", "Text modeling", "Stable optimization"],
    32: ["Images", "Object detection", "Image classification", "Face recognition", "Medical imaging"],
    33: ["Max", "Average pooling", "Feature reduction", "CNN compression", "Spatial downsampling"],
    34: ["Text", "Language modeling", "Speech processing", "Time series forecasting", "Sequence tagging"],
    35: ["Sequence", "Machine translation", "Speech recognition", "Time series", "Text generation"],
    36: ["Text generation", "Chatbots", "Summarization", "Question answering", "Code assistance"],
}


def enrich_ml_questions() -> None:
    for unit in ML_UNITS:
        for question in unit["questions"]:
            if question["id"] in COMPLETE_QUESTION_TEXTS:
                question["question"] = COMPLETE_QUESTION_TEXTS[question["id"]]
            question["examples"] = QUESTION_EXAMPLES.get(question["id"], [question.get("example", "")])
            if question.get("star") and question["id"] in IMPORTANT_EXTRA_POINTS:
                question["points"] = question.get("points", []) + IMPORTANT_EXTRA_POINTS.get(question["id"], [])


PIP_UNITS = [
    {
        "id": "pip-unit-1",
        "number": 1,
        "title": "Basics",
        "marks": "12 marks",
        "questions": [
            {"id": 101, "star": "⭐⭐⭐", "question": "What is Digital Image Processing", "definition": "Digital image processing is technique used to manipulate images using computer algorithms.", "points": ["Enhances image quality and clarity", "Removes noise from images", "Extracts useful information from images", "Used in various real applications"], "examples": ["Medical", "Satellite imaging", "Face recognition", "Document scanning", "Surveillance"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Digital_image_processing_pipeline.png", "diagram_caption": "Basic digital image processing pipeline."},
            {"id": 102, "star": "⭐⭐⭐", "question": "Fundamental Steps in Image Processing", "definition": "Image processing involves sequence of steps to improve and analyze digital images.", "points": ["Image acquisition captures input image", "Preprocessing improves image quality", "Segmentation divides image into regions", "Analysis extracts meaningful information"], "examples": ["Analysis", "Inspection", "Recognition", "Automation", "Classification"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/5/54/Image_processing_steps.png", "diagram_caption": "Common stages in an image processing workflow."},
            {"id": 103, "star": "⭐⭐", "question": "Components of Image Processing System", "definition": "Image processing system consists of hardware and software used to process images.", "points": ["Image sensor captures raw image", "Processing unit performs operations", "Storage stores image data", "Output device displays results"], "examples": ["Camera", "Scanner", "GPU system", "Monitor", "Storage"], "type": "standard"},
            {"id": 104, "star": "⭐⭐", "question": "Image Sampling and Quantization", "definition": "Sampling converts continuous image to discrete form while quantization assigns intensity values.", "points": ["Sampling defines spatial resolution", "Quantization defines intensity levels", "Higher sampling gives better quality", "Quantization reduces gray levels"], "examples": ["Pixels", "8 bit image", "Resolution setting", "Gray levels", "Digitization"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Sampling_quantization.png", "diagram_caption": "Sampling and quantization convert an analog image into digital form."},
            {"id": 105, "star": "⭐⭐", "question": "Types of Images", "definition": "Images are classified based on intensity values and color representation.", "points": ["Binary image uses two values", "Grayscale uses multiple intensity levels", "Color image uses RGB components", "Multispectral captures multiple bands"], "examples": ["RGB", "Binary image", "Grayscale image", "Multispectral image", "Color photo"], "type": "standard"},
        ],
    },
    {
        "id": "pip-unit-2",
        "number": 2,
        "title": "Image Enhancement",
        "marks": "16 marks",
        "questions": [
            {"id": 106, "star": "⭐⭐⭐", "question": "Histogram and Histogram Equalization", "definition": "Histogram represents pixel intensity distribution and equalization improves contrast of image.", "points": ["Histogram shows frequency of intensities", "Equalization spreads intensity values", "Enhances image contrast effectively", "Useful for low contrast images"], "examples": ["Contrast", "Low contrast image", "Medical scan", "X ray improvement", "Night image"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/c/ca/Histogrammeinebnung.png", "diagram_caption": "Histogram equalization improves the spread of intensity values."},
            {"id": 107, "star": "⭐⭐⭐", "question": "Image Enhancement in Spatial Domain", "definition": "Spatial domain enhancement modifies pixel values directly to improve image quality.", "points": ["Works directly on pixel values", "Uses filtering techniques", "Improves brightness and contrast", "Simple and easy to implement"], "examples": ["Filtering", "Smoothing", "Sharpening", "Brightness adjustment", "Contrast stretch"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Spatial_filtering.png", "diagram_caption": "Spatial domain methods operate directly on neighboring pixels."},
            {"id": 108, "star": "⭐⭐", "question": "Image Enhancement in Frequency Domain", "definition": "Frequency domain enhancement processes image using Fourier transform.", "points": ["Converts image into frequency domain", "Uses filters like low pass", "Removes noise effectively", "Improves image details"], "examples": ["FFT", "Low pass filter", "High pass filter", "Spectrum analysis", "Frequency filtering"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/8/86/2D_Fourier_transform_example.png", "diagram_caption": "Frequency domain processing uses transforms before filtering."},
            {"id": 109, "star": "⭐⭐", "question": "Difference Spatial vs Frequency", "definition": "Spatial and frequency enhancement differ in operation method and processing complexity.", "differences": [["Direct pixel manipulation", "Uses transform methods"], ["Simple implementation", "More complex process"], ["Faster processing", "Slower computation"], ["Basic enhancement tasks", "Advanced filtering"]], "difference_headers": ["Spatial Domain", "Frequency Domain"], "difference_basis": ["Operation", "Complexity", "Speed", "Use"], "examples": ["Enhancement", "Filtering", "FFT", "Spatial processing", "Frequency filtering"], "type": "difference"},
        ],
    },
    {
        "id": "pip-unit-3",
        "number": 3,
        "title": "Image Restoration",
        "marks": "14 marks",
        "questions": [
            {"id": 110, "star": "⭐⭐⭐", "question": "Image Restoration", "definition": "Image restoration recovers original image by removing degradation and noise.", "points": ["Removes blur and noise", "Uses mathematical models", "Improves image accuracy", "Restores original quality"], "examples": ["Restoration", "Deblurring", "Denoising", "Satellite cleanup", "Medical correction"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/9/99/Image_restoration_example.png", "diagram_caption": "Restoration tries to recover the original scene from degraded input."},
            {"id": 111, "star": "⭐⭐", "question": "Noise Models", "definition": "Noise models describe unwanted variations in images affecting quality.", "points": ["Gaussian noise affects intensity", "Salt and pepper noise appears randomly", "Speckle noise common in radar images", "Poisson noise based on distribution"], "examples": ["Noise", "Gaussian", "Salt and pepper", "Speckle", "Poisson"], "type": "standard"},
            {"id": 112, "star": "⭐⭐", "question": "Filtering Techniques", "definition": "Filtering techniques remove noise and improve image quality.", "points": ["Mean filter smooths image", "Median filter removes noise", "Gaussian filter reduces blur", "Sharpening enhances edges"], "examples": ["Filter", "Mean filter", "Median filter", "Gaussian filter", "Sharpening"], "type": "standard"},
        ],
    },
    {
        "id": "pip-unit-4",
        "number": 4,
        "title": "Image Compression",
        "marks": "14 marks",
        "questions": [
            {"id": 113, "star": "⭐⭐⭐", "question": "Image Compression", "definition": "Image compression reduces image size while maintaining acceptable quality.", "points": ["Reduces storage requirements", "Speeds data transmission", "Removes redundant data", "Maintains image quality"], "examples": ["JPEG", "PNG", "Web transfer", "Storage saving", "Compression"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/5/56/Data_Compression.png", "diagram_caption": "Compression reduces size by removing redundancy."},
            {"id": 114, "star": "⭐⭐", "question": "Lossy vs Lossless Compression", "definition": "Lossy and lossless compression differ in data preservation and image quality.", "differences": [["Some data lost", "No data lost"], ["Reduced quality", "Original quality"], ["High compression", "Low compression"], ["Images videos", "Text files"]], "difference_headers": ["Lossy", "Lossless"], "difference_basis": ["Data loss", "Quality", "Size", "Use"], "examples": ["JPEG", "PNG", "MP3", "ZIP", "Compression"], "type": "difference"},
            {"id": 115, "star": "⭐⭐", "question": "JPEG Compression", "definition": "JPEG compression reduces image size using lossy compression techniques.", "points": ["Uses discrete cosine transform", "Removes high frequency data", "Applies quantization", "Compresses image efficiently"], "examples": ["JPEG", "DCT", "Quantization", "Photo storage", "Web images"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/3/38/JPEG_Process.svg", "diagram_caption": "JPEG architecture includes DCT, quantization, and encoding stages."},
        ],
    },
    {
        "id": "pip-unit-5",
        "number": 5,
        "title": "Segmentation & Representation",
        "marks": "14 marks",
        "questions": [
            {"id": 116, "star": "⭐⭐⭐", "question": "Image Segmentation", "definition": "Image segmentation divides image into meaningful regions for analysis.", "points": ["Separates objects from background", "Groups similar pixels", "Simplifies image analysis", "Used in recognition tasks"], "examples": ["Detection", "Medical imaging", "Object isolation", "Recognition", "Scene analysis"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Image_segmentation_example.png", "diagram_caption": "Segmentation isolates meaningful regions from the image."},
            {"id": 117, "star": "⭐⭐", "question": "Edge Detection", "definition": "Edge detection identifies boundaries of objects in image.", "points": ["Detects sharp intensity changes", "Uses operators like Sobel", "Helps in object detection", "Improves feature extraction"], "examples": ["Edges", "Sobel", "Canny", "Boundary detection", "Feature extraction"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Sobel_filter_example.png", "diagram_caption": "Edge operators highlight boundaries with high intensity change."},
            {"id": 118, "star": "⭐⭐", "question": "Thresholding", "definition": "Thresholding separates objects based on intensity values.", "points": ["Converts grayscale to binary", "Uses threshold value", "Simple segmentation method", "Works for simple images"], "examples": ["Binary", "Segmentation", "Otsu method", "Document scan", "Foreground extraction"], "type": "standard", "diagram_url": "https://upload.wikimedia.org/wikipedia/commons/3/34/Otsu%27s_Method_Visualization.png", "diagram_caption": "Thresholding selects a cutoff to separate object and background."},
            {"id": 119, "star": "⭐⭐", "question": "Region-Based Segmentation", "definition": "Region based segmentation groups pixels with similar properties.", "points": ["Uses region growing method", "Groups similar pixels", "Produces continuous regions", "Accurate segmentation"], "examples": ["Regions", "Region growing", "Grouping", "Segmentation", "Medical image"], "type": "standard"},
            {"id": 120, "star": "⭐⭐", "question": "Representation and Description", "definition": "Representation describes region structure and features of segmented image.", "points": ["Boundary representation shows edges", "Region representation shows areas", "Descriptors extract features", "Used for recognition"], "examples": ["Features", "Shape descriptor", "Boundary", "Region feature", "Recognition"], "type": "standard"},
        ],
    },
]

PIP_IMPORTANT_QUESTION_BANK = [
    {"unit": "Unit 2", "priority": "Most Important - 16 marks", "color": "red", "items": [
        {"stars": "⭐⭐⭐", "text": "Histogram & Histogram Equalization", "question_id": 106},
        {"stars": "⭐⭐⭐", "text": "Image Enhancement in Spatial Domain", "question_id": 107},
        {"stars": "⭐⭐", "text": "Spatial vs Frequency Domain (Difference)", "question_id": 109},
    ]},
    {"unit": "Unit 5", "priority": "Very Scoring", "color": "red", "items": [
        {"stars": "⭐⭐⭐", "text": "Image Segmentation", "question_id": 116},
        {"stars": "⭐⭐", "text": "Edge Detection", "question_id": 117},
        {"stars": "⭐⭐", "text": "Thresholding", "question_id": 118},
    ]},
    {"unit": "Unit 4", "priority": "Easy Marks", "color": "red", "items": [
        {"stars": "⭐⭐⭐", "text": "Image Compression", "question_id": 113},
        {"stars": "⭐⭐", "text": "Lossy vs Lossless (Difference)", "question_id": 114},
        {"stars": "⭐⭐", "text": "JPEG Compression", "question_id": 115},
    ]},
    {"unit": "Unit 1", "priority": "Medium Priority", "color": "yellow", "items": [
        {"stars": "⭐⭐", "text": "Digital Image Processing (Definition + steps)", "question_id": 101},
        {"stars": "⭐⭐", "text": "Sampling & Quantization", "question_id": 104},
    ]},
    {"unit": "Unit 3", "priority": "Medium Priority", "color": "yellow", "items": [
        {"stars": "⭐⭐", "text": "Image Restoration", "question_id": 110},
        {"stars": "⭐⭐", "text": "Noise Models", "question_id": 111},
        {"stars": "⭐⭐", "text": "Filtering (Mean, Median)", "question_id": 112},
    ]},
    {"unit": "Low Priority", "priority": "Skip If Time Less", "color": "green", "items": [
        {"stars": "⚠️", "text": "Components of image system", "question_id": 103},
        {"stars": "⚠️", "text": "Types of images", "question_id": 105},
        {"stars": "⚠️", "text": "Region-based segmentation", "question_id": 119},
        {"stars": "⚠️", "text": "Representation & description", "question_id": 120},
    ]},
]

PIP_MARKS = [
    {"unit": "Unit 1", "topic": "Basics of Image Processing", "marks": "12 marks"},
    {"unit": "Unit 2", "topic": "Image Enhancement", "marks": "16 marks", "highlight": True},
    {"unit": "Unit 3", "topic": "Image Restoration", "marks": "14 marks"},
    {"unit": "Unit 4", "topic": "Image Compression", "marks": "14 marks"},
    {"unit": "Unit 5", "topic": "Segmentation & Representation", "marks": "14 marks"},
]

BDA_UNITS = [
    {
        "id": "bda-unit-1",
        "number": 1,
        "title": "Big Data Basics",
        "marks": "12 marks",
        "priority": "Foundation",
        "learning_hours": "3-4 hrs",
        "syllabus_topics": ["What is Big Data", "Types of Data", "Characteristics (Volume, Velocity, Variety, Veracity)", "Applications", "Advantages and Challenges"],
        "total_2m_questions": 8,
        "total_4m_questions": 1,
        "total_diagram_questions": 1,
        "questions": [
            {"id": 201, "qno": "Q1", "marks": "2M", "importance": "⭐", "question": "Classify Big Data into three primary types with one example each.", "type": "standard", "answer": "Structured Data: Data organized in a fixed format or tabular structure. (Example: Relational Databases / SQL Tables).\nSemi-Structured Data: Data that does not use traditional tables but contains tags or markers to separate elements. (Example: XML files, JSON files, Emails).\nUnstructured Data: Data with no specific format, sequence, or structure. (Example: Videos, Audio files, Social media posts).", "page_number": None, "has_diagram": False},
            {"id": 202, "qno": "Q2", "marks": "2M", "importance": "⭐", "question": "Define Big Data and Big Data Analytics. State any two needs for Big Data Analytics.", "type": "standard", "answer": "Big Data: Extremely large and complex datasets that traditional data processing applications cannot manage, store, or analyze effectively.\nBig Data Analytics: The advanced process of examining Big Data to uncover hidden patterns, unknown correlations, market trends, and customer preferences.\nNeeds:\n• To make faster, more accurate data-driven business decisions.\n• To provide highly personalized customer recommendations and improve user experience.", "page_number": None, "has_diagram": False},
            {"id": 203, "qno": "Q3", "marks": "2M", "importance": "⭐", "question": "List and Define Big Data Types", "type": "standard", "answer": "Structured: Highly organized data that can be easily stored, accessed, and processed in fixed formats (like rows and columns).\nUnstructured: Raw, unorganized data that cannot be stored in traditional relational databases (like images or text documents).\nSemi-Structured: A mix of both; it lacks a strict relational database structure but contains structural tags/keys (like HTML or JSON).", "page_number": None, "has_diagram": False},
            {"id": 204, "qno": "Q4", "marks": "2M", "importance": "⭐", "question": "State any four key features of the Hadoop framework.", "type": "standard", "answer": "Open Source: It is a free, open-source project managed by the Apache Software Foundation.\nDistributed Storage: It stores massive files across multiple independent computers (nodes) using HDFS.\nFault Tolerance: It automatically replicates data across multiple nodes, ensuring no data is lost if a single hardware node fails.\nHigh Scalability: It allows organizations to easily add hundreds of new computer nodes to the cluster without downtime.", "page_number": None, "has_diagram": False},
            {"id": 205, "qno": "Q5", "marks": "2M", "importance": "⭐", "question": "List any four HDFS commands used for interacting with files.", "type": "standard", "answer": "hdfs dfs -ls : Lists all files and directories in the specified HDFS path.\nhdfs dfs -mkdir : Creates a new directory in HDFS.\nhdfs dfs -put : Copies a file from the local file system into HDFS.\nhdfs dfs -cat : Displays the contents of a file stored in HDFS.", "page_number": None, "has_diagram": False},
            {"id": 206, "qno": "Q6", "marks": "2M", "importance": "⭐", "question": "What is a \"Key-Value pair\" in the context of MapReduce?", "type": "standard", "answer": "In MapReduce, all input and output data must be formatted as Key-Value pairs.\n• The \"Key\" acts as a unique identifier or category (e.g., a specific word in a document).\n• The \"Value\" represents the data or metric associated with that key (e.g., the frequency/count of that word).\nThe MapReduce algorithm groups and aggregates data based entirely on these keys.", "page_number": None, "has_diagram": False},
            {"id": 207, "qno": "Q7", "marks": "2M", "importance": "⭐", "question": "State the primary purpose of using NoSQL databases in Big Data management.", "type": "standard", "answer": "The primary purpose of NoSQL (Not Only SQL) databases is to handle massive volumes of unstructured and semi-structured data at high speeds. They provide flexible, schema-less data models and high horizontal scalability, which traditional Relational Databases (RDBMS) cannot offer.", "page_number": None, "has_diagram": False},
            {"id": 208, "qno": "Q8", "marks": "2M", "importance": "⭐", "question": "List and Define Hive Built-in functions.", "type": "standard", "answer": "Apache Hive provides various built-in functions to process data easily:\nMathematical Functions: Performs math operations on data (e.g., ROUND(), SQRT()).\nString Functions: Manipulates text and string values (e.g., UPPER(), LENGTH(), CONCAT()).\nDate Functions: Extracts and manipulates date and time values (e.g., YEAR(), DATEDIFF()).\nAggregate Functions: Performs calculations on multiple rows to return a single summarized value (e.g., SUM(), AVG(), COUNT()).", "page_number": None, "has_diagram": False},
            {"id": 209, "qno": "Q9", "marks": "2M", "importance": "⭐", "question": "List any two characteristics and two limitations of Apache Hive.", "type": "standard", "answer": "Characteristics:\n• It uses a simple, SQL-like querying language called HiveQL.\n• It translates these SQL queries in the background into complex MapReduce jobs automatically.\nLimitations:\n• It is not suitable for Real-Time queries or OLTP (Online Transaction Processing).\n• It suffers from high latency (queries take time to execute due to MapReduce overhead).", "page_number": None, "has_diagram": False},
            {"id": 210, "qno": "Q1", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Differentiate between Structured, Semi-structured, and Unstructured data. [IMP]", "type": "differentiate", "image_path": "UNIT1/UT1_Q1_4m.png", "answer": "TABLE FORMAT:\n\nParameters | Structured Data | Semi-Structured Data | Unstructured Data\n\nDefinition: Data that is highly organized, strictly formatted, and fits neatly into fixed fields. | Data that does not reside in a relational database but has organizational properties like tags or keys. | Raw data that has absolutely no predefined format, sequence, or structural organization.\n\nSchema: Strictly follows a predefined schema (Schema-on-write). | Self-describing schema (Schema-on-read) using tags/markers. | Completely schema-less.\n\nStorage: Stored in traditional Relational Databases (RDBMS) like MySQL, Oracle. | Stored in NoSQL databases, XML/JSON files, or Document stores. | Stored in Data Lakes, Hadoop (HDFS), or NoSQL databases.\n\nSearchability: Extremely easy to search, query, and analyze using standard SQL. | Moderately easy to search using specific parsing tools. | Highly difficult to search and analyze; requires advanced AI/ML or Big Data tools.\n\nVolume: Represents a very small percentage (around 10-20%) of all enterprise data. | Represents a moderate percentage of enterprise data. | Represents the vast majority (80%+) of all global data generated today.\n\nExamples: Employee tables, Bank transaction records, Excel spreadsheets. | Emails, XML files, JSON documents, Web server logs. | Videos (YouTube), Audio files, Images, raw social media posts.", "page_number": None, "has_diagram": True, "diagram_type": "table"},
        ],
    },
    {
        "id": "bda-unit-2",
        "number": 2,
        "title": "Hadoop & HDFS",
        "marks": "16 marks",
        "priority": "CRITICAL - HIGHEST MARKS",
        "learning_hours": "5-6 hrs",
        "syllabus_topics": ["Hadoop Framework", "HDFS Architecture", "HDFS Features", "Hadoop Ecosystem", "YARN Architecture", "Comparison with Traditional Systems"],
        "total_2m_questions": 2,
        "total_4m_questions": 4,
        "total_diagram_questions": 4,
        "questions": [
            {"id": 301, "qno": "Q1", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Explain the core characteristics of Big Data (Volume, Velocity, Variety, Veracity) with real-world examples. [IMP]", "type": "standard", "answer": "The core characteristics of Big Data are traditionally defined by the '4 Vs':\n\nVolume (Scale of Data): Refers to the unimaginably massive amount of data generated every second (Terabytes, Petabytes, Exabytes). Example: Facebook stores over 300 Petabytes of user data, hundreds of hours of video uploaded to YouTube every minute.\n\nVelocity (Speed of Data): Refers to the speed at which new data is being generated and processed. Example: Millions of stock market trades in milliseconds, credit card fraud detection before receipt prints.\n\nVariety (Diversity of Data): Refers to different forms and formats (structured, semi-structured, unstructured). Example: Smart city networks collecting structured sensor data, semi-structured JSON weather APIs, unstructured CCTV video.\n\nVeracity (Uncertainty of Data): Refers to data quality, trustworthiness, and accuracy. Example: Twitter data for sentiment analysis contains typos, slang, fake news, bot spam.", "page_number": None, "has_diagram": False},
            {"id": 302, "qno": "Q2", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Describe the Big Data Processing Architecture Design with a neat block diagram. [IMP]", "type": "standard", "image_path": "UNIT1/UT1_Q3_4m.png", "answer": "Big Data Processing Architecture Design consists of distinct logical layers:\n\nData Sources Layer: Origin of data (relational databases, IoT sensors, social media, server logs).\n\nData Ingestion Layer: Acquires data using tools like Apache Kafka (real-time) or Apache Sqoop (batch loading).\n\nData Storage Layer: Distributed storage systems like HDFS, AWS S3, or NoSQL databases (HBase).\n\nData Processing Layer:\n• Batch Processing: Hadoop MapReduce or Apache Spark\n• Real-Time Processing: Apache Storm or Spark Streaming\n\nData Consumption/Visualization Layer: Business Intelligence tools (Tableau, PowerBI) for dashboards and reports.", "page_number": None, "has_diagram": True, "diagram_type": "architecture"},
            {"id": 303, "qno": "Q3", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Explain the core components of the Hadoop Ecosystem with a suitable diagram. [IMP]", "type": "standard", "image_path": "UNIT2/UT2_Q1_4m.png", "answer": "Hadoop Ecosystem components:\n\nHDFS (Hadoop Distributed File System): The fundamental storage layer breaking massive files into blocks distributed across thousands of nodes.\n\nMapReduce: The original data processing engine allowing parallel processing of massive datasets.\n\nYARN (Yet Another Resource Negotiator): Cluster resource management layer acting as the OS of Hadoop, dynamically allocating CPU and RAM.\n\nExtended Ecosystem Tools:\nApache Hive: SQL-like interface (HiveQL) for querying HDFS data.\nApache Pig: High-level scripting language (Pig Latin) for data transformations and ETL.\nApache Sqoop: Efficiently transfers bulk data between Hadoop and RDBMS.\nApache HBase: Scalable NoSQL database on HDFS for real-time read/write access.", "page_number": None, "has_diagram": True, "diagram_type": "ecosystem"},
            {"id": 304, "qno": "Q4", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Explain the architecture and functioning of HDFS (Hadoop Distributed File System) for data storage. [IMP]", "type": "standard", "image_path": "UNIT2/UT2_Q2_4m.png", "answer": "HDFS Architecture (Master/Slave Model):\n\nNameNode (The Master):\nFunction: Central controller of HDFS cluster maintaining metadata (filesystem namespace, directory tree, file permissions, DataNode block locations).\nHealth Monitoring: Receives 'Heartbeat' signals from slaves constantly.\n\nDataNodes (The Slaves):\nFunction: Worker machines physically storing raw data.\nBlocks: Massive files split into fixed-size chunks (default 128 MB) distributed across multiple DataNodes.\n\nReplication (Fault Tolerance):\nDefault Replication Factor: 3 (each block copied to 3 different DataNodes for data security).\nExample: Block 1 stored on DataNode A, copied to DataNode B and C.\n\nSecondary NameNode:\nFunction: Periodically merges namespace image files, not a backup NameNode.", "page_number": None, "has_diagram": True, "diagram_type": "hdfs_arch"},
            {"id": 305, "qno": "Q5", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Describe the MapReduce Programming Model.", "type": "standard", "answer": "MapReduce is a distributed programming model for parallel processing of massive datasets.\n\nMaster/Slave Architecture:\nJobTracker (Master): Receives job, divides into smaller tasks, schedules on worker nodes.\nTaskTracker (Slave): Runs on every worker node executing assigned data processing tasks.\n\nTwo Fundamental Phases:\n\nMap Phase:\nRaw input data split into independent chunks.\nMapper function processes chunks in parallel on different nodes (filtering, sorting, parsing).\nOutput: Intermediate Key-Value pairs.\n\nReduce Phase:\nIntermediate Key-Value pairs shuffled, sorted, and grouped by 'Keys'.\nReducer function aggregates, sums, or summarizes values.\nOutput: Final condensed result written to HDFS.", "page_number": None, "has_diagram": False},
            {"id": 306, "qno": "Q6", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Explain the MapReduce processing steps in detail, including Map Tasks, Combiners, Partitioning, and Reduce Tasks. [IMP]", "type": "standard", "answer": "Complete MapReduce Job Execution Steps:\n\n1. Input Splits & Record Reader:\nMassive input file logically divided into Input Splits (usually 128MB block size).\nRecord Reader converts raw data into basic Key-Value pairs for Mapper.\n\n2. Map Task:\nUser-defined Map function executes core business logic (filtering, tokenizing).\nGenerates millions of intermediate Key-Value pairs.\n\n3. Combiner (Optional but Recommended):\nMini-Reducer running on same node as Mapper immediately after Map phase.\nPerforms local aggregation before network transmission.\n\n4. Partitioner:\nDecides which Reducer receives which Key-Value pairs.\nUses hash function ensuring all same-Key values go to same Reduce Task.\n\n5. Shuffle and Sort:\nFramework transfers partitioned data across network to assigned Reducers.\nData automatically grouped and sorted by Key.\n\n6. Reduce Task:\nUser-defined Reduce function receives Key and all associated values.\nAggregates them and writes final result to HDFS.", "page_number": None, "has_diagram": False},
            {"id": 307, "qno": "Q7", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Describe the functioning of YARN (Hadoop 2 Execution Model) with its architecture diagram. [IMP]", "type": "standard", "image_path": "UNIT2/UT2_Q5_4m.png", "answer": "YARN (Yet Another Resource Negotiator) introduced in Hadoop 2.0 separates resource management from data processing.\n\nYARN Architecture Components:\n\nResourceManager (RM):\nMaster daemon managing all cluster resources (CPU, RAM).\n\nNodeManager (NM):\nRuns on each worker node, monitors resource usage.\n\nContainer:\nLogical bundle of resources (CPU + RAM) where tasks run.\n\nApplicationMaster (AM):\nEach application has its own AM.\nNegotiates resources with ResourceManager.\nManages task execution throughout application lifecycle.\n\nFunctioning:\nApplicationMaster requests resources from ResourceManager.\nResourceManager allocates containers on NodeManagers.\nNodeManagers monitor container execution and report back.\nApplicationMaster can request more/release containers dynamically.", "page_number": None, "has_diagram": True, "diagram_type": "yarn_arch"},
        ],
    },
    {
        "id": "bda-unit-3",
        "number": 3,
        "title": "NoSQL Databases and Big Data Management",
        "marks": "12 marks",
        "priority": "Important",
        "learning_hours": "4-5 hrs",
        "syllabus_topics": ["CAP Theorem", "Schema-less Data Models", "Key-Value vs Document Stores", "NoSQL Architecture Patterns"],
        "total_2m_questions": 0,
        "total_4m_questions": 4,
        "total_diagram_questions": 1,
        "questions": [
            {"id": 401, "qno": "Q1", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "State and explain the CAP theorem in detail with a suitable diagram. [IMP]", "type": "differentiate", "image_path": "UNIT3/UT3_Q1_4m.png", "answer": "CAP Theorem (Brewer's Theorem) states that distributed data stores can guarantee at most 2 of 3 properties:\n\n1. Consistency (C):\nEvery read receives most recent write or error.\nAll nodes see exactly same data at same time.\n\n2. Availability (A):\nEvery request receives valid response without guarantee of latest write.\nSystem remains operational even if some nodes fail.\n\n3. Partition Tolerance (P):\nSystem continues operating despite arbitrary message drops/delays between nodes.\n\nTRADE-OFFS:\nSince Partitions are inevitable in large systems, choose between C and A:\n\nCP (Consistency + Partition): Returns error during partition rather than stale data. Examples: HBase, MongoDB.\n\nAP (Availability + Partition): Always responds even if stale data during partition. Examples: Cassandra, CouchDB.\n\nCA (Consistency + Availability): Only possible in single-node systems like traditional RDBMS (MySQL, Oracle).", "page_number": None, "has_diagram": True, "diagram_type": "cap_theorem"},
            {"id": 402, "qno": "Q2", "marks": "4/6M", "importance": "⭐⭐", "question": "Explain the concept of schema-less data models in NoSQL.", "type": "standard", "answer": "Schema-less (Flexible Schema) Data Model:\n\nTraditional RDBMS Limitation: Data strictly bound by predefined schema. Must define columns, data types before inserting data. Adding new fields requires altering entire table structure.\n\nNoSQL Schema-less Advantages:\n\nDynamic Structure: No predefined structure required. Add data without defining schema.\n\nDocument Autonomy: Every record can have entirely different internal structure. Document A might have 3 fields (Name, Age, Email), Document B might have 5 different fields (Name, Address, Phone, Hobbies, Gender) in same collection.\n\nAgile Development: Continuously modify, add, or remove fields without system downtime or complex migrations.\n\nUnstructured Data Handling: Perfect for Big Data applications ingesting variable unstructured data (JSON feeds from IoT sensors, social media APIs, web logs).", "page_number": None, "has_diagram": False},
            {"id": 403, "qno": "Q3", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Describe the Key-Value Store and Document Store architecture patterns of NoSQL. [IMP]", "type": "differentiate", "answer": "1. KEY-VALUE STORE ARCHITECTURE:\n\nDescription: Simplest NoSQL database, acts as massive distributed hash table.\n\nArchitecture: Every data stored as paired entity - unique Key (identifier) and Value (data payload).\n\nCharacteristics: Database treats Value as opaque blob, doesn't know/care internal structure (string, object, image, JSON). Data queryable only by exact Key.\n\nAdvantages: Blazing fast read/write speeds, highly scalable. Excellent for caching, shopping carts, session management.\n\nExamples: Redis, Amazon DynamoDB, Riak.\n\n---\n\n2. DOCUMENT STORE ARCHITECTURE:\n\nDescription: Evolution of Key-Value store where Value is structured semi-structured document (JSON, BSON, XML).\n\nArchitecture: Data logically grouped into Collections (like tables) and stored as Documents (like rows).\n\nCharacteristics: Database understands internal document structure, allows querying based on contents (Find all docs where Age > 25 and City = 'Mumbai').\n\nAdvantages: Flexible schema, perfect for content management systems, e-commerce catalogs, user profile analytics.\n\nExamples: MongoDB, Couchbase, CouchDB.", "page_number": None, "has_diagram": False},
            {"id": 404, "qno": "Q4", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Explain various NoSQL data architecture patterns (Key-Value, Document, Tabular, Object, Graph store). [IMP]", "type": "standard", "answer": "NoSQL databases classified into 5 main architecture patterns:\n\n1. Key-Value Store:\nStores data as hash table with unique key mapped to value blob.\nOptimized for fast simple lookups by key.\nExamples: Redis, DynamoDB.\n\n2. Document Store:\nStores flexible semi-structured documents (JSON/BSON).\nAllows complex querying against nested document data.\nExamples: MongoDB, CouchDB.\n\n3. Column-Family (Tabular) Store:\nInstead of row-sequential storage like RDBMS, stores in column families.\nOptimized for massive write operations and reading specific columns without reading entire row.\nExamples: Apache Cassandra, HBase.\n\n4. Graph Store:\nStores data in nodes (entities) and edges (relationships).\nExplicitly designed to map, traverse, and query complex interconnected relationships faster than traditional JOINs.\nExamples: Neo4j, Amazon Neptune (used for social networks, recommendations).\n\n5. Object Store:\nStores data purely as objects exactly as created/used in OOP languages (Java, C#, C++).", "page_number": None, "has_diagram": False},
        ],
    },
    {
        "id": "bda-unit-4",
        "number": 4,
        "title": "Hive and Pig",
        "marks": "14 marks",
        "priority": "Important",
        "learning_hours": "4-5 hrs",
        "syllabus_topics": ["Apache Hive", "HiveQL", "Hive Architecture", "Apache Pig", "Pig Latin", "Hive vs Pig Comparison"],
        "total_2m_questions": 4,
        "total_4m_questions": 4,
        "total_diagram_questions": 1,
        "questions": [
            {"id": 501, "qno": "Q1", "marks": "2M", "importance": "⭐", "question": "Define Apache Hive.", "type": "standard", "answer": "Apache Hive is a data warehouse infrastructure built on top of Hadoop that provides a SQL-like interface (HiveQL) for querying and analyzing large datasets stored in HDFS. It converts HiveQL queries into MapReduce jobs for execution.", "page_number": None, "has_diagram": False},
            {"id": 502, "qno": "Q2", "marks": "2M", "importance": "⭐", "question": "What is HiveQL?", "type": "standard", "answer": "HiveQL (Hive Query Language) is a SQL-like language used in Apache Hive to perform queries, data analysis, and data manipulation on large datasets stored in Hadoop.", "page_number": None, "has_diagram": False},
            {"id": 503, "qno": "Q3", "marks": "2M", "importance": "⭐", "question": "Define Apache Pig.", "type": "standard", "answer": "Apache Pig is a high-level platform for creating programs that run on Hadoop. It uses a scripting language called Pig Latin to process and analyze large datasets.", "page_number": None, "has_diagram": False},
            {"id": 504, "qno": "Q4", "marks": "2M", "importance": "⭐", "question": "What is Pig Latin?", "type": "standard", "answer": "Pig Latin is a high-level scripting language used in Apache Pig to write data transformation and analysis programs.", "page_number": None, "has_diagram": False},
            {"id": 505, "qno": "Q5", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Explain Hive Architecture with neat diagram. [IMP]", "type": "standard", "image_path": "UNIT4/UT4_Q1_4m.png", "answer": "Hive Architecture Components:\n\nUser Interface (UI):\nUsers interact via CLI, Web UI, or JDBC/ODBC interfaces.\n\nDriver:\nReceives queries, manages lifecycle, creates execution plans, coordinates execution.\n\nCompiler:\nParses HiveQL, performs semantic analysis, converts to execution plan.\n\nMetastore:\nStores metadata (table schemas, column types, HDFS data location).\n\nExecution Engine:\nExecutes query plan by submitting jobs to Hadoop (MapReduce).\n\nHadoop (HDFS + MapReduce):\nProvides storage and processing infrastructure.", "page_number": None, "has_diagram": True, "diagram_type": "hive_arch"},
            {"id": 506, "qno": "Q6", "marks": "4/6M", "importance": "⭐⭐", "question": "Explain features of Hive.", "type": "standard", "answer": "Hive Features:\n\n• SQL-like language (HiveQL) for easy querying\n• Supports large-scale data processing\n• Schema-on-read approach\n• Integrates with Hadoop ecosystem\n• Supports partitioning and bucketing\n• Translates queries to MapReduce automatically\n• Suitable for batch processing\n• Provides data warehouse capabilities", "page_number": None, "has_diagram": False},
            {"id": 507, "qno": "Q7", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Differentiate between Hive, Pig, and SQL. [IMP]", "type": "differentiate", "answer": "HIVE vs PIG COMPARISON:\n\nLanguage | Hive | Pig\nUses HiveQL (SQL-like language) | Uses Pig Latin (scripting language)\nSuitable for structured data analysis | Suitable for data flow and transformation\nEasier for SQL users | Easier for programmers\nQuery-based approach | Script-based approach\nDeclarative style | Procedural style\nUsed by: Data Analysts | Used by: Developers", "page_number": None, "has_diagram": False},
            {"id": 508, "qno": "Q8", "marks": "4/6M", "importance": "⭐", "question": "Explain Pig Architecture.", "type": "standard", "image_path": "UNIT4/UT4_Q4_4m.png", "answer": "Pig Architecture Components:\n\nPig Latin Script:\nUser writes scripts for data processing.\n\nParser:\nChecks syntax and type.\n\nLogical Plan:\nCreates logical execution steps.\n\nOptimizer:\nOptimizes the plan for better performance.\n\nCompiler:\nConverts plan into MapReduce jobs.\n\nExecution Engine:\nRuns jobs on Hadoop cluster.", "page_number": None, "has_diagram": False},
        ],
    },
    {
        "id": "bda-unit-5",
        "number": 5,
        "title": "Spark and Real-Time Analytics",
        "marks": "16 marks",
        "priority": "CRITICAL - HIGHEST MARKS",
        "learning_hours": "5-6 hrs",
        "syllabus_topics": ["Apache Spark", "RDD", "Spark Streaming", "DataFrame", "Spark Architecture", "Real-Time Processing"],
        "total_2m_questions": 4,
        "total_4m_questions": 4,
        "total_diagram_questions": 2,
        "questions": [
            {"id": 601, "qno": "Q1", "marks": "2M", "importance": "⭐", "question": "Define Apache Spark.", "type": "standard", "answer": "Apache Spark is an open-source distributed computing system designed for fast data processing. It provides in-memory computation to process large datasets efficiently.", "page_number": None, "has_diagram": False},
            {"id": 602, "qno": "Q2", "marks": "2M", "importance": "⭐", "question": "What is RDD in Spark?", "type": "standard", "answer": "RDD (Resilient Distributed Dataset) is the fundamental data structure of Spark. It is an immutable, distributed collection of objects that can be processed in parallel.", "page_number": None, "has_diagram": False},
            {"id": 603, "qno": "Q3", "marks": "2M", "importance": "⭐", "question": "What is Spark Streaming?", "type": "standard", "answer": "Spark Streaming is a component of Apache Spark that enables real-time processing of live data streams.", "page_number": None, "has_diagram": False},
            {"id": 604, "qno": "Q4", "marks": "2M", "importance": "⭐", "question": "Define DataFrame in Spark.", "type": "standard", "answer": "A DataFrame is a distributed collection of data organized into named columns, similar to a table in a relational database.", "page_number": None, "has_diagram": False},
            {"id": 605, "qno": "Q5", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Explain Apache Spark Architecture with neat diagram. [IMP]", "type": "standard", "image_path": "UNIT5/UT5_Q1_4m.png", "answer": "Apache Spark Architecture (Master-Slave Model):\n\nDriver Program:\nActs as master, controls execution, maintains metadata, schedules tasks.\n\nCluster Manager:\nAllocates resources across applications (Standalone, YARN, Mesos).\n\nWorker Nodes:\nNodes performing actual data processing.\n\nExecutors:\nProcesses running on worker nodes executing tasks and storing data.\n\nTasks:\nSmallest unit of work sent to executors.\n\nFunctioning:\nDriver creates task graph and sends to executors.\nExecutors run tasks in parallel on data partitions.\nDriver coordinates and manages overall job execution.", "page_number": None, "has_diagram": True, "diagram_type": "spark_arch"},
            {"id": 606, "qno": "Q6", "marks": "4/6M", "importance": "⭐⭐", "question": "Explain features of Apache Spark.", "type": "standard", "answer": "Apache Spark Features:\n\n• In-memory processing for faster computation (100x faster than Hadoop)\n• Supports batch and real-time processing\n• Fault-tolerant system using lineage\n• Easy integration with Hadoop ecosystem\n• Supports multiple languages (Java, Scala, Python)\n• Lazy evaluation of transformations\n• Rich set of high-level APIs\n• GraphX for graph processing\n• MLlib for machine learning", "page_number": None, "has_diagram": False},
            {"id": 607, "qno": "Q7", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Explain RDD in detail. [IMP]", "type": "standard", "image_path": "UNIT5/UT5_Q5_4m.png", "answer": "RDD (Resilient Distributed Dataset) - Core Abstraction of Spark:\n\nCharacteristics:\n\nImmutable: Once created, cannot be changed.\n\nDistributed: Data divided across multiple nodes.\n\nFault-tolerant: Recovers data using lineage (DAG - Directed Acyclic Graph).\n\nLazy Evaluation: Operations executed only when action performed.\n\nOperations on RDD:\n\nTransformations: map(), filter(), reduceByKey(), join(), groupByKey() - return new RDD\n\nActions: collect(), count(), saveAsTextFile(), first(), take() - return results to driver\n\nLineage: Spark remembers sequence of transformations to recover lost partitions.", "page_number": None, "has_diagram": False},
            {"id": 608, "qno": "Q8", "marks": "4/6M", "importance": "⭐⭐⭐", "question": "Explain Spark Streaming architecture. [IMP]", "type": "standard", "image_path": "UNIT5/UT5_Q6_4m.png", "answer": "Spark Streaming Architecture:\n\nData Sources: Kafka, Flume, HDFS, sockets, TCP connections.\n\nStreaming Engine:\nDivides incoming data into micro-batches.\nEach micro-batch processed as RDD.\n\nProcessing:\nApplies transformations using Spark.\nProcesses multiple streams simultaneously.\n\nOutput:\nStores results in databases or dashboards.\nCan trigger actions on processed data.\n\nFunctioning:\n1. Data arrives from sources in continuous stream\n2. Streaming engine collects data for batch interval (e.g., 2 seconds)\n3. Creates micro-batch RDD\n4. Applies transformations\n5. Stores/outputs results\n6. Repeats process", "page_number": None, "has_diagram": True, "diagram_type": "spark_streaming"},
        ],
    },
]

BDA_IMPORTANT_QUESTION_BANK = [
    {"unit": "Unit 1", "priority": "Foundation", "color": "green", "items": [
        {"stars": "⭐", "text": "Q1 Classify Big Data Types", "question_id": 201},
        {"stars": "⭐⭐⭐", "text": "Q10 Differentiate Structured vs Semi-structured vs Unstructured", "question_id": 210},
    ]},
    {"unit": "Unit 2", "priority": "🔴 CRITICAL - MOST IMPORTANT (16 marks)", "color": "red", "items": [
        {"stars": "⭐⭐⭐", "text": "Q1 Big Data Characteristics (4V)", "question_id": 301},
        {"stars": "⭐⭐⭐", "text": "Q2 Big Data Processing Architecture", "question_id": 302},
        {"stars": "⭐⭐⭐", "text": "Q3 Hadoop Ecosystem", "question_id": 303},
        {"stars": "⭐⭐⭐", "text": "Q4 HDFS Architecture & Functioning", "question_id": 304},
        {"stars": "⭐⭐⭐", "text": "Q5 MapReduce Programming Model", "question_id": 305},
        {"stars": "⭐⭐⭐", "text": "Q6 MapReduce Processing Steps (Combiner, Partitioner)", "question_id": 306},
        {"stars": "⭐⭐⭐", "text": "Q7 YARN Architecture", "question_id": 307},
    ]},
    {"unit": "Unit 3", "priority": "Important (12 marks)", "color": "orange", "items": [
        {"stars": "⭐⭐⭐", "text": "Q1 CAP Theorem with Diagram", "question_id": 401},
        {"stars": "⭐⭐", "text": "Q2 Schema-less Data Models", "question_id": 402},
        {"stars": "⭐⭐⭐", "text": "Q3 Key-Value vs Document Store", "question_id": 403},
        {"stars": "⭐⭐⭐", "text": "Q4 NoSQL Architecture Patterns", "question_id": 404},
    ]},
    {"unit": "Unit 4", "priority": "Important (14 marks)", "color": "orange", "items": [
        {"stars": "⭐", "text": "Q1-Q4 Basic 2M Questions", "question_id": 501},
        {"stars": "⭐⭐⭐", "text": "Q5 Hive Architecture with Diagram", "question_id": 505},
        {"stars": "⭐⭐⭐", "text": "Q7 Hive vs Pig Differentiation", "question_id": 507},
    ]},
    {"unit": "Unit 5", "priority": "🔴 CRITICAL - HIGHEST MARKS (16 marks)", "color": "red", "items": [
        {"stars": "⭐", "text": "Q1-Q4 Basic 2M Questions", "question_id": 601},
        {"stars": "⭐⭐⭐", "text": "Q5 Spark Architecture with Diagram", "question_id": 605},
        {"stars": "⭐⭐⭐", "text": "Q7 RDD in Detail", "question_id": 607},
        {"stars": "⭐⭐⭐", "text": "Q8 Spark Streaming Architecture", "question_id": 608},
    ]},
]

BDA_MARKS = [
    {"unit": "Unit 1", "topic": "Big Data Basics", "marks": "12 marks", "priority": "Foundation"},
    {"unit": "Unit 2", "topic": "Hadoop & HDFS & MapReduce & YARN", "marks": "16 marks", "highlight": True, "priority": "🔴 HIGHEST"},
    {"unit": "Unit 3", "topic": "NoSQL Databases", "marks": "12 marks", "priority": "Important"},
    {"unit": "Unit 4", "topic": "Hive & Pig", "marks": "14 marks", "priority": "Important"},
    {"unit": "Unit 5", "topic": "Spark & Real-Time Analytics", "marks": "16 marks", "highlight": True, "priority": "🔴 HIGHEST"},
]

MAN_UNITS = [
    {
        "id": "man-unit-1",
        "number": 1,
        "title": "Management MCQ Bank",
        "marks": "MCQ focus",
        "questions": [
            {"id": 301, "star": "", "question": "In a pull-based Kanban system", "definition": "Work is started only when there is demand from the next process", "points": ["Work is started only when there is demand from the next process"], "examples": [], "type": "mcq"},
            {"id": 302, "star": "", "question": 'The "Zero Defect" concept was given by', "definition": "Philip Crosby", "points": ["Philip Crosby"], "examples": [], "type": "mcq"},
            {"id": 303, "star": "", "question": "In the 7 Ps of marketing, Physical Evidence refers to", "definition": "Tangible elements that represent service quality", "points": ["Tangible elements that represent service quality"], "examples": [], "type": "mcq"},
            {"id": 304, "star": "", "question": "Which company popularized Six Sigma after Motorola", "definition": "General Electric (GE)", "points": ["General Electric (GE)"], "examples": [], "type": "mcq"},
            {"id": 305, "star": "", "question": "TPM focuses on improving", "definition": "Overall Equipment Effectiveness (OEE)", "points": ["Overall Equipment Effectiveness (OEE)"], "examples": [], "type": "mcq"},
            {"id": 306, "star": "", "question": "Durable long-lasting mobile phone refers to", "definition": "Real need", "points": ["Real need"], "examples": [], "type": "mcq"},
            {"id": 307, "star": "", "question": "Shitsuke in 5S means", "definition": "Discipline and sustaining habit", "points": ["Discipline and sustaining habit"], "examples": [], "type": "mcq"},
            {"id": 308, "star": "", "question": "Practice related to Kaizen", "definition": "Just-in-Time (JIT)", "points": ["Just-in-Time (JIT)"], "examples": [], "type": "mcq"},
            {"id": 309, "star": "", "question": "Six Sigma goal", "definition": "3.4 defects per million opportunities", "points": ["3.4 defects per million opportunities"], "examples": [], "type": "mcq"},
            {"id": 310, "star": "", "question": "DMAIC stands for", "definition": "Define Measure Analyze Improve Control", "points": ["Define Measure Analyze Improve Control"], "examples": [], "type": "mcq"},
            {"id": 311, "star": "", "question": "Traditional marketing provides", "definition": "One-way communication", "points": ["One-way communication"], "examples": [], "type": "mcq"},
            {"id": 312, "star": "", "question": "Fitness for use given by", "definition": "Juran", "points": ["Juran"], "examples": [], "type": "mcq"},
            {"id": 313, "star": "", "question": "Not part of 7Ps", "definition": "Partnership", "points": ["Partnership"], "examples": [], "type": "mcq"},
            {"id": 314, "star": "", "question": "Seiri means", "definition": "Sort remove unnecessary items", "points": ["Sort remove unnecessary items"], "examples": [], "type": "mcq"},
            {"id": 315, "star": "", "question": "OEE formula", "definition": "Availability x Performance x Quality", "points": ["Availability x Performance x Quality"], "examples": [], "type": "mcq"},
            {"id": 316, "star": "", "question": "Six Sigma developed by", "definition": "Motorola", "points": ["Motorola"], "examples": [], "type": "mcq"},
            {"id": 317, "star": "", "question": "Quality Circle includes", "definition": "5-10 members from same department", "points": ["5-10 members from same department"], "examples": [], "type": "mcq"},
            {"id": 318, "star": "", "question": "Sigma represents", "definition": "Standard deviation", "points": ["Standard deviation"], "examples": [], "type": "mcq"},
            {"id": 319, "star": "", "question": "Tool used in Quality Circles", "definition": "Fishbone diagram", "points": ["Fishbone diagram"], "examples": [], "type": "mcq"},
            {"id": 320, "star": "", "question": "Core principle of TQM", "definition": "Doing things right first time", "points": ["Doing things right first time"], "examples": [], "type": "mcq"},
            {"id": 321, "star": "", "question": "Purpose of Kanban", "definition": "Control production and material flow visually", "points": ["Control production and material flow visually"], "examples": [], "type": "mcq"},
            {"id": 322, "star": "", "question": "TPM originated from", "definition": "Nippon Denso", "points": ["Nippon Denso"], "examples": [], "type": "mcq"},
            {"id": 323, "star": "", "question": "Black Belts are", "definition": "Experts who mentor others", "points": ["Experts who mentor others"], "examples": [], "type": "mcq"},
            {"id": 324, "star": "", "question": "Ability to pay + desire", "definition": "Demand", "points": ["Demand"], "examples": [], "type": "mcq"},
            {"id": 325, "star": "", "question": "Six Sigma accuracy", "definition": "99.99966%", "points": ["99.99966%"], "examples": [], "type": "mcq"},
            {"id": 326, "star": "", "question": "Not TPM pillar", "definition": "Product Design", "points": ["Product Design"], "examples": [], "type": "mcq"},
            {"id": 327, "star": "", "question": "Red tag used in", "definition": "Seiri", "points": ["Seiri"], "examples": [], "type": "mcq"},
            {"id": 328, "star": "", "question": "Place in marketing", "definition": "Distribution channels", "points": ["Distribution channels"], "examples": [], "type": "mcq"},
            {"id": 329, "star": "", "question": "Two-card Kanban", "definition": "Transport and Production Kanban", "points": ["Transport and Production Kanban"], "examples": [], "type": "mcq"},
            {"id": 330, "star": "", "question": "Relationship", "definition": "Need -> Want -> Demand", "points": ["Need -> Want -> Demand"], "examples": [], "type": "mcq"},
            {"id": 331, "star": "", "question": "Lean Manufacturing objective", "definition": "Eliminate waste and improve value to customer", "points": ["Eliminate waste and improve value to customer"], "examples": [], "type": "mcq"},
            {"id": 332, "star": "", "question": "Founder of Quality Circle", "definition": "Kaoru Ishikawa", "points": ["Kaoru Ishikawa"], "examples": [], "type": "mcq"},
            {"id": 333, "star": "", "question": "TPM emphasizes", "definition": "Preventive and Autonomous maintenance", "points": ["Preventive and Autonomous maintenance"], "examples": [], "type": "mcq"},
            {"id": 334, "star": "", "question": "Kanban card represents", "definition": "Production order or part requirement", "points": ["Production order or part requirement"], "examples": [], "type": "mcq"},
            {"id": 335, "star": "", "question": "Autonomous Maintenance means", "definition": "Operators maintain their own machines", "points": ["Operators maintain their own machines"], "examples": [], "type": "mcq"},
            {"id": 336, "star": "", "question": "Not traditional marketing", "definition": "Search engine optimization (SEO)", "points": ["Search engine optimization (SEO)"], "examples": [], "type": "mcq"},
            {"id": 337, "star": "", "question": "7Ps expanded from", "definition": "4 Ps", "points": ["4 Ps"], "examples": [], "type": "mcq"},
            {"id": 338, "star": "", "question": "Quality Circles approach", "definition": "Bottom-up", "points": ["Bottom-up"], "examples": [], "type": "mcq"},
            {"id": 339, "star": "", "question": "TPM goal", "definition": "Zero accidents zero defects zero breakdowns", "points": ["Zero accidents zero defects zero breakdowns"], "examples": [], "type": "mcq"},
            {"id": 340, "star": "", "question": "Kaizen means", "definition": "Continuous improvement", "points": ["Continuous improvement"], "examples": [], "type": "mcq"},
            {"id": 341, "star": "", "question": "Master Black Belt", "definition": "Leads Six Sigma program company-wide", "points": ["Leads Six Sigma program company-wide"], "examples": [], "type": "mcq"},
            {"id": 342, "star": "", "question": "PPC means", "definition": "Pay only when users click advertisement", "points": ["Pay only when users click advertisement"], "examples": [], "type": "mcq"},
            {"id": 343, "star": "", "question": "Seiton means", "definition": "Set things in order for easy access", "points": ["Set things in order for easy access"], "examples": [], "type": "mcq"},
            {"id": 344, "star": "", "question": "Quality Circles in India", "definition": "BHEL", "points": ["BHEL"], "examples": [], "type": "mcq"},
            {"id": 345, "star": "", "question": "Not element of TQM", "definition": "Rigid hierarchy", "points": ["Rigid hierarchy"], "examples": [], "type": "mcq"},
            {"id": 346, "star": "", "question": "Goal of Kanban", "definition": "Produce only what is needed when needed", "points": ["Produce only what is needed when needed"], "examples": [], "type": "mcq"},
            {"id": 347, "star": "", "question": "TPM pillars", "definition": "8", "points": ["8"], "examples": [], "type": "mcq"},
            {"id": 348, "star": "", "question": "First step marketing", "definition": "Identifying customer needs", "points": ["Identifying customer needs"], "examples": [], "type": "mcq"},
            {"id": 349, "star": "", "question": "SEO helps to", "definition": "Increase website visibility", "points": ["Increase website visibility"], "examples": [], "type": "mcq"},
            {"id": 350, "star": "", "question": "Kanban language", "definition": "Japanese", "points": ["Japanese"], "examples": [], "type": "mcq"},
            {"id": 351, "star": "", "question": "Analytics easier in", "definition": "Digital marketing", "points": ["Digital marketing"], "examples": [], "type": "mcq"},
            {"id": 352, "star": "", "question": "Expecting service but not saying", "definition": "Unstated need", "points": ["Unstated need"], "examples": [], "type": "mcq"},
            {"id": 353, "star": "", "question": "PDCA cycle", "definition": "Kaizen and TQM", "points": ["Kaizen and TQM"], "examples": [], "type": "mcq"},
            {"id": 354, "star": "", "question": "Seiketsu means", "definition": "Standardizing procedures", "points": ["Standardizing procedures"], "examples": [], "type": "mcq"},
            {"id": 355, "star": "", "question": "Benefit of Quality Circles", "definition": "Improved quality and productivity", "points": ["Improved quality and productivity"], "examples": [], "type": "mcq"},
            {"id": 356, "star": "", "question": "People in marketing", "definition": "Employees sales staff and service providers", "points": ["Employees sales staff and service providers"], "examples": [], "type": "mcq"},
            {"id": 357, "star": "", "question": "Kanban means", "definition": "Visual signal or card", "points": ["Visual signal or card"], "examples": [], "type": "mcq"},
            {"id": 358, "star": "", "question": "Kaizen philosophy", "definition": "Small improvements regularly", "points": ["Small improvements regularly"], "examples": [], "type": "mcq"},
            {"id": 359, "star": "", "question": "Not advantage of Kanban", "definition": "Increases lead time", "points": ["Increases lead time"], "examples": [], "type": "mcq"},
            {"id": 360, "star": "", "question": "Traditional marketing", "definition": "Offline promotion using print radio TV", "points": ["Offline promotion using print radio TV"], "examples": [], "type": "mcq"},
        ],
    },
]

MAN_IMPORTANT_QUESTION_BANK = [
    {"unit": "Top 30 Important", "priority": "Exam Focus", "color": "red", "items": [
        {"stars": "TOP", "text": "Zero Defect - Philip Crosby", "question_id": 302},
        {"stars": "TOP", "text": "Six Sigma GE", "question_id": 304},
        {"stars": "TOP", "text": "OEE", "question_id": 305},
        {"stars": "TOP", "text": "JIT", "question_id": 308},
        {"stars": "TOP", "text": "Six Sigma 3.4 defects", "question_id": 309},
        {"stars": "TOP", "text": "DMAIC", "question_id": 310},
        {"stars": "TOP", "text": "Juran", "question_id": 312},
        {"stars": "TOP", "text": "OEE formula", "question_id": 315},
        {"stars": "TOP", "text": "Motorola", "question_id": 316},
        {"stars": "TOP", "text": "Quality Circle", "question_id": 317},
        {"stars": "TOP", "text": "Standard deviation", "question_id": 318},
        {"stars": "TOP", "text": "Fishbone diagram", "question_id": 319},
        {"stars": "TOP", "text": "TQM principle", "question_id": 320},
        {"stars": "TOP", "text": "Kanban purpose", "question_id": 321},
        {"stars": "TOP", "text": "TPM origin", "question_id": 322},
        {"stars": "TOP", "text": "Black Belt", "question_id": 323},
        {"stars": "TOP", "text": "Six Sigma accuracy", "question_id": 325},
        {"stars": "TOP", "text": "Kanban types", "question_id": 329},
        {"stars": "TOP", "text": "Lean Manufacturing", "question_id": 331},
        {"stars": "TOP", "text": "Ishikawa", "question_id": 332},
        {"stars": "TOP", "text": "TPM maintenance", "question_id": 333},
        {"stars": "TOP", "text": "Bottom-up", "question_id": 338},
        {"stars": "TOP", "text": "TPM goal", "question_id": 339},
        {"stars": "TOP", "text": "Kaizen", "question_id": 340},
        {"stars": "TOP", "text": "Seiton", "question_id": 343},
        {"stars": "TOP", "text": "TPM pillars", "question_id": 347},
        {"stars": "TOP", "text": "PDCA", "question_id": 353},
        {"stars": "TOP", "text": "Seiketsu", "question_id": 354},
        {"stars": "TOP", "text": "Kanban meaning", "question_id": 357},
        {"stars": "TOP", "text": "Kaizen philosophy", "question_id": 358},
    ]},
]

SUBJECTS = {
    "aam": {
        "key": "aam",
        "name": "AAM",
        "code": "AAM",
        "hero": "Unit-wise study pages, important questions, diagrams, bookmarks, and answer checking.",
        "units": ML_UNITS,
        "important_bank": ML_IMPORTANT_QUESTION_BANK,
        "must_study": ML_MUST_STUDY,
        "marks": [],
    },
    "pip": {
        "key": "pip",
        "name": "PIP",
        "code": "PIP",
        "hero": "Image processing syllabus with marks dashboard, priority questions, diagrams, and study-mode checking.",
        "units": PIP_UNITS,
        "important_bank": PIP_IMPORTANT_QUESTION_BANK,
        "must_study": [],
        "marks": PIP_MARKS,
    },
    "bda": {
        "key": "bda",
        "name": "BDA (Big Data Analytics)",
        "code": "BDA",
        "hero": "Big data analytics syllabus with unit-wise marks, Hadoop-heavy priority topics, architecture diagrams, and exam-ready revision pages.",
        "units": BDA_UNITS,
        "important_bank": BDA_IMPORTANT_QUESTION_BANK,
        "must_study": [],
        "marks": BDA_MARKS,
    },
    "man": {
        "key": "man",
        "name": "Management",
        "code": "MAN",
        "hero": "MCQ-only revision page with direct question-answer format and top 30 exam-focus picks.",
        "units": MAN_UNITS,
        "important_bank": MAN_IMPORTANT_QUESTION_BANK,
        "must_study": [],
        "marks": [],
        "mcq_only": True,
    },
}


enrich_ml_questions()


def expand_question_details() -> None:
    subject_suffix = {
        "aam": " It is important for understanding exam-oriented concepts along with practical analytical applications.",
        "pip": " It is important for understanding how images are processed, improved, and analyzed in practical systems.",
        "bda": " It is important for understanding distributed storage, large-scale processing, and modern analytics systems.",
        "man": "",
    }
    point_suffix = {
        "aam": ", which strengthens conceptual understanding for model building and data-driven problem solving.",
        "pip": ", which helps explain the role of the concept in practical image processing workflows.",
        "bda": ", which is useful for explaining how scalable data systems work in real environments.",
        "man": "",
    }
    for subject_key, subject in SUBJECTS.items():
        for unit in subject["units"]:
            for question in unit["questions"]:
                if subject_key == "man" or subject_key == "bda":
                    continue
                if "definition" not in question:
                    continue
                if not question["definition"].endswith(subject_suffix[subject_key].strip()):
                    question["definition"] = question["definition"].rstrip(".") + "." + subject_suffix[subject_key]
                if question["type"] != "difference":
                    question["points"] = [
                        point.rstrip(".") + point_suffix[subject_key]
                        for point in question.get("points", [])
                    ]


expand_question_details()


ALL_QUESTIONS = [question for subject in SUBJECTS.values() for unit in subject["units"] for question in unit["questions"]]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", value.lower())).strip()


def tokenize(value: str) -> set[str]:
    return {token for token in normalize_text(value).split() if len(token) > 2}


def list_pdf_files() -> list[dict]:
    if not PDF_DIR.exists():
        return []
    return [{"name": path.name, "size_kb": round(path.stat().st_size / 1024, 1)} for path in sorted(PDF_DIR.glob("*.pdf"))]


def get_subject(subject_key: str) -> dict | None:
    return SUBJECTS.get(subject_key)


def exam_date_label(raw_date: str) -> str:
    parsed = datetime.strptime(raw_date, "%d-%m-%Y")
    return f"{parsed.day} {parsed.strftime('%B')}"


def build_exam_timetable_view() -> dict:
    today = date.today()
    schedule = []
    for item in EXAM_TIMETABLE["schedule"]:
        exam_date = datetime.strptime(item["date"], "%d-%m-%Y").date()
        days_left = (exam_date - today).days
        exam_start = datetime.combine(exam_date, time(hour=9, minute=30))
        schedule.append({**item, "days_left": days_left, "exam_start_iso": exam_start.isoformat()})
    final_order = []
    for item in schedule:
        short_subject = item["subject"].split("(")[-1].replace(")", "")
        final_order.append(f"{short_subject} -> {exam_date_label(item['date'])} ({item['days_left']} days left)")
    return {
        **EXAM_TIMETABLE,
        "schedule": schedule,
        "final_order": final_order,
    }


def build_question_unit_map(subject: dict) -> dict[int, int]:
    mapping = {}
    for unit in subject["units"]:
        for question in unit["questions"]:
            mapping[question["id"]] = unit["number"]
    return mapping


def get_question(question_id: int) -> dict | None:
    for question in ALL_QUESTIONS:
        if question["id"] == question_id:
            return question
    return None


def build_answer_text(question: dict) -> str:
    if "answer" in question:
        return question["answer"]
    parts = [question.get("definition", "")]
    if question["type"] == "difference":
        for basis, pair in zip(question.get("difference_basis", []), question.get("differences", [])):
            parts.append(basis)
            parts.extend(pair)
    else:
        parts.extend(question.get("points", []))
    parts.extend(question.get("examples", []))
    return " ".join(p for p in parts if p)


def evaluate_answer(question: dict, answer: str) -> dict:
    reference = build_answer_text(question)
    answer_clean = normalize_text(answer)
    similarity = SequenceMatcher(None, answer_clean, normalize_text(reference)).ratio()
    definition_similarity = SequenceMatcher(None, answer_clean, normalize_text(question.get("definition", reference))).ratio()

    matched_points, missed_points, matched_differences, missed_differences = [], [], [], []
    for point in question.get("points", []):
        if len(tokenize(point) & tokenize(answer)) >= 2 or SequenceMatcher(None, answer_clean, normalize_text(point)).ratio() >= 0.45:
            matched_points.append(point)
        else:
            missed_points.append(point)

    for basis, pair in zip(question.get("difference_basis", []) or [], question.get("differences", []) or []):
        if not pair or len(pair) < 2:
            continue
        left, right = pair
        basis_hit = len(tokenize(basis) & tokenize(answer)) >= 1
        left_hit = len(tokenize(left) & tokenize(answer)) >= 1
        right_hit = len(tokenize(right) & tokenize(answer)) >= 1
        if basis_hit and left_hit and right_hit:
            matched_differences.append({"basis": basis, "values": pair})
        else:
            missed_differences.append({"basis": basis, "values": pair})

    examples = question.get("examples", [question.get("example", "")])
    example_hits = [example for example in examples if example and example.lower() in answer.lower()]
    example_hit = bool(example_hits)
    score = round(definition_similarity * 25)
    if question["type"] == "difference" or question["type"] == "differentiate":
        score += round((len(matched_differences) / max(1, len(question.get("differences", [])))) * 55)
    else:
        score += round((len(matched_points) / max(1, len(question.get("points", [])))) * 55)
    score += 20 if example_hit else round(similarity * 20)
    score = max(0, min(100, score))

    feedback = []
    if not answer.strip():
        feedback.append("Write an answer first to see score and missing parts.")
    else:
        if definition_similarity < 0.35:
            feedback.append("Definition needs to be closer to the stored answer.")
        if missed_points:
            feedback.append("Some key bullet points are missing.")
        if missed_differences:
            feedback.append("Some side-by-side difference rows are missing.")
        if not example_hit:
            feedback.append(f"Add examples such as: {', '.join(examples[:3])}.")
        if score >= 85:
            feedback.append("Very close to the stored answer.")

    return {
        "score": score,
        "similarity_percent": round(similarity * 100),
        "definition_match_percent": round(definition_similarity * 100),
        "matched_points": matched_points,
        "missed_points": missed_points,
        "matched_differences": matched_differences,
        "missed_differences": missed_differences,
        "example_expected": examples,
        "example_found": example_hit,
        "example_matches": example_hits,
        "feedback": feedback,
    }


@app.get("/")
def index():
    subject_cards = []
    for subject in SUBJECTS.values():
        question_count = sum(len(unit["questions"]) for unit in subject["units"])
        subject_cards.append(
            {
                "key": subject["key"],
                "name": subject["name"],
                "code": subject["code"],
                "units": len(subject["units"]),
                "questions": question_count,
                "hero": subject["hero"],
            }
        )
    return render_template("dashboard.html", subject_cards=subject_cards, pdf_files=list_pdf_files(), exam_timetable=build_exam_timetable_view())


@app.get("/tasks")
def tasks_page():
    return render_template(
        "tasks.html",
        exam_timetable=build_exam_timetable_view(),
        all_questions=ALL_QUESTIONS,
        all_questions_json=json.dumps(ALL_QUESTIONS),
        subjects_meta=[
            {"key": subject["key"], "name": subject["name"], "code": subject["code"]}
            for subject in SUBJECTS.values()
        ],
    )


@app.get("/subject/<subject_key>")
def subject_page(subject_key: str):
    subject = get_subject(subject_key)
    if not subject:
        return ("Subject not found", 404)
    
    # BDA uses custom template
    if subject_key == "bda":
        total_questions = sum(len(unit["questions"]) for unit in subject["units"])
        diagram_questions = sum(
            sum(1 for q in unit["questions"] if q.get("has_diagram", False))
            for unit in subject["units"]
        )
        return render_template(
            "bda_subject.html",
            subject=subject,
            units=subject["units"],
            important_bank=subject["important_bank"],
            marks=subject["marks"],
            exam_timetable=build_exam_timetable_view(),
            total_questions=total_questions,
            diagram_questions=diagram_questions,
        )
    
    return render_template(
        "subject.html",
        subject=subject,
        units=subject["units"],
        must_study=subject["must_study"],
        important_question_bank=subject["important_bank"],
        marks=subject["marks"],
        exam_timetable=build_exam_timetable_view(),
        question_unit_map=build_question_unit_map(subject),
        pdf_files=list_pdf_files(),
        all_questions=[question for unit in subject["units"] for question in unit["questions"]],
    )


@app.get("/subject/ml")
def legacy_ml_subject_page():
    return redirect(url_for("subject_page", subject_key="aam"), code=302)


@app.get("/subject/<subject_key>/unit/<int:unit_number>")
def unit_page(subject_key: str, unit_number: int):
    subject = get_subject(subject_key)
    if not subject:
        return ("Subject not found", 404)
    unit = next((item for item in subject["units"] if item["number"] == unit_number), None)
    if not unit:
        return ("Unit not found", 404)
    current_bank = next((item for item in subject["important_bank"] if item["unit"] == f"Unit {unit_number}"), None)
    
    # BDA uses custom template
    if subject_key == "bda":
        return render_template(
            "bda_unit.html",
            subject=subject,
            units=subject["units"],
            important_question_bank=subject["important_bank"],
            current_bank=current_bank,
            unit=unit,
            exam_timetable=build_exam_timetable_view(),
            question_unit_map=build_question_unit_map(subject),
            pdf_files=list_pdf_files(),
            questions_json=json.dumps([question for unit in subject["units"] for question in unit["questions"]]),
            all_questions=[question for unit in subject["units"] for question in unit["questions"]],
            saved_diagrams=load_saved_diagrams(),
        )
    
    return render_template(
        "unit.html",
        subject=subject,
        units=subject["units"],
        must_study=subject["must_study"],
        important_question_bank=subject["important_bank"],
        current_bank=current_bank,
        unit=unit,
        exam_timetable=build_exam_timetable_view(),
        question_unit_map=build_question_unit_map(subject),
        pdf_files=list_pdf_files(),
        questions_json=json.dumps([question for unit in subject["units"] for question in unit["questions"]]),
        all_questions=[question for unit in subject["units"] for question in unit["questions"]],
    )


@app.get("/subject/ml/unit/<int:unit_number>")
def legacy_ml_unit_page(unit_number: int):
    return redirect(url_for("unit_page", subject_key="aam", unit_number=unit_number), code=302)


@app.get("/unit/<int:unit_number>")
def legacy_unit_page(unit_number: int):
    return redirect(url_for("unit_page", subject_key="aam", unit_number=unit_number), code=302)


@app.post("/api/evaluate")
def api_evaluate():
    payload = request.get_json(silent=True) or {}
    question = get_question(int(payload.get("questionId", 0)))
    if not question:
        return jsonify({"error": "Question not found."}), 404
    return jsonify(evaluate_answer(question, payload.get("answer", "")))


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.post("/api/upload-image")
def api_upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    # Create directory if it doesn't exist
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save file with secure filename
    filename = secure_filename(file.filename)
    filepath = IMAGE_DIR / filename
    file.save(filepath)
    
    return jsonify({"success": True, "filename": filename, "url": url_for("serve_image", filename=filename)})


@app.get("/api/images")
def api_list_images():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    images = []
    if IMAGE_DIR.exists():
        for filepath in sorted(IMAGE_DIR.glob("*")):
            if filepath.is_file() and allowed_file(filepath.name):
                images.append({
                    "filename": filepath.name,
                    "url": url_for("serve_image", filename=filepath.name),
                    "size_kb": round(filepath.stat().st_size / 1024, 1)
                })
    return jsonify({"images": images})


@app.post("/api/save-diagram")
def api_save_diagram():
    payload = request.get_json(silent=True) or {}
    question_id = str(payload.get("questionId", "")).strip()
    image_url = str(payload.get("imageUrl", "")).strip()

    if not question_id:
        return jsonify({"error": "Question id is required"}), 400
    if not image_url.startswith("/images/"):
        return jsonify({"error": "Please select an uploaded image first"}), 400

    filename = secure_filename(image_url.rsplit("/", 1)[-1])
    if not filename or not allowed_file(filename) or not (IMAGE_DIR / filename).exists():
        return jsonify({"error": "Selected image was not found"}), 404

    saved_url = url_for("serve_image", filename=filename)
    save_diagram_mapping(question_id, saved_url)
    return jsonify({"success": True, "question_id": question_id, "url": saved_url})


@app.get("/images/<filename>")
def serve_image(filename: str):
    return send_from_directory(IMAGE_DIR, secure_filename(filename))


@app.get("/manifest.webmanifest")
def manifest():
    return send_from_directory(BASE_DIR / "static", "manifest.webmanifest", mimetype="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    response = send_from_directory(BASE_DIR / "static", "sw.js", mimetype="application/javascript")
    response.headers["Service-Worker-Allowed"] = "/"
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)
