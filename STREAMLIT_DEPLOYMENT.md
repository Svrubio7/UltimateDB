# Despliegue de la Aplicación Streamlit en Streamlit Community Cloud

Esta guía explica cómo desplegar tu aplicación BDNS Convocatorias en Streamlit Community Cloud de forma completamente gratuita.

## Requisitos Previos

1. **Cuenta de GitHub**: Necesitas una cuenta en GitHub (gratis)
2. **Repositorio Git**: Tu proyecto debe estar en un repositorio de GitHub
3. **Cuenta de Streamlit Community Cloud**: Crear una cuenta en [share.streamlit.io](https://share.streamlit.io) (gratis, usando tu cuenta de GitHub)

## Paso 1: Preparar tu Repositorio de GitHub

### 1.1 Inicializar Git (si aún no lo has hecho)

```bash
cd "C:\Users\svrub\Documents\Mis cosillas\ProyectosPersonales\Mapscanner"
git init
git add .
git commit -m "Initial commit: BDNS scanner and Streamlit app"
```

### 1.2 Crear un Repositorio en GitHub

1. Ve a [github.com](https://github.com)
2. Haz clic en el botón "+" en la esquina superior derecha
3. Selecciona "New repository"
4. Nombra tu repositorio (ej: `bdns-scanner`)
5. Hazlo **público** o **privado** (ambos funcionan con Streamlit Community Cloud)
6. NO inicialices con README, .gitignore ni licencia (ya los tienes)
7. Crea el repositorio

### 1.3 Subir tu Código a GitHub

```bash
git remote add origin https://github.com/TU_USUARIO/bdns-scanner.git
git branch -M main
git push -u origin main
```

## Paso 2: Preparar Archivos de Datos

### Opción A: Incluir datos en el repositorio (para datasets pequeños)

Si tus archivos Parquet son pequeños (<100MB total):

```bash
git add data/*.parquet
git commit -m "Add data files"
git push
```

### Opción B: Usar Git LFS (Large File Storage) para archivos grandes

Si tus archivos son grandes:

1. Instala Git LFS: [git-lfs.github.com](https://git-lfs.github.com/)

2. Configura Git LFS:
```bash
git lfs install
git lfs track "data/*.parquet"
git add .gitattributes
git add data/*.parquet
git commit -m "Add large data files with LFS"
git push
```

### Opción C: Cargar datos desde una URL externa

Si los datos son muy grandes, considera:
- Subir los archivos Parquet a Google Drive, Dropbox, o AWS S3
- Modificar `streamlit_app.py` para descargar los datos desde la URL

## Paso 3: Desplegar en Streamlit Community Cloud

### 3.1 Crear Cuenta en Streamlit Community Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Haz clic en "Sign in with GitHub"
3. Autoriza Streamlit para acceder a tu cuenta de GitHub

### 3.2 Desplegar la Aplicación

1. En Streamlit Community Cloud, haz clic en "New app"
2. Selecciona tu repositorio de GitHub
3. Configura:
   - **Repository**: Tu repositorio (ej: `TU_USUARIO/bdns-scanner`)
   - **Branch**: `main` (o la rama que estés usando)
   - **Main file path**: `streamlit_app.py`
4. Haz clic en "Deploy!"

### 3.3 Espera el Despliegue

- La aplicación tardará unos minutos en desplegarse por primera vez
- Streamlit instalará automáticamente las dependencias del `requirements.txt`
- Una vez completado, obtendrás una URL pública (ej: `https://tu-usuario-bdns-scanner.streamlit.app`)

## Paso 4: Actualizar la Aplicación

Cada vez que hagas cambios:

```bash
git add .
git commit -m "Descripción de los cambios"
git push
```

La aplicación se actualizará automáticamente en Streamlit Community Cloud.

## Características de Streamlit Community Cloud (Gratis)

✅ **Completamente gratis**
✅ **Hosting ilimitado de apps públicas**
✅ **SSL/HTTPS automático**
✅ **Actualizaciones automáticas desde GitHub**
✅ **1 GB de RAM por app**
✅ **1 CPU compartida**
✅ **Dominio personalizado disponible**

## Limitaciones

⚠️ La app se "duerme" después de 7 días de inactividad
⚠️ Recursos limitados (1GB RAM, 1 CPU)
⚠️ Tiempo de ejecución máximo de 10 minutos por solicitud

## Solución de Problemas

### Error: "Requirements file not found"
- Asegúrate de que `requirements.txt` está en la raíz del repositorio

### Error: "Module not found"
- Verifica que todas las dependencias estén en `requirements.txt`
- Asegúrate de que los nombres y versiones sean correctos

### Error: "Data files not found"
- Si usas datos locales, asegúrate de que la carpeta `data/` esté en el repositorio
- Verifica que `.gitignore` NO esté excluyendo los archivos `.parquet`

### La app es muy lenta
- Considera reducir el tamaño de los datos
- Usa `@st.cache_data` para cachear operaciones costosas (ya implementado)
- Optimiza las consultas y filtros

### La app se queda sin memoria
- Reduce el tamaño del dataset
- Filtra los datos antes de cargarlos
- Considera dividir los datos en múltiples archivos más pequeños

## Configuración Avanzada (Opcional)

### Configurar Secretos

Para datos sensibles (API keys, contraseñas):

1. En Streamlit Community Cloud, ve a tu app
2. Haz clic en "Settings" > "Secrets"
3. Agrega secretos en formato TOML:

```toml
[secrets]
api_key = "tu_api_key_aqui"
```

4. Accede en el código:
```python
import streamlit as st
api_key = st.secrets["secrets"]["api_key"]
```

### Personalizar la Configuración

Crea `.streamlit/config.toml` en tu repositorio:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
```

## Recursos Adicionales

- [Documentación de Streamlit](https://docs.streamlit.io)
- [Streamlit Community Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Foro de Streamlit](https://discuss.streamlit.io)
- [Galería de Apps](https://streamlit.io/gallery)

## URL de tu Aplicación

Una vez desplegada, tu aplicación estará disponible en:
```
https://[tu-usuario]-[nombre-repo]-[hash].streamlit.app
```

Por ejemplo:
```
https://svrub-bdns-scanner-abc123.streamlit.app
```

¡Disfruta de tu aplicación en la nube completamente gratis! 🎉

