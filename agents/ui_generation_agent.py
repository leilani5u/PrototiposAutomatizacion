class UIGenerationAgent:
    def __init__(self, client, deployment):
        self.client = client
        self.deployment = deployment

    def run(self, especificaciones):
        print("Generando proyecto Angular...")

        prompt_ui = """
Eres un desarrollador frontend experto en Angular 17.

Devuelve el proyecto usando este formato de archivos:

==== ARCHIVO: ruta/del/archivo ====
codigo
==== FIN_ARCHIVO ====

Incluye los archivos necesarios para compilar el proyecto.
"""

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": prompt_ui},
                {"role": "user", "content": especificaciones},
            ],
        )

        return response.choices[0].message.content
