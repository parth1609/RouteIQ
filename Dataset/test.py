import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# --- 1. Download NLTK Data (run once if not already done) ---
# This ensures that necessary NLTK data (stopwords, wordnet) is available.
# It's crucial that the preprocessing steps are identical to those used during training.
# try:
#     nltk.data.find('corpora/stopwords')
# except nltk.downloader.DownloadError:
#     nltk.download('stopwords')
# try:
#     nltk.data.find('corpora/wordnet')
# except nltk.downloader.DownloadError:
#     nltk.download('wordnet')
# try:
#     nltk.data.find('corpora/omw-1.4') # Required for WordNetLemmatizer
# except nltk.downloader.DownloadError:
#     nltk.download('omw-1.4')


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


# --- 6. Example Usage ---
if __name__ == '__main__':
    print("\n--- Making Predictions with Loaded Models ---")

    test_ticket_1 = """I am writing to report persistent and highly disruptive issues with my company email (Outlook 365) and calendar synchronization. This problem began immediately after the system-wide software update that was pushed out last Tuesday.

Specifically, my Outlook email client on my desktop (Windows 10, Dell Latitude 7420) is failing to sync new emails in real-time. There's a significant delay, often up to 15-20 minutes, before new messages appear in my inbox. I've tried restarting Outlook, restarting my laptop, and even checking my internet connection (which is stable and fast). The issue persists whether I'm connected via Wi-Fi or Ethernet.

Furthermore, my Outlook calendar is not syncing correctly with my mobile device (iPhone 13, iOS 17.5.1). Meetings I accept or create on my desktop do not show up on my phone, and vice-versa. This is causing me to miss important appointments and double-book myself, leading to significant professional embarrassment and impacting project deadlines. I've already tried re-adding my email account on my iPhone, but the problem remains. I also noticed that shared calendars are particularly affected; updates from my team members' calendars are not reflecting on my end.

I rely heavily on real-time email communication and an accurate calendar for my role in project management. This ongoing issue is severely hindering my productivity and ability to collaborate effectively. Could you please investigate this matter as soon as possible? I am available for a remote session or a desk visit at your earliest convenience"""
    dept1, prio1 = predict_ticket_category_loaded(test_ticket_1)
    print(f"Ticket: '{test_ticket_1}'")
    print(f"Predicted Department: {dept1}, Predicted Priority: {prio1}\n")
