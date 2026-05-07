class CleaningAgent:

    def __init__(self, llamar_openai):
        self.llamar_openai = llamar_openai

    def dividir_texto(self, texto, max_chars=8000):
        return [texto[i:i+max_chars] for i in range(0, len(texto), max_chars)]

    def run(self, texto):
        print("🧹 Limpiando transcripción...")

        prompt = """
        Limpia la transcripción:
        - corrige gramática
        - elimina muletillas
        - organiza ideas
        """

        partes = self.dividir_texto(texto)

        resultado = ""

        for parte in partes:
            limpio = self.llamar_openai(prompt, parte)
            resultado += limpio + "\n"

        return resultado