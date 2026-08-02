# Catálogo de flujos

Descripción breve y casos de uso de cada pipeline de la biblioteca. Para los
requisitos técnicos (secretos, variables, compatibilidad) ver el
`manifest.yml` de cada flujo.

---

## GHA-DEPLOY-DOCK-REG

| Campo | Valor |
| --- | --- |
| Plataforma | GitHub Actions |
| Tipo | DEPLOY (CD) |
| Stack | Docker |
| Destino | Container Registry (GHCR) |
| Versión actual | [v1](github-actions/GHA-DEPLOY-DOCK-REG/v1/README.md) |

**Qué hace:** compila la imagen Docker con Buildx, la etiqueta (`sha` + `latest`)
y la publica en el GitHub Container Registry. No se conecta a ningún servidor:
Dokploy detecta la imagen nueva y ejecuta el despliegue.

**Casos de uso:**

- Aplicaciones Docker desplegadas con **Dokploy** (PaaS self-hosted) que
  consumen imágenes desde GHCR.
- Equipos que quieren centralizar las imágenes en el **mismo GitHub** sin
  crear una cuenta en otro registry.
- Proyectos que ya tienen el deployment gestionado externamente y solo
  necesitan que la imagen esté publicada y actualizada.

---

## GHA-FULL-DOCK-VM

| Campo | Valor |
| --- | --- |
| Plataforma | GitHub Actions |
| Tipo | FULL (CI + CD) |
| Stack | Docker |
| Destino | VM / VPS (SSH) |
| Versión actual | [v1](github-actions/GHA-FULL-DOCK-VM/v1/README.md) |

**Qué hace:** flujo completo. Compila la imagen, la publica en **Docker Hub** y
despliega en un **VPS** por SSH: prepara el directorio, sube el
`docker-compose.yml` por SCP y levanta los contenedores con
`docker compose up -d`.

**Casos de uso:**

- Aplicaciones Docker en un **VPS propio** (DigitalOcean, Hetzner, Vultr, etc.)
  sin plataforma gestionada.
- Despliegue con `docker compose` cuando el proyecto ya tiene su
  `docker-compose.yml` en la raíz del repositorio.
- Flujos que necesitan **CI + CD en un solo workflow**: construir, publicar y
  desplegar en cada push a `main` o tag `v*.*.*`.
