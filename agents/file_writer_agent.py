import os
import re
from pathlib import Path


class FileWriterAgent:
    def run(self, texto_ia, ruta_base):
        print("Escribiendo archivos generados por IA...")

        ruta_base = Path(ruta_base)
        patron = r"====\s*ARCHIVO:\s*(.*?)\s*====\n(.*?)\n====\s*FIN_ARCHIVO\s*===="
        bloques = re.findall(patron, texto_ia or "", re.DOTALL)

        if not bloques:
            print("No se encontraron bloques de archivo en la respuesta.")
            return []

        archivos_generados = []

        for ruta_relativa, contenido in bloques:
            archivo_final = self._resolver_archivo_destino(ruta_base, ruta_relativa)
            os.makedirs(archivo_final.parent, exist_ok=True)

            limpio = re.sub(r"```[a-zA-Z0-9]*\n?", "", contenido)
            limpio = limpio.replace("```", "").strip()

            archivo_final.write_text(limpio, encoding="utf-8")
            archivos_generados.append(archivo_final)
            print(f"Archivo generado: {archivo_final}")

        return archivos_generados

    def _resolver_archivo_destino(self, ruta_base, ruta_relativa):
        partes = Path(ruta_relativa.strip()).parts

        if partes and partes[0].lower() == ruta_base.name.lower():
            partes = partes[1:]

        return ruta_base.joinpath(*partes)
