from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modulos'))
from recommendation import RecommendationEngine

# ==================== CONFIGURACIÓN ====================

app = FastAPI(
    title="API de Recomendación ICFES",
    description="Sistema de recomendación de áreas de estudio basado en puntuaciones ICFES",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELOS ====================

class ScoresInput(BaseModel):
    """Modelo de entrada: puntuaciones del estudiante"""
    estudiante_id: str = Field(..., description="ID del estudiante")
    punt_ingles: float = Field(..., ge=0, le=100, description="Puntuación Inglés (0-100)")
    punt_matematicas: float = Field(..., ge=0, le=100, description="Puntuación Matemáticas (0-100)")
    punt_sociales_ciudadanas: float = Field(..., ge=0, le=100, description="Puntuación Sociales Ciudadanas (0-100)")
    punt_c_naturales: float = Field(..., ge=0, le=100, description="Puntuación Ciencias Naturales (0-100)")
    punt_lectura_critica: float = Field(..., ge=0, le=100, description="Puntuación Lectura Crítica (0-100)")
    
    class Config:
        schema_extra = {
            "example": {
                "estudiante_id": "EST001",
                "punt_ingles": 75,
                "punt_matematicas": 88,
                "punt_sociales_ciudadanas": 70,
                "punt_c_naturales": 85,
                "punt_lectura_critica": 92
            }
        }


class UploadResponse(BaseModel):
    """Respuesta de carga de datos"""
    mensaje: str
    estudiante_id: str
    timestamp: str
    estado: str


class TopArea(BaseModel):
    """Área top con puntuación"""
    area: str
    puntuacion: float
    categoria: str


class Recomendacion(BaseModel):
    """Recomendación de carrera"""
    posicion: int
    carrera: str
    categoria: str
    razon: str
    relevancia: float


class RecommendationResponse(BaseModel):
    """Respuesta de recomendación"""
    estudiante_id: str
    timestamp: str
    puntuaciones: Dict[str, float]
    top_areas: List[TopArea]
    recomendaciones: List[Recomendacion]
    mensaje: str


class HealthResponse(BaseModel):
    """Respuesta de salud"""
    status: str
    servicio: str
    version: str


# ==================== ALMACENAMIENTO ====================

# Almacenar datos de estudiantes (en producción usar DB)
estudiantes_data: Dict[str, Dict] = {}

# Inicializar motor
try:
    recommender = RecommendationEngine()
    print("✅ Motor de recomendación inicializado")
except Exception as e:
    print(f"❌ Error inicializando motor: {e}")
    recommender = None

# ==================== ENDPOINTS ====================

@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health_check():
    """Verificar estado del servicio"""
    return HealthResponse(
        status="healthy",
        servicio="API de Recomendación ICFES",
        version="1.0.0"
    )


@app.post("/predict", response_model=UploadResponse, tags=["Carga de Datos"])
async def upload_scores(scores: ScoresInput):
    """
    Cargar puntuaciones de un estudiante
    
    Solo guarda los datos. No devuelve recomendaciones.
    
    Args:
        scores: Puntuaciones ICFES del estudiante
    
    Returns:
        Confirmación de carga
    
    Ejemplo:
        ```json
        {
            "estudiante_id": "EST001",
            "punt_ingles": 75,
            "punt_matematicas": 88,
            "punt_sociales_ciudadanas": 70,
            "punt_c_naturales": 85,
            "punt_lectura_critica": 92
        }
        ```
    """
    try:
        # Guardar datos
        estudiantes_data[scores.estudiante_id] = {
            'PUNT_INGLES': scores.punt_ingles,
            'PUNT_MATEMATICAS': scores.punt_matematicas,
            'PUNT_SOCIALES_CIUDADANAS': scores.punt_sociales_ciudadanas,
            'PUNT_C_NATURALES': scores.punt_c_naturales,
            'PUNT_LECTURA_CRITICA': scores.punt_lectura_critica,
            'timestamp_guardado': datetime.now().isoformat()
        }
        
        return UploadResponse(
            mensaje=f"Datos del estudiante {scores.estudiante_id} guardados exitosamente",
            estudiante_id=scores.estudiante_id,
            timestamp=datetime.now().isoformat(),
            estado="guardado"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando datos: {str(e)}")


@app.get("/recommendation/{estudiante_id}", response_model=RecommendationResponse, tags=["Recomendaciones"])
async def get_recommendation(estudiante_id: str):
    """
    Obtener recomendaciones para un estudiante
    
    Recupera los datos guardados del estudiante y genera recomendaciones.
    
    Args:
        estudiante_id: ID del estudiante (path parameter)
    
    Returns:
        Recomendaciones basadas en puntuaciones guardadas
    
    Ejemplo:
        GET /recommendation/EST001
    """
    if recommender is None:
        raise HTTPException(status_code=500, detail="Motor de recomendación no inicializado")
    
    # Verificar que el estudiante exista
    if estudiante_id not in estudiantes_data:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron datos para el estudiante {estudiante_id}"
        )
    
    try:
        # Obtener datos guardados
        scores_dict = estudiantes_data[estudiante_id].copy()
        timestamp_guardado = scores_dict.pop('timestamp_guardado')
        
        # Generar recomendaciones
        rec = recommender.get_recommendations(scores_dict)
        
        # Construir respuesta
        response = RecommendationResponse(
            estudiante_id=estudiante_id,
            timestamp=datetime.now().isoformat(),
            puntuaciones=scores_dict,
            top_areas=[TopArea(**top) for top in rec['top_areas']],
            recomendaciones=[Recomendacion(**rec_item) for rec_item in rec['recomendaciones']],
            mensaje="Recomendación generada exitosamente"
        )
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando recomendación: {str(e)}")


@app.get("/students", tags=["Consultas"])
async def list_students():
    """
    Listar todos los estudiantes cargados
    
    Returns:
        Lista de IDs de estudiantes y sus timestamps
    """
    return {
        "total_estudiantes": len(estudiantes_data),
        "estudiantes": [
            {
                "id": est_id,
                "timestamp_guardado": data.get('timestamp_guardado')
            }
            for est_id, data in estudiantes_data.items()
        ]
    }


@app.get("/student/{estudiante_id}", tags=["Consultas"])
async def get_student_data(estudiante_id: str):
    """
    Obtener datos guardados de un estudiante (sin recomendaciones)
    
    Args:
        estudiante_id: ID del estudiante
    
    Returns:
        Puntuaciones guardadas del estudiante
    """
    if estudiante_id not in estudiantes_data:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron datos para {estudiante_id}"
        )
    
    data = estudiantes_data[estudiante_id].copy()
    return {
        "estudiante_id": estudiante_id,
        "puntuaciones": {k: v for k, v in data.items() if k != 'timestamp_guardado'},
        "timestamp_guardado": data.get('timestamp_guardado')
    }


@app.delete("/student/{estudiante_id}", tags=["Gestión"])
async def delete_student(estudiante_id: str):
    """
    Eliminar datos de un estudiante
    
    Args:
        estudiante_id: ID del estudiante a eliminar
    """
    if estudiante_id not in estudiantes_data:
        raise HTTPException(
            status_code=404,
            detail=f"Estudiante {estudiante_id} no encontrado"
        )
    
    del estudiantes_data[estudiante_id]
    
    return {
        "mensaje": f"Datos del estudiante {estudiante_id} eliminados",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/stats", tags=["Estadísticas"])
async def get_statistics():
    """
    Obtener estadísticas del sistema
    
    Returns:
        Total de estudiantes cargados
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "total_estudiantes": len(estudiantes_data)
    }


@app.get("/", tags=["Info"])
async def root():
    """Información general de la API"""
    return {
        "nombre": "API de Recomendación ICFES",
        "version": "1.0.0",
        "descripcion": "Sistema de recomendación de áreas de estudio",
        "flujo": {
            "paso_1": "POST /upload → Guardar puntuaciones del estudiante",
            "paso_2": "GET /recommendation/{id} → Obtener recomendaciones"
        },
        "documentacion": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )