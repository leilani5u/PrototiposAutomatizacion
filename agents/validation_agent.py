import os
import json
import shutil
import subprocess
import time
import requests

from pathlib import Path


class ValidationAgent:

    def __init__(self, llamar_openai=None, max_retries=3):

        self.llamar_openai = llamar_openai
        self.max_retries = max_retries

    # =====================================================
    # VALIDAR ESTRUCTURA
    # =====================================================

    def check_structure(self, base_path: Path):

        required_files = [
            "package.json",
            "angular.json",
            "tsconfig.json",
            "src/main.ts",
            "src/index.html",
        ]

        missing = []

        for file in required_files:

            if not (base_path / file).exists():
                missing.append(file)

        return missing

    # =====================================================
    # INSTALAR DEPENDENCIAS
    # =====================================================

    def install_dependencies(self, base_path: Path):

        print("📦 Instalando dependencias...")

        command = (
            "npm install"
            if os.name == "nt"
            else ["npm", "install"]
        )

        result = subprocess.run(
            command,
            cwd=base_path,
            shell=os.name == "nt",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:

            print("❌ Error en npm install")
            print(result.stdout)
            print(result.stderr)

            raise Exception("npm install falló")

        print("✅ Dependencias instaladas")

    # =====================================================
    # ASEGURAR ANGULAR CLI
    # =====================================================

    def ensure_angular_cli(self, base_path: Path):

        print("🛠 Instalando Angular CLI...")

        command = (
            "npm install @angular/cli --save-dev"
            if os.name == "nt"
            else ["npm", "install", "@angular/cli", "--save-dev"]
        )

        subprocess.run(
            command,
            cwd=base_path,
            shell=os.name == "nt"
        )

    # =====================================================
    # LIMPIAR NODE_MODULES
    # =====================================================

    def clean_node_modules(self, base_path: Path):

        node_modules = base_path / "node_modules"
        package_lock = base_path / "package-lock.json"

        if node_modules.exists():

            shutil.rmtree(
                node_modules,
                ignore_errors=True
            )

        if package_lock.exists():
            package_lock.unlink()

        print("🧹 node_modules eliminado")

    # =====================================================
    # CORREGIR DEPENDENCIAS ANGULAR
    # =====================================================

    def fix_angular_dependencies(self, base_path: Path):

        package_json_path = base_path / "package.json"

        if not package_json_path.exists():
            return False

        with open(
            package_json_path,
            "r",
            encoding="utf-8"
        ) as f:

            package_data = json.load(f)

        # ============================================
        # SCRIPTS
        # ============================================

        package_data["scripts"] = {
            "ng": "ng",
            "start": "ng serve",
            "build": "ng build",
            "watch": "ng build --watch --configuration development",
            "test": "ng test"
        }

        # ============================================
        # VERSIONES ANGULAR
        # ============================================

        angular_version = "^19.2.0"

        dependencies = package_data.get(
            "dependencies",
            {}
        )

        required_packages = {
            "@angular/animations": angular_version,
            "@angular/common": angular_version,
            "@angular/common/http": angular_version,
            "@angular/compiler": angular_version,
            "@angular/core": angular_version,
            "@angular/forms": angular_version,
            "@angular/platform-browser": angular_version,
            "@angular/platform-browser-dynamic": angular_version,
            "@angular/router": angular_version,
            "rxjs": "~7.8.0",
            "zone.js": "~0.15.0",
            "tslib": "^2.3.0"
        }

        dependencies.update(required_packages)

        package_data["dependencies"] = dependencies

        # ============================================
        # DEV DEPENDENCIES
        # ============================================

        dev_dependencies = package_data.get(
            "devDependencies",
            {}
        )

        required_dev = {
            "@angular/cli": angular_version,
            "@angular/compiler-cli": angular_version,
            "@angular-devkit/build-angular": angular_version,
            "typescript": "~5.5.0"
        }

        dev_dependencies.update(required_dev)

        package_data["devDependencies"] = dev_dependencies

        # ============================================
        # GUARDAR PACKAGE.JSON
        # ============================================

        with open(
            package_json_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                package_data,
                f,
                indent=2
            )

        print("✅ package.json Angular corregido")

        return True

    # =====================================================
    # CORREGIR ANGULAR.JSON
    # =====================================================

    def fix_angular_json(self, base_path: Path):

        angular_json_path = base_path / "angular.json"

        project_name = base_path.name.lower().replace(" ", "-")

        config = {
            "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
            "version": 1,
            "defaultProject": project_name,
            "projects": {
                project_name: {
                    "projectType": "application",
                    "root": "",
                    "sourceRoot": "src",
                    "prefix": "app",
                    "targets": {

                        "build": {
                            "builder": "@angular-devkit/build-angular:application",

                            "options": {
                                "outputPath": f"dist/{project_name}",
                                "index": "src/index.html",
                                "browser": "src/main.ts",

                                "polyfills": [
                                    "zone.js"
                                ],

                                "tsConfig": "tsconfig.app.json",

                                "assets": [
                                    {
                                        "glob": "**/*",
                                        "input": "public"
                                    }
                                ],

                                "styles": [
                                    "src/styles.css"
                                ]
                            },

                            "configurations": {

                                "production": {
                                    "optimization": True,
                                    "extractLicenses": True,
                                    "sourceMap": False
                                },

                                "development": {
                                    "optimization": False,
                                    "extractLicenses": False,
                                    "sourceMap": True
                                }
                            },

                            "defaultConfiguration": "production"
                        },

                        "serve": {
                            "builder": "@angular-devkit/build-angular:dev-server",

                            "configurations": {

                                "development": {
                                    "buildTarget": f"{project_name}:build:development"
                                },

                                "production": {
                                    "buildTarget": f"{project_name}:build:production"
                                }
                            },

                            "defaultConfiguration": "development"
                        }
                    }
                }
            }
        }

        with open(
            angular_json_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(config, f, indent=2)

        print("✅ angular.json corregido")

    # =====================================================
    # EJECUTAR BUILD
    # =====================================================

    def run_build(self, base_path: Path):

        print("🏗 Ejecutando Angular build...")

        command = (
            "npx ng build --verbose"
            if os.name == "nt"
            else ["npx", "ng", "build", "--verbose"]
        )

        result = subprocess.run(
            command,
            cwd=base_path,
            shell=os.name == "nt",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        return result

    # =====================================================
    # GUARDAR LOGS
    # =====================================================

    def save_logs(
        self,
        base_path: Path,
        content: str
    ):

        log_path = base_path / "build_errors.log"

        with open(
            log_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(content)

        print(f"📝 Logs guardados en: {log_path}")

    # =====================================================
    # LEER ARCHIVOS PROYECTO
    # =====================================================

    def get_project_files(self, base_path: Path):

        allowed_extensions = [
            ".ts",
            ".html",
            ".css",
            ".scss",
            ".json"
        ]

        content = ""

        for file in base_path.rglob("*"):

            if file.suffix.lower() in allowed_extensions:

                try:

                    relative = file.relative_to(base_path)

                    with open(
                        file,
                        "r",
                        encoding="utf-8",
                        errors="replace"
                    ) as f:

                        text = f.read()

                    content += (
                        f"\n\n===== ARCHIVO: "
                        f"{relative} =====\n"
                    )

                    content += text

                except Exception:
                    pass

        return content

    # =====================================================
    # CORREGIR CON IA
    # =====================================================

    def fix_errors_with_ai(
        self,
        base_path: Path,
        error_output: str,
        proyecto_texto=None
    ):

        if not self.llamar_openai:

            print("⚠ No hay función OpenAI configurada")
            return False

        print("🤖 Intentando corrección automática...")

        project_files = self.get_project_files(base_path)

        prompt = f"""
Eres un experto en Angular.

OBJETIVO:
Corregir automáticamente un proyecto Angular que NO compila.

El proyecto DEBE:
- compilar sin errores
- ejecutar ng serve correctamente
- iniciar localhost:4200
- no tener errores TypeScript
- no tener imports inválidos
- no tener módulos faltantes
- ser Angular standalone

IMPORTANTE:
- Angular standalone
- Angular 19 ONLY
- NO mezclar versiones Angular
- TODOS los @angular/* deben tener la misma versión

REGLAS:
- SOLO devolver JSON
- NO markdown
- NO explicaciones

FORMATO:

{{
  "files": [
    {{
      "path": "src/app/app.component.ts",
      "content": "contenido"
    }}
  ]
}}

ERRORES:

{error_output}

REQUERIMIENTOS:

{proyecto_texto}

ARCHIVOS:

{project_files}
"""

        try:

            response = self.llamar_openai(prompt)

            response = response.replace(
                "```json",
                ""
            )

            response = response.replace(
                "```",
                ""
            )

            response = response.strip()

            data = json.loads(response)

            if "files" not in data:

                print("❌ JSON inválido")
                return False

            for file_data in data["files"]:

                clean_path = file_data["path"].lstrip("/\\")

                path = base_path / clean_path

                path.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                with open(
                    path,
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(file_data["content"])

                print(f"✅ Archivo corregido: {path}")

            return True

        except Exception as e:

            print("❌ Error corrigiendo con IA")
            print(str(e))

            return False

    # =====================================================
    # VALIDAR ANGULAR JSON
    # =====================================================

    def validate_angular_json(self, base_path: Path):

        angular_json = base_path / "angular.json"

        if not angular_json.exists():
            return False

        try:

            with open(
                angular_json,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            if "projects" not in data:
                return False

            return True

        except Exception:
            return False

    # =====================================================
    # EJECUTAR ANGULAR SERVE
    # =====================================================

    def run_angular_serve(self, base_path: Path):

        print("🚀 Iniciando Angular serve...")

        command = (
            "npx ng serve --port 4200"
            if os.name == "nt"
            else ["npx", "ng", "serve", "--port", "4200"]
        )

        process = subprocess.Popen(
            command,
            cwd=base_path,
            shell=os.name == "nt",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        return process

    # =====================================================
    # VALIDAR APP EJECUTÁNDOSE
    # =====================================================

    def validate_running_app(self, process):

        print("🔎 Validando servidor Angular...")

        timeout = 60

        start = time.time()

        logs = ""

        while time.time() - start < timeout:

            line = process.stdout.readline()

            if not line:
                continue

            logs += line

            print(line.strip())

            success_patterns = [
                "Application bundle generation complete",
                "Local:",
                "localhost:4200"
            ]

            if any(p in line for p in success_patterns):

                print("🌐 Verificando localhost:4200...")

                try:

                    response = requests.get(
                        "http://localhost:4200",
                        timeout=10
                    )

                    if response.status_code == 200:

                        print("✅ Angular funcionando correctamente")

                        return True, logs

                    else:

                        print(
                            f"❌ HTTP inválido: "
                            f"{response.status_code}"
                        )

                except Exception as e:

                    print("❌ Angular no respondió HTTP")
                    print(str(e))

            error_patterns = [
                "ERROR",
                "Cannot determine project",
                "Module not found",
                "TS2307"
            ]

            if any(p in line for p in error_patterns):

                print("❌ Error detectado en runtime")

                return False, logs

        return False, logs

    # =====================================================
    # FLUJO PRINCIPAL
    # =====================================================

    def run(
        self,
        base_path: Path,
        proyecto_texto=None
    ):

        print("\n==============================")
        print("🚀 VALIDATION AGENT")
        print("==============================\n")

        missing = self.check_structure(base_path)

        if missing:

            print("❌ Faltan archivos obligatorios:")

            for file in missing:
                print("-", file)

            return False

        try:

            self.fix_angular_json(base_path)

            self.fix_angular_dependencies(base_path)

            self.ensure_angular_cli(base_path)

            self.install_dependencies(base_path)

        except Exception as e:

            print("❌ Error instalando dependencias")
            print(str(e))

            return False

        for attempt in range(
            1,
            self.max_retries + 1
        ):

            print(f"\n🔁 Intento #{attempt}")

            result = self.run_build(base_path)

            error_output = (
                result.stdout +
                "\n\n" +
                result.stderr
            )

            print("\n========== STDOUT ==========\n")
            print(result.stdout)

            print("\n========== STDERR ==========\n")
            print(result.stderr)

            # ========================================
            # BUILD EXITOSO
            # ========================================

            if result.returncode == 0:

                print("\n✅ BUILD EXITOSO")

                serve_process = self.run_angular_serve(base_path)

                success, runtime_logs = self.validate_running_app(
                    serve_process
                )

                serve_process.terminate()

                if success:

                    print("🎉 Proyecto Angular funcionando")

                    return True

                error_output += "\n\n" + runtime_logs

            # ========================================
            # ERROR CONFIG ANGULAR
            # ========================================

            angular_config_errors = [
                "Cannot determine project or target for command",
                "Project target does not exist",
                "Workspace extension"
            ]

            if any(
                err in error_output
                for err in angular_config_errors
            ):

                print("⚠ Configuración Angular inválida")

                self.fix_angular_json(base_path)

                continue

            # ========================================
            # ERROR DEPENDENCIAS
            # ========================================

            angular_dependency_errors = [
                "@angular/common/http",
                "@angular/core/primitives/di",
                "@angular/platform-browser/animations",
                "Cannot find module"
            ]

            if any(
                err in error_output
                for err in angular_dependency_errors
            ):

                print(
                    "⚠ Detectado problema "
                    "de dependencias Angular"
                )

                self.clean_node_modules(base_path)

                self.fix_angular_dependencies(base_path)

                self.install_dependencies(base_path)

                continue

            # ========================================
            # GUARDAR LOGS
            # ========================================

            self.save_logs(
                base_path,
                error_output
            )

            # ========================================
            # ÚLTIMO INTENTO
            # ========================================

            if attempt == self.max_retries:

                print(
                    f"\n❌ Build fallido "
                    f"después de "
                    f"{self.max_retries} intentos:"
                )

                print(base_path)

                return False

            # ========================================
            # CORREGIR CON IA
            # ========================================

            fixed = self.fix_errors_with_ai(
                base_path,
                error_output,
                proyecto_texto
            )

            if fixed:

                self.install_dependencies(base_path)

            else:

                print(
                    "❌ No se pudieron "
                    "aplicar correcciones"
                )

                return False

        return False