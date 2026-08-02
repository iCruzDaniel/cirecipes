# SDD — Especificación de Diseño: Biblioteca de Flujos CI/CD

> **Documento:** Especificación de Diseño del Repositorio (`cirecipes`)
> **Estado:** Base del repositorio — todo flujo nuevo debe cumplir esta especificación

## 1. Propósito

Este repositorio es una **biblioteca de flujos CI/CD listos para copiar y
pegar**. Su objetivo es que cualquier persona pueda encontrar un pipeline que
resuelva su necesidad, conocer sus requisitos (secretos, variables, versiones)
en segundos y trasladarlo a su proyecto sin adivinar nada.

Para lograrlo se define un **sistema de clasificación por códigos
(taxonomía)** combinado con una **jerarquía de directorios por plataforma y
stack**, una **ficha técnica por flujo** (`manifest.yml`) y un **flujo de
trabajo estándar de reutilización**.

## 2. Contexto

- Cada flujo se clasifica según su **caso de uso** (build, deploy, completo,
  seguridad) y el **tipo de arquitectura** en la que trabaja (VM, Kubernetes,
  registry, etc.).
- Los flujos se versionan individualmente para permitir que cada uno evolucione
  sin romper a quien ya copió una versión anterior.
- El contenido de los archivos de flujo (workflows, Jenkinsfiles, etc.) no se
  edita dentro de la biblioteca: se guardan tal cual funcionan y se documentan
  los puntos de adaptación.
- La biblioteca se valida a sí misma: un flujo de lint interno comprueba la
  sintaxis de los flujos recopilados y la presencia del `manifest.yml`.

## 3. Objetivos

1. **Encontrar rápido:** una convención de nombres uniforme y predecible.
2. **Reutilizar sin adivinar:** toda la metadata del flujo declarada en un
   `manifest.yml`.
3. **Versionar por flujo:** evolución independiente de cada pipeline.
4. **Documentar cada pipeline:** documentación general del repositorio +
   subdocumentación por flujo.

## 4. Decisiones de diseño

| Decisión | Opción elegida | Alternativa descartada |
| --- | --- | --- |
| Clasificación | Código taxonómico de 4 bloques (`PLATAFORMA-TIPO-STACK-DESTINO`) | Carpetas por nombre libre (difícil de filtrar por caso de uso) |
| Jerarquía | Plana: `plataforma/CODIGO-FLUJO/vN/` (la plataforma en la carpeta raíz, el resto en el código) | `plataforma/stack/codigo-flujo/vN/` (más niveles, redundante con el bloque STACK del código) |
| Metadata | `manifest.yml` junto al flujo dentro de `vN/` | README como única fuente (no parseable) |
| Versionado | Carpeta `vN/` solo para cambios mayores (breaking); parches y menores actualizan la misma carpeta con SemVer en el manifest | Tag por flujo en git (requiere clonar el repo completo) |
| Archivos de flujo | Contenido intacto; renombrar solo si es necesario | Editar/adaptar dentro de la biblioteca (contamina el original) |
| Validación | Flujo interno `.github/workflows/lint.yml` que valida sintaxis y manifest obligatorios | Sin validación automática (los errores se descubren al copiar) |

## 5. Especificación

### 5.1 Código de clasificación (taxonomía)

Cada carpeta de flujo usa una convención de 4 bloques separados por guiones:

```text
[PLATAFORMA]-[TIPO]-[STACK]-[ARQUITECTURA/DESTINO]
```

**Tabla de códigos:**

| Bloque | Significado | Ejemplos de códigos |
| --- | --- | --- |
| **Plataforma** | Motor de CI/CD | `GHA` (GitHub Actions), `JNK` (Jenkins), `GLB` (GitLab CI) |
| **Tipo** | Objetivo del flujo | `BUILD` (Build + Test), `DEPLOY` (Solo CD), `FULL` (CI + CD), `SEC` (Linter / SAST) |
| **Stack** | Lenguaje / Framework | `PY-FAST` (FastAPI), `JS-REACT` (React), `NODE` (Node.js), `DOCK` (Docker puro) |
| **Destino** | Dónde se despliega | `VM` (VPS / Servidor por SSH), `K8S` (Kubernetes), `REG` (Container Registry) |

**Ejemplos de carpetas usando el código:**

- `GHA-FULL-PY-FAST-VM` → GitHub Actions, CI/CD completo para FastAPI desplegando en VM por SSH.
- `JNK-DEPLOY-DOCK-K8S` → Jenkins, despliegue de imagen Docker hacia Kubernetes.
- `GHA-SEC-JS-REACT` → GitHub Actions, linter y análisis estático para un frontend en React.

### 5.2 Estructura de directorios

```text
/
├── github-actions/
│   ├── GHA-FULL-PY-FAST-VM/
│   │   ├── v1/
│   │   │   ├── workflow.yml
│   │   │   ├── manifest.yml
│   │   │   └── README.md
│   │   └── v2/
│   └── GHA-DEPLOY-JS-S3/
│       └── v1/
├── jenkins/
│   └── JNK-FULL-DOCK-VM/
│       └── v1/
│           └── Jenkinsfile
├── docs/
│   ├── SDD.md
│   ├── flows.md
│   └── img/
│       ├── cover.svg
│       ├── logo.svg
│       ├── favicon.svg
│       ├── favicon0.png
│       ├── favicon.png
│       ├── favicon.ico
│       ├── portada0.png
│       └── portada.png
└── templates-comunes/
    ├── docker-compose/
    └── systemd-scripts/
```

Reglas:

- Nivel 1: **plataforma** (`github-actions/`, `jenkins/`, `gitlab-ci/`). La
  plataforma vive en la carpeta raíz; el resto de la clasificación está en el
  código.
