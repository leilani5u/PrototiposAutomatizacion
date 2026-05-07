import argparse
import re
import sys
from pathlib import Path

from orchestrator import Orchestrator
from config.settings import (
    MS_CLIENT_ID,
    MS_CLIENT_SECRET,
    MS_TENANT_ID,
    SHAREPOINT_FILE_URL,
)
from services.sharepoint_service import SharePointService


PROJECT_ROOT = Path(__file__).resolve().parent
PROJECTS_OUTPUT_DIR = Path("C:/Users/a_barrientos.m/proyectos")
SHAREPOINT_DOWNLOAD_DIR = PROJECT_ROOT / "downloads" / "sharepoint"
DEFAULT_SOURCE_PATH = Path(
    "C:/Users/a_barrientos.m/OneDrive - Secretar\u00eda de Educaci\u00f3n de Guanajuato/"
    "Seguimiento de Requisitos - Documentos"
)
SUPPORTED_SOURCE_EXTENSIONS = {
    ".aac",
    ".avi",
    ".m4a",
    ".md",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".srt",
    ".txt",
    ".vtt",
    ".wav",
    ".webm",
    ".wma",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Genera un prototipo Angular desde video, audio o transcripcion."
    )
    parser.add_argument(
        "source_path",
        nargs="?",
        default=DEFAULT_SOURCE_PATH,
        type=Path,
        help="Ruta local del archivo o carpeta a procesar.",
    )
    parser.add_argument(
        "--sharepoint-url",
        default=SHAREPOINT_FILE_URL,
        help="URL compartida de SharePoint/OneDrive del video, audio o transcripcion.",
    )
    parser.add_argument(
        "--project-name",
        help="Nombre de la carpeta del proyecto dentro de C:/Users/a_barrientos.m/proyectos.",
    )
    return parser.parse_args()


def resolve_local_path(source_path):
    resolved_path = source_path if source_path.is_absolute() else PROJECT_ROOT / source_path

    if resolved_path.is_dir():
        return find_latest_source_file(resolved_path)

    return resolved_path


def find_latest_source_file(source_dir):
    files = [
        path
        for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SOURCE_EXTENSIONS
    ]

    if not files:
        extensions = ", ".join(sorted(SUPPORTED_SOURCE_EXTENSIONS))
        raise FileNotFoundError(
            f"No se encontraron archivos compatibles en: {source_dir}\n"
            f"Extensiones soportadas: {extensions}"
        )

    return max(files, key=lambda path: path.stat().st_mtime)


def resolve_source_path(args):
    if args.sharepoint_url:
        sharepoint_service = SharePointService(
            tenant_id=MS_TENANT_ID,
            client_id=MS_CLIENT_ID,
            client_secret=MS_CLIENT_SECRET,
        )
        downloaded_path = sharepoint_service.download_file(
            args.sharepoint_url,
            SHAREPOINT_DOWNLOAD_DIR,
        )
        print(f"Archivo descargado desde SharePoint: {downloaded_path}")
        return downloaded_path

    return resolve_local_path(args.source_path)


def resolve_project_output_dir(project_name):
    clean_name = sanitize_project_name(project_name or ask_project_name())
    return PROJECTS_OUTPUT_DIR / clean_name


def ask_project_name():
    name = input("Nombre de la carpeta del proyecto: ").strip()

    if not name:
        raise ValueError("Debes escribir un nombre de carpeta para el proyecto.")

    return name


def sanitize_project_name(project_name):
    clean_name = re.sub(r'[<>:"/\\|?*]', "_", project_name).strip().strip(".")

    if not clean_name:
        raise ValueError("El nombre de carpeta del proyecto no es valido.")

    return clean_name


def main():
    try:
        args = parse_args()
        source_path = resolve_source_path(args)
        output_dir = resolve_project_output_dir(args.project_name)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(exc)
        sys.exit(1)

    from config.azure_config import chat_client, transcribe_client
    from config.settings import CHAT_DEPLOYMENT, TRANSCRIBE_DEPLOYMENT
    from services.openai_service import OpenAIService

    chat_model = CHAT_DEPLOYMENT
    transcribe_model = TRANSCRIBE_DEPLOYMENT
    openai_service = OpenAIService(
        client=chat_client,
        deployment=CHAT_DEPLOYMENT
    )

    orq = Orchestrator(
        chat_client=chat_client,
        chat_model=chat_model,
        transcribe_client=transcribe_client,
        transcribe_model=transcribe_model,
        openai_service=openai_service,
        output_dir=output_dir,
    )

    try:
        resultado = orq.run(source_path)
    except (FileNotFoundError, RuntimeError) as exc:
        print(exc)
        sys.exit(1)

    if resultado.requerimientos:
        print(resultado.requerimientos)


if __name__ == "__main__":
    main()
