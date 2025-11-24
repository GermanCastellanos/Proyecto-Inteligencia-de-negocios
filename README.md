# Dashboard de Predicción ICFES

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red?style=flat&logo=streamlit)
![License](https://img.shields.io/github/license/GermanCastellanos/Proyecto-Inteligencia-de-negocios)

Proyecto desarrollado para el análisis, visualización y recomendación de carreras basado en datos reales de resultados ICFES. El dashboard integra clustering, modelado ARIMA y un sistema de recomendaciones inteligentes vía API.

---

## Características principales

- Carga y procesamiento de más de 135,000 registros reales
- Visualización interactiva de clustering KMeans y análisis PCA
- Predicción temporal con ARIMA para promedios por área
- Sistema de recomendaciones: CRUD completo vía REST API para perfiles de estudiantes y sugerencia automática de carrera profesional
- Análisis estadístico general y exploración de correlaciones
- Interfaz simple, moderna y personalizable (sin emojis)

---

## Tabla de contenidos

- [Instalación](#instalación)
- [Ejecución rápida](#ejecución-rápida)
- [Estructura principal](#estructura-principal)
- [Funcionalidad por módulo](#funcionalidad-por-módulo)
- [API de recomendaciones](#api-de-recomendaciones)
- [Licencia](#licencia)
- [Autor y contacto](#autor-y-contacto)

---

## Instalación

1. **Clona el repositorio**

```bash
git clone https://github.com/GermanCastellanos/Proyecto-Inteligencia-de-negocios.git
cd Proyecto-Inteligencia-de-negocios
```

2. **Instala dependencias**

```bash
pip install -r requirements.txt
```

3. **Genera la base de datos ejecutando el notebook**

Abre y ejecuta el archivo `Proyecto_ICFES.ipynb` (o el notebook correspondiente) desde Jupyter Notebook, JupyterLab o Visual Studio Code.
Esto creará el archivo `datos_icfes_filtrado.csv` necesario para el funcionamiento del dashboard y la API.
Asegúrate de que el archivo quede guardado en la raíz del proyecto.

---

## Ejecución rápida

**1. Inicia la API (en una terminal):**

```bash
python main.py
```

La API debe correr por defecto en `http://localhost:8000`.

**2. Inicia el dashboard (en otra terminal):**

```bash
streamlit run app.py
```

Accede a `http://localhost:8501` desde tu navegador.

---

## Estructura principal

```
Proyecto-Inteligencia-de-negocios/
│
├── app.py                      # Dashboard principal (sin emojis)
├── main.py                     # API de recomendaciones y estudiantes
├── config.py                   # Configuración general
├── requirements.txt            # Dependencias
│
├── datos_icfes_filtrado.csv    # Archivo de datos (generado por el notebook)
├── Proyecto_ICFES.ipynb        # Notebook para generación de datos
├── pages/
│   ├── clustering.py           # Página de clustering interactivo
│   ├── arima.py                # Página de predicción ARIMA
│   ├── recomendaciones.py      # CRUD + recomendación de carreras
│   └── estadisticas.py         # Estadísticas descriptivas y gráficas
│
└── (otros archivos de apoyo)
```

---

## Funcionalidad por módulo

**app.py:**
Controla la navegación, el layout y retira menús repetidos. Título personalizable y mayor tamaño usando HTML.

**clustering.py:**
Visualiza clusters con KMeans y PCA, incluye gráfico de dispersión, barras y tabla.

**arima.py:**
Predicción y modelado de series temporales por área (RMSE, MAE, MSE y visualización de forecast).

**recomendaciones.py:**
Permite crear, consultar, borrar y listar estudiantes. Para cada uno, recomienda dos carreras según su perfil.

**estadisticas.py:**
Presenta distribución, estadística descriptiva y matriz de correlación de las áreas ICFES.

---

## API de recomendaciones

La API (FastAPI) permite:

- Crear/actualizar estudiante con sus puntajes
- Obtener recomendación de carreras
- Listar y consultar estudiantes
- Eliminar estudiante

Endpoints disponibles:

```
POST   /predict
GET    /recommendation/{id}
GET    /students
GET    /student/{id}
DELETE /student/{id}
```

Consulta el dashboard en la sección "Recomendaciones" para usar todas estas funciones desde la interfaz.

---

## Licencia

Este proyecto utiliza la MIT License.

---

## Autor y contacto

Desarrollado por German Castellanos.

Si encuentras bugs, tienes sugerencias o quieres colaborar, abre un issue o envía un PR.

---

¡Gracias por visitar y probar el Dashboard ICFES!
