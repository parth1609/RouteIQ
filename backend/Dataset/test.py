import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# --- 1. Download NLTK Data (run once if not already done) ---
# This ensures that necessary NLTK data (stopwords, wordnet) is available.
# It's crucial that the preprocessing steps are identical to those used during training.
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('corpora/omw-1.4') # Required for WordNetLemmatizer
except LookupError:
    nltk.download('omw-1.4')


# --- 2. Define Preprocessing Function (MUST be identical to training) ---
def preprocess_text(text):
    """
    Cleans and preprocesses text data. This function must be exactly the same
    as the one used when the models were trained and saved.
    - Removes non-alphabetic characters.
    - Converts text to lowercase.
    - Removes English stopwords.
    - Applies WordNet Lemmatization.
    """
    if not isinstance(text, str):
        return "" # Handle non-string inputs gracefully
    text = re.sub(r'[^a-zA-Z\s]', '', text) # Remove non-alphabetic characters
    text = text.lower() # Convert to lowercase
    words = text.split() # Tokenize
    words = [word for word in words if word not in stopwords.words('english')] # Remove stopwords
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words] # Lemmatize
    return ' '.join(words)


# --- 3. Define Paths to Saved Models and Transformers ---
tfidf_vectorizer_path = 'tfidf_vectorizer.pkl'
le_department_path = 'le_department.pkl'
le_priority_path = 'le_priority.pkl'
log_reg_dept_path = 'log_reg_dept_model.pkl'
log_reg_prio_path = 'log_reg_prio_model.pkl'

# --- 4. Load Models and Transformers ---
print("--- Loading Models and Transformers ---")
try:
    with open(tfidf_vectorizer_path, 'rb') as f:
        loaded_tfidf_vectorizer = pickle.load(f)
    print(f"Loaded TF-IDF Vectorizer from {tfidf_vectorizer_path}")

    with open(le_department_path, 'rb') as f:
        loaded_le_department = pickle.load(f)
    print(f"Loaded Department LabelEncoder from {le_department_path}")

    with open(le_priority_path, 'rb') as f:
        loaded_le_priority = pickle.load(f)
    print(f"Loaded Priority LabelEncoder from {le_priority_path}")

    with open(log_reg_dept_path, 'rb') as f:
        loaded_log_reg_dept = pickle.load(f)
    print(f"Loaded Department Logistic Regression Model from {log_reg_dept_path}")

    with open(log_reg_prio_path, 'rb') as f:
        loaded_log_reg_prio = pickle.load(f)
    print(f"Loaded Priority Logistic Regression Model from {log_reg_prio_path}")

    print("\nAll models and transformers loaded successfully!")

except FileNotFoundError as e:
    print(f"Error: One or more .pkl files not found. Please ensure they are in the same directory.")
    print(f"Missing file: {e.filename}")
    exit() # Exit if files are not found
except Exception as e:
    print(f"An unexpected error occurred during loading: {e}")
    exit()


# --- 5. Prediction Function using Loaded Models ---
def predict_ticket_category_loaded(description: str) -> tuple[str, str]:
    """
    Predicts the department and priority for a given IT ticket description
    using the loaded models and transformers.

    Args:
        description (str): The raw text description of the IT ticket.

    Returns:
        tuple[str, str]: A tuple containing the predicted department and predicted priority.
    """
    # Preprocess the new description using the SAME function as training
    clean_description = preprocess_text(description)

    # Transform using the LOADED TF-IDF vectorizer
    description_tfidf = loaded_tfidf_vectorizer.transform([clean_description])

    # Predict Department using the LOADED model
    predicted_dept_encoded = loaded_log_reg_dept.predict(description_tfidf)
    predicted_department = loaded_le_department.inverse_transform(predicted_dept_encoded)[0]

    # Predict Priority using the LOADED model
    predicted_prio_encoded = loaded_log_reg_prio.predict(description_tfidf)
    predicted_priority = loaded_le_priority.inverse_transform(predicted_prio_encoded)[0]

    return predicted_department, predicted_priority

