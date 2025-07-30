from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Model paths
    TFIDF_VECTORIZER_PATH: str = str(Path(__file__).parent / "models" / "tfidf_vectorizer.pkl")
    LE_DEPARTMENT_PATH: str = str(Path(__file__).parent / "models" / "le_department.pkl")
    LE_PRIORITY_PATH: str = str(Path(__file__).parent / "models" / "le_priority.pkl")
    LOG_REG_DEPT_PATH: str = str(Path(__file__).parent / "models" / "log_reg_dept_model.pkl")
    LOG_REG_PRIO_PATH: str = str(Path(__file__).parent / "models" / "log_reg_prio_model.pkl")
    
    # API settings
    API_TITLE: str = "Ticket Classification API"
    API_DESCRIPTION: str = "API for classifying support tickets into departments and priorities"
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
