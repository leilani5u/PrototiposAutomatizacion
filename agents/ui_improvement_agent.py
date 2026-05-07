from openai import BadRequestError


def is_content_filter_error(exc):
    if getattr(exc, "code", None) == "content_filter":
        return True

    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        error = body.get("error", body)
        if error.get("code") == "content_filter":
            return True

        inner_error = error.get("innererror", {})
        return inner_error.get("code") == "ResponsibleAIPolicyViolation"

    return False


class UIImprovementAgent:
    def __init__(self, client, deployment):
        self.client = client
        self.deployment = deployment

    def run(self, proyecto_base, especificaciones):
        print("Mejorando UI...")

        prompt = f"""
Mejora la interfaz de este proyecto Angular 17.

Devuelve los cambios en este formato de archivos:

==== ARCHIVO: ruta ====
codigo
==== FIN_ARCHIVO ====

Prioriza una interfaz profesional para una aplicacion web moderna:

1. Diseno global
- Tipografia: Inter o Roboto
- Espaciado consistente basado en 8px
- Bordes redondeados
- Sombras suaves

2. Layout
- Sidebar profesional
- Header fijo
- Contenido organizado en secciones y cards

3. Componentes
- Botones con estados hover y focus
- Inputs estilizados
- Tablas con estados hover
- Cards limpias

4. UX
- Transiciones suaves
- Feedback visual claro
- Buena legibilidad

5. Responsive
- Adaptacion movil tipo app

Colores sugeridos:
- Primario: #003366
- Secundario: #0055aa
- Fondo: #f5f7fa

Proyecto actual:
{proyecto_base}

Contexto funcional:
{especificaciones}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un desarrollador frontend especializado en Angular "
                            "y diseno de interfaces de negocio."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
        except BadRequestError as exc:
            if is_content_filter_error(exc):
                print(
                    "Azure OpenAI filtro la mejora de UI. "
                    "Se continua con el proyecto generado inicialmente."
                )
                return proyecto_base
            raise

        return response.choices[0].message.content