- Nivel 2: **código taxonómico** del flujo en mayúsculas (`GHA-FULL-PY-FAST-VM/`).
- Nivel 3: **versión** (`v1/`, `v2/`...).
- Dentro de cada versión: el/los archivos del flujo, el `manifest.yml` y un
  `README.md` con la subdocumentación del pipeline.
- `templates-comunes/`: recursos compartidos (docker-compose, scripts de
  systemd) reutilizables entre flujos.
- `docs/`: documentación general — `SDD.md` (este documento) y `flows.md`
  (catálogo con descripción y casos de uso de cada flujo).

### 5.3 Ficha técnica por flujo (`manifest.yml`)

Para no tener que adivinar qué variables o secretos necesita un flujo antes de
copiarlo, cada versión incluye un `manifest.yml` con su metadata:

```yaml
id: GHA-FULL-PY-FAST-VM
version: 1.2.0
plataforma: github-actions
stack:
  lenguaje: python 3.11
  framework: fastapi
arquitectura:
  tipo: contenedor
  destino: virtual-machine
  despliegue_via: ssh + docker-compose
version_compatibilidad:
  github_runner: ubuntu-latest
  docker_compose_version: ">=2.20"
secretos_requeridos:
  - SSH_HOST
  - SSH_USER
  - SSH_PRIVATE_KEY
  - DOCKER_HUB_TOKEN
variables_entorno:
  - APP_PORT
  - CONTAINER_NAME
```

Campos obligatorios:

| Campo | Descripción |
| --- | --- |
| `id` | Código taxonómico del flujo |
| `version` | Versión semver del flujo (debe coincidir con la carpeta `vN`) |
| `plataforma` | Motor de CI/CD (ej. `github-actions`) |
| `stack` | Lenguaje y framework |
| `arquitectura` | Tipo, destino y vía de despliegue |
| `version_compatibilidad` | Versiones mínimas de runner/acciones/herramientas |
| `secretos_requeridos` | Lista de secrets que deben existir en el repo destino |
| `variables_entorno` | Variables de entorno utilizadas por el flujo |

### 5.4 Regla de versionado

- La carpeta `vN/` corresponde a **cambios mayores (breaking changes)** de ese
  flujo. Se crea un `vN+1/` solo cuando el flujo deja de ser compatible con
  quien ya copió la versión anterior (ej. cambia el nombre de un secreto, la
  acción principal o el mecanismo de despliegue).
- Los **parches y cambios menores** (bugfixes, versiones nuevas de acciones,
  mejoras sin romper compatibilidad) **no crean carpeta nueva**: se actualizan
  los archivos dentro de la misma carpeta `vN/` y se incrementa la versión
  SemVer en el `manifest.yml` (ej. `1.0.0` → `1.1.0` → `1.1.1`).
- Regla de coherencia: el **major** de la versión SemVer del manifest debe
  coincidir con la `N` de la carpeta (`version: 2.3.0` vive en `v2/`). La
  validación interna la verifica automáticamente.

### 5.5 Flujo de trabajo para reutilizar

1. **Buscar por necesidad:** ir a la carpeta de la plataforma
   (`github-actions/`).
2. **Identificar la arquitectura:** ubicar la carpeta con el código
   taxonómico (`GHA-FULL-PY-FAST-VM/`).
3. **Revisar requisitos:** abrir el `manifest.yml` para ver qué `SECRETS`
   configurar en el repositorio destino.
4. **Copiar y pegar:** llevar el contenido del directorio `v1/` directamente
   al proyecto objetivo.

### 5.6 Documentación

- **`README.md` raíz:** documentación general — qué es el repo, mapa de
  navegación, índice de pipelines disponibles y guía rápida de reutilización.
- **`docs/flows.md`:** catálogo general — descripción breve de cada flujo y
  sus casos de uso.
- **`README.md` por flujo (dentro de `vN/`):** subdocumentación del pipeline —
  descripción, disparadores, jobs, secretos, requisitos previos y puntos de
  adaptación.
- **`docs/SDD.md`:** este documento, la base de diseño del repositorio.

## 6. Validación interna

El repositorio valida su propia biblioteca con un flujo de CI:

- **`.github/workflows/lint.yml`**: corre en cada push/PR sobre `main` y
  ejecuta `scripts/validate_flows.py` con Python 3.12 + PyYAML.
- **`scripts/validate_flows.py`** verifica:
  1. Sintaxis YAML válida en todos los `.yml`/`.yaml` del repositorio
     (incluido el propio `lint.yml`).
  2. Todo directorio de flujo (código taxonómico en mayúsculas) tiene al
     menos una carpeta `vN/`.
  3. Cada carpeta `vN/` contiene su `manifest.yml` obligatorio.
  4. El `manifest.yml` incluye los campos obligatorios `id`, `version` y
     `plataforma`.
  5. El `id` del manifest coincide con el nombre de la carpeta del flujo.
  6. El major de la versión SemVer coincide con la carpeta `vN/`.

Cualquier flujo nuevo debe pasar esta validación antes de mergearse.

## 7. Estado actual del repositorio

| Código | Versión | Descripción |
| --- | --- | --- |
| `GHA-DEPLOY-DOCK-REG` | v1 | Build + push de imagen Docker a GHCR; Dokploy realiza el deploy |
| `GHA-FULL-DOCK-VM` | v1 | Build + push a Docker Hub y deploy a VPS por SSH con docker compose |

## 8. Alcance futuro

- `templates-comunes/` con plantillas de `docker-compose` y scripts de systemd.
- Más plataformas (`jenkins/`, `gitlab-ci/`) y stacks (FastAPI, React, Node).
- Nuevos tipos de flujo: `SEC` (linter/SAST), `BUILD` puro, destinos `K8S` y `S3`.
