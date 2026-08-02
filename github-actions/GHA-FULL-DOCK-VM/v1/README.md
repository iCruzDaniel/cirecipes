# GHA-FULL-DOCK-VM — CI/CD Docker a VPS por SSH

> **Código:** `GHA-FULL-DOCK-VM` · **Versión:** v1 · **Plataforma:** GitHub Actions

Flujo completo de **integración y despliegue continuo (CI + CD)** para
aplicaciones Docker: compila la imagen, la publica en **Docker Hub** y la
despliega en un **VPS** por SSH usando `docker compose`.

## Disparadores (`on`)

| Evento | Condición |
| --- | --- |
| `push` | Rama `main` |
| `tags` | `v*.*.*` (ej. `v1.2.0`) |
| `workflow_dispatch` | Manual |

## Jobs

| Job | Descripción |
| --- | --- |
| `build` | Build con Buildx, etiquetado (`branch`, `tag`, `sha`, `latest`) y push a Docker Hub |
| `deploy` | Corre solo en `main` (`needs: build`). Prepara el directorio en el VPS, sube `docker-compose.yml` por SCP, hace pull y levanta con `docker compose up -d` |

## Secretos requeridos

| Secreto | Uso |
| --- | --- |
| `DOCKER_USERNAME` | Usuario de Docker Hub (login + nombre de la imagen) |
| `DOCKER_PASSWORD` | Password o token de Docker Hub |
| `VPS_HOST` | IP o dominio del VPS |
| `VPS_PORT` | Puerto SSH (opcional, default `22`) |
| `VPS_USER` | Usuario SSH del VPS |
| `VPS_SSH_KEY` | Llave privada SSH para conectarse al VPS |

## Variables de entorno

| Variable | Default |
| --- | --- |
| `IMAGE_NAME` | `${{ secrets.DOCKER_USERNAME }}/waitlistgo` |

## Requisitos previos

- Un archivo **`docker-compose.yml`** en la raíz del repositorio destino
  (el workflow lo sube al VPS por SCP).
- En el VPS: Docker + Docker Compose instalados.
- La imagen en Docker Hub debe ser accesible para `docker compose pull`
  desde el VPS.

## Cómo adaptarlo

1. Copia el contenido de esta carpeta (`v1/`) a tu repositorio destino, en
   `.github/workflows/`.
2. Cambia el nombre de la aplicación en `IMAGE_NAME` (`waitlistgo` es el
   proyecto de origen) y el directorio `/opt/waitlistgo` del script SSH.
3. Configura los secrets en **Settings → Secrets and variables → Actions**.
4. Asegúrate de tener `docker-compose.yml` en la raíz de tu proyecto.
