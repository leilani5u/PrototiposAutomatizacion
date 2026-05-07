class RequirementsAgent:
    def __init__(self, llamar_openai):
        self.llamar_openai = llamar_openai

    def run(self, texto):
        system_prompt = """
Extrae requerimientos accionables de software.
No escribas reflexiones, oportunidades, consultoria ni analisis narrativo.
Devuelve Markdown tecnico con secciones concretas y listas accionables.
"""

        user_prompt = f"""
Convierte el siguiente contenido en requisitos de software para generar un frontend Angular.

Incluye obligatoriamente:
- Resumen ejecutivo
- Tipo de sistema
- Usuarios y roles
- Funcionalidades
- Historias de usuario
- Modulos
- Entidades
- Flujo del sistema
- Pantallas necesarias
- Componentes UI
- Requerimientos tecnicos
- Arquitectura sugerida
- APIs necesarias
- Validaciones
- Permisos
- Estados
- Edge cases

Reglas:
- Requisitos accionables.
- Sin frases como "la transcripcion refleja", "esto indica", "desde producto" u "oportunidades".
- Si se mencionan velocidad, seguimiento, aprobaciones, metricas o usuarios, conviertelos en funcionalidades concretas.

Contenido:
{texto}
"""

        return self.llamar_openai(system_prompt, user_prompt)
