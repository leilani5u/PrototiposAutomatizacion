from pathlib import Path

class FileService:

    @staticmethod
    def ensure_directory(path):
        Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def save_text(path, content):

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)