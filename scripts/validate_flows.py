#!/usr/bin/env python3
"""Valida la biblioteca de flujos CI/CD.

Reglas verificadas (ver docs/SDD.md):
  1. Sintaxis YAML válida en todos los archivos .yml/.yaml del repositorio
     (se excluyen directorios ocultos y entornos virtuales).
  2. Todo directorio de flujo (código taxonómico en mayúsculas) contiene al
     menos una carpeta de versión vN/.
  3. Cada carpeta vN/ contiene su manifest.yml obligatorio.
  4. El manifest.yml es YAML válido e incluye los campos obligatorios
     id, version y plataforma.
  5. El id del manifest coincide con el nombre de la carpeta del flujo.
  6. El major de la versión SemVer del manifest coincide con la carpeta vN/
     (la carpeta vN corresponde a cambios mayores / breaking changes).

Uso: python3 scripts/validate_flows.py
Salida: exit 0 si todo valida, exit 1 en caso contrario.
"""

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FLOW_DIR_RE = re.compile(r"^[A-Z]{3,4}(?:-[A-Z0-9]+){2,4}$")
VERSION_DIR_RE = re.compile(r"^v(\d+)$")
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

# Directorios de nivel raíz que no son plataformas de flujos
EXCLUDED_TOP_DIRS = {"docs", "scripts", "templates-comunes"}
# Directorios cuyo contenido no se considera parte de la biblioteca
EXCLUDED_DIR_PARTS = {".venv", "venv", "node_modules"}

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def collect_yaml_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if path.suffix not in {".yml", ".yaml"}:
            continue
        rel_parts = path.relative_to(REPO_ROOT).parts[:-1]
        # Los workflows propios del repo (.github/workflows/) se validan igual
        is_repo_ci = (
            len(rel_parts) >= 2
            and rel_parts[0] == ".github"
            and rel_parts[1] == "workflows"
        )
        if not is_repo_ci and any(
            part.startswith(".") or part in EXCLUDED_DIR_PARTS for part in rel_parts
        ):
            continue
        files.append(path)
    return files


def validate_yaml_syntax(files: list[Path]) -> None:
    for path in files:
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            fail(f"Sintaxis YAML inválida: {path.relative_to(REPO_ROOT)} -> {exc}")


def get_flow_dirs() -> list[tuple[Path, str]]:
    """Devuelve (ruta del flujo, plataforma) para cada flujo de la biblioteca."""
    flows: list[tuple[Path, str]] = []
    for platform in sorted(REPO_ROOT.iterdir()):
        if not platform.is_dir():
            continue
        if platform.name.startswith(".") or platform.name in EXCLUDED_TOP_DIRS:
            continue
        for flow in sorted(platform.iterdir()):
            if not flow.is_dir():
                warn(f"Archivo suelto en plataforma {platform.name}/: {flow.name}")
                continue
            if not FLOW_DIR_RE.match(flow.name):
                warn(
                    f"Directorio que no parece código taxonómico en {platform.name}/: "
                    f"{flow.name} (esperado [PLATAFORMA]-[TIPO]-[STACK]-[DESTINO])"
                )
                continue
            flows.append((flow, platform.name))
    return flows


def validate_flow(flow: Path, platform: str) -> None:
    rel = flow.relative_to(REPO_ROOT)
    version_dirs = [p for p in sorted(flow.iterdir()) if p.is_dir() and VERSION_DIR_RE.match(p.name)]
    if not version_dirs:
        fail(f"{rel}: el flujo no tiene carpetas de versión vN/")
        return

    for version_dir in version_dirs:
        vnum = int(VERSION_DIR_RE.match(version_dir.name).group(1))
        vrel = version_dir.relative_to(REPO_ROOT)
        manifest = version_dir / "manifest.yml"

        if not manifest.exists():
            fail(f"{vrel}: falta el manifest.yml obligatorio")
            continue

        try:
            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            fail(f"{manifest.relative_to(REPO_ROOT)}: YAML inválido -> {exc}")
            continue

        if not isinstance(data, dict):
            fail(f"{manifest.relative_to(REPO_ROOT)}: el manifest debe ser un mapeo YAML")
            continue

        for key in ("id", "version", "plataforma"):
            if key not in data:
                fail(f"{manifest.relative_to(REPO_ROOT)}: falta el campo obligatorio '{key}'")

        if data.get("id") != flow.name:
            fail(
                f"{manifest.relative_to(REPO_ROOT)}: el id '{data.get('id')}' no coincide "
                f"con la carpeta '{flow.name}'"
            )

        version_str = str(data.get("version", ""))
        semver = SEMVER_RE.match(version_str)
        if not semver:
            fail(f"{manifest.relative_to(REPO_ROOT)}: version '{version_str}' no es SemVer (x.y.z)")
        elif int(semver.group(1)) != vnum:
            fail(
                f"{manifest.relative_to(REPO_ROOT)}: la version {version_str} no coincide con la "
                f"carpeta {version_dir.name} (major != {vnum})"
            )


def main() -> int:
    print(f"Validando biblioteca en {REPO_ROOT}")
    yaml_files = collect_yaml_files()
    validate_yaml_syntax(yaml_files)
    flows = get_flow_dirs()
    for flow, platform in flows:
        validate_flow(flow, platform)

    print(f"- {len(yaml_files)} archivos YAML revisados")
    print(f"- {len(flows)} flujos validados")
    for w in warnings:
        print(f"  AVISO: {w}")
    for e in errors:
        print(f"  ERROR: {e}")

    if errors:
        print(f"\n{len(errors)} error(es) encontrado(s).")
        return 1
    print("\nValidación exitosa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
