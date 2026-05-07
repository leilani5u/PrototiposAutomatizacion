import subprocess
from pathlib import Path


class TranscriptionAgent:

    def convertir_a_wav_segmentado(self, input_mp4):
        import uuid

        input_path = Path(input_mp4).resolve()

        if not input_path.is_file():
            raise FileNotFoundError(
                f"No se encontro el archivo: {input_path}\n"
                "Coloca el archivo en uploads/video.mp4, usa --sharepoint-url, "
                "o ejecuta: python main.py ruta/al/archivo.mp4"
            )

        base_path = input_path.parent
        output_pattern = base_path / f"chunk_{uuid.uuid4().hex}_%03d.wav"

        comando = [
            "ffmpeg",
            "-i", str(input_path),
            "-f", "segment",
            "-segment_time", "60",
            "-ac", "1",
            "-ar", "16000",
            "-vn",
            str(output_pattern)
        ]

        try:
            subprocess.run(comando, check=True)
        except FileNotFoundError as exc:
            raise RuntimeError(
                "No se encontro ffmpeg en el PATH. Instala ffmpeg o agregalo al PATH."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"ffmpeg no pudo procesar el archivo: {input_path}"
            ) from exc

        return list(base_path.glob(output_pattern.name.replace("%03d", "*")))

    def transcribir_audio(self, ruta_audio, client, deployment):
        with open(ruta_audio, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=deployment,
                file=audio_file
            )
        return transcript.text

    def run(self, video_path, client, deployment):
        print("🎥 Transcribiendo video...")

        chunks = self.convertir_a_wav_segmentado(video_path)

        chunks = sorted(
            chunks,
            key=lambda x: int(x.stem.split("_")[-1])
        )

        texto_total = ""

        for chunk in chunks:
            try:
                texto = self.transcribir_audio(chunk, client, deployment)
                texto_total += texto + "\n"
            except Exception as e:
                print(f"Error en chunk {chunk}: {e}")

        Path("transcripcion_completa.txt").write_text(texto_total, encoding="utf-8")

        return texto_total
