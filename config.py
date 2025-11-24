# config.py
"""
Archivo de configuración centralizado
Aquí cambias colores, mensajes, rutas, etc.
"""

# ==================== RUTAS ====================
CSV_FILE = 'datos_icfes_filtrado.csv'
FAVICON = "📊"

# ==================== CONFIGURACIÓN STREAMLIT ====================
PAGE_CONFIG = {
    "page_title": "Dashboard ICFES - Análisis y Predicción",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ==================== COLORES ====================
COLORS = {
    "primary": "#1f77b4",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c",
    "info": "#3498db"
}

# ==================== CLUSTERING ====================
CLUSTERING = {
    "sample_size": 1000,
    "k_min": 2,
    "k_max": 10,
    "k_default": 4,
    "random_state": 42,
    "n_init": 10
}

# ==================== ARIMA ====================
ARIMA = {
    "order": (1, 1, 1),
    "test_size": 3,
    "min_periods": 5,
    "random_state": 42
}

# ==================== RECOMENDACIONES ====================
AREA_MAPPING = {
    'PUNT_INGLES': 'Humanidades',
    'PUNT_MATEMATICAS': 'STEM',
    'PUNT_SOCIALES_CIUDADANAS': 'Ciencias Sociales',
    'PUNT_C_NATURALES': 'STEM',
    'PUNT_LECTURA_CRITICA': 'Humanidades',
    'PUNT_GLOBAL': 'Multidisciplinario'
}

FACULTY_PROGRAMS = {
    'STEM': [
        'Ingeniería (Sistemas, Civil, Mecánica)',
        'Ciencias de la Computación',
        'Matemáticas Aplicadas',
        'Biología / Bioquímica'
    ],
    'Ciencias Sociales': [
        'Administración Pública',
        'Economía / Contabilidad',
        'Derecho',
        'Sociología / Antropología'
    ],
    'Humanidades': [
        'Filosofía / Literatura',
        'Lingüística / Traducción',
        'Historia / Arqueología',
        'Comunicación Social'
    ],
    'Salud': [
        'Medicina',
        'Enfermería',
        'Psicología',
        'Salud Pública'
    ],
    'Artes': [
        'Artes Plásticas',
        'Música / Conservatorio',
        'Cine / Audiovisuales',
        'Diseño Gráfico'
    ],
    'Multidisciplinario': [
        'Ingeniería Industrial',
        'Gestión Ambiental',
        'Administración de Empresas',
        'Análisis de Sistemas'
    ]
}

# ==================== MENSAJES ====================
MESSAGES = {
    "title": "📊 Dashboard de Predicción ICFES",
    "subtitle": "Sistema de Análisis y Predicción de Puntuaciones ICFES",
    "description": """
    - Análisis de clustering de estudiantes
    - Predicción temporal de puntuaciones con ARIMA
    - Recomendaciones de carrera basadas en datos
    """
}
