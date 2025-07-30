import pickle
import re
import nltk
from pathlib import Path
from typing import Tuple, Optional
import logging

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from ..config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClassifierService:
    """Service for ticket classification."""
    
    def __init__(self):
        """Initialize the classifier service and load models."""
        self._load_models()
        self._download_nltk_resources()
    
    def _download_nltk_resources(self):
        """Download required NLTK resources."""
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        try:
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            nltk.download('omw-1.4')
    
    def _load_models(self):
        """Load all required models and encoders."""
        try:
            with open(settings.TFIDF_VECTORIZER_PATH, 'rb') as f:
                self.tfidf_vectorizer = pickle.load(f)
            
            with open(settings.LE_DEPARTMENT_PATH, 'rb') as f:
                self.le_department = pickle.load(f)
            
            with open(settings.LE_PRIORITY_PATH, 'rb') as f:
                self.le_priority = pickle.load(f)
            
            with open(settings.LOG_REG_DEPT_PATH, 'rb') as f:
                self.log_reg_dept = pickle.load(f)
            
            with open(settings.LOG_REG_PRIO_PATH, 'rb') as f:
                self.log_reg_prio = pickle.load(f)
                
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess the input text.
        
        Args:
            text: Raw input text
            
        Returns:
            Preprocessed text
        """
        if not isinstance(text, str):
            return ""
            
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = text.lower()
        words = text.split()
        
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word not in stop_words]
        
        lemmatizer = WordNetLemmatizer()
        words = [lemmatizer.lemmatize(word) for word in words]
        
        return ' '.join(words)
    
    def predict(self, description: str) -> Tuple[str, str]:
        """
        Predict department and priority for a ticket description.
        
        Args:
            description: Ticket description
            
        Returns:
            Tuple of (department, priority)
        """
        try:
            if not description.strip():
                raise ValueError("Description cannot be empty")
                
            # Preprocess
            clean_description = self.preprocess_text(description)
            
            # Transform
            description_tfidf = self.tfidf_vectorizer.transform([clean_description])
            
            # Predict
            dept_encoded = self.log_reg_dept.predict(description_tfidf)
            prio_encoded = self.log_reg_prio.predict(description_tfidf)
            
            # Inverse transform
            department = self.le_department.inverse_transform(dept_encoded)[0]
            priority = self.le_priority.inverse_transform(prio_encoded)[0]
            
            return department, priority
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
