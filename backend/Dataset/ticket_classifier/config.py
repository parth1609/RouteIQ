from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import find_dotenv

class Settings(BaseSettings):
    # Model paths - pointing to the models directory in the parent folder
    TFIDF_VECTORIZER_PATH: str = str(Path(__file__).parent.parent / "models" / "tfidf_vectorizer.pkl")
    LE_DEPARTMENT_PATH: str = str(Path(__file__).parent.parent / "models" / "le_department.pkl")
    LE_PRIORITY_PATH: str = str(Path(__file__).parent.parent / "models" / "le_priority.pkl")
    LOG_REG_DEPT_PATH: str = str(Path(__file__).parent.parent / "models" / "log_reg_dept_model.pkl")
    LOG_REG_PRIO_PATH: str = str(Path(__file__).parent.parent / "models" / "log_reg_prio_model.pkl")
    
    # API settings
    API_TITLE: str = "Ticket Classification API"
    API_DESCRIPTION: str = "API for classifying support tickets into departments and priorities"
    API_VERSION: str = "1.0.0"

    # Pydantic v2 settings: ignore unrelated env vars and point to root .env
    model_config = SettingsConfigDict(
        env_file=find_dotenv(usecwd=True),
        case_sensitive=True,
        extra="ignore",
    )

    def _abs(self, p: str) -> str:
        """Return absolute path robustly.
        - Absolute -> return as-is
        - Starts with './' -> resolve from repo root
        - Contains 'Dataset/models' -> try resolving from repo root
        - Otherwise -> resolve from backend/Dataset
        """
        path = Path(p)
        if path.is_absolute():
            return str(path)
        # repo root = .../RouteIQ
        repo_root = Path(__file__).resolve().parents[3]
        s = str(p)
        if s.startswith('./'):
            s = s[2:]
        # Map bare 'Dataset/...' to actual location under backend/
        if s.startswith('Dataset/'):
            return str((repo_root / 'backend' / s).resolve())
        if s.startswith('backend/Dataset/'):
            return str((repo_root / s).resolve())
        base = Path(__file__).parent.parent  # backend/Dataset
        return str((base / p).resolve())

    def model_post_init(self, __context) -> None:  # pydantic v2 hook
        # Normalize all model file paths to absolute paths for robustness
        self.TFIDF_VECTORIZER_PATH = self._abs(self.TFIDF_VECTORIZER_PATH)
        self.LE_DEPARTMENT_PATH = self._abs(self.LE_DEPARTMENT_PATH)
        self.LE_PRIORITY_PATH = self._abs(self.LE_PRIORITY_PATH)
        self.LOG_REG_DEPT_PATH = self._abs(self.LOG_REG_DEPT_PATH)
        self.LOG_REG_PRIO_PATH = self._abs(self.LOG_REG_PRIO_PATH)

# Create settings instance
settings = Settings()
