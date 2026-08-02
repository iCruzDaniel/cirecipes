# GHA-DEPLOY-DOCK-REG — Build & Push a GHCR (Deploy vía Dokploy)

> **Código:** `GHA-DEPLOY-DOCK-REG` · **Versión:** v1 · **Plataforma:** GitHub Actions

Flujo de despliegue continuo para aplicaciones Docker que se publican en el
**GitHub Container Registry (GHCR)** y son consumidas por **Dokploy** para
realizar el deploy. El workflow no toca el servidor directamente: publica la
imagen y Dokploy detecta la actualización.

## Disparadores (`on`)

| Evento | Condición |
| --- | --- |
| `push` | Rama `main` |
| `workflow_dispatch` | Manual |

## Jobs

| Job | Descripción |
| --- | --- |
| `build-and-push` | Build de la imagen Docker con Buildx, etiquetado (`sha` + `latest`) y push a `ghcr.io` |

## Secretos requeridos

| Secreto | Uso |
| --- | --- |
| `GITHUB_TOKEN` | Automático. El job declara `permissions: packages: write` para poder publicar en GHCR |

No requiere secretos adicionales.

## Variables de entorno

| Variable | Default |
| --- | --- |
| `REGISTRY` | `ghcr.io` |
| `IMAGE_NAME` | `${{ github.repository }}` |

## Requisitos previos

- Acceso de escritura a paquetes (`packages: write`) habilitado para el repositorio.
- Un servicio **Dokploy** configurado para desplegar desde el paquete GHCR de este repositorio.

## Cómo adaptarlo

1. Copia el contenido de esta carpeta (`v1/`) a tu repositorio destino, en
   `.github/workflows/`.
2. Ajusta `IMAGE_NAME` si tu imagen no debe usar `github.repository` o si usas
   un registry distinto.
3. Verifica que tu proyecto tenga el `Dockerfile` correcto para el build.
4. Configura Dokploy para escuchar el nuevo paquete del registry.
