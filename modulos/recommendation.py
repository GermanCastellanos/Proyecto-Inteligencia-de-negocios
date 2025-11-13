# recommendation.py
"""
Módulo de Recomendación de Áreas de Estudio
Basado en puntuaciones por área del estudiante (escala 0-100)
Genera 2 recomendaciones de carreras/facultades según desempeño
"""

import numpy as np
import pandas as pd


class RecommendationEngine:
    """Engine para recomendar áreas de estudio según puntuaciones"""
    
    def __init__(self):
        # Mapeo de áreas a categorías de facultades
        self.area_to_category = {
            'PUNT_INGLES': 'Humanidades',
            'PUNT_MATEMATICAS': 'STEM',
            'PUNT_SOCIALES_CIUDADANAS': 'Ciencias Sociales',
            'PUNT_C_NATURALES': 'STEM',
            'PUNT_LECTURA_CRITICA': 'Humanidades'
        }
        
        # Facultades por categoría
        self.category_to_programs = {
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
            ]
        }
        
        # Áreas de estudio normalizadas
        self.areas_list = [
            'PUNT_INGLES',
            'PUNT_MATEMATICAS',
            'PUNT_SOCIALES_CIUDADANAS',
            'PUNT_C_NATURALES',
            'PUNT_LECTURA_CRITICA'
        ]
    
    def get_recommendations(self, scores_dict):
        """
        Generar recomendaciones para un estudiante basadas en sus puntuaciones
        
        Entrada:
            scores_dict: diccionario con estructura
            {
                'PUNT_INGLES': 75,
                'PUNT_MATEMATICAS': 88,
                'PUNT_SOCIALES_CIUDADANAS': 70,
                'PUNT_C_NATURALES': 85,
                'PUNT_LECTURA_CRITICA': 92
            }
        
        Salida:
            diccionario con recomendaciones
        """
        
        # Validar que todas las áreas estén presentes
        for area in self.areas_list:
            if area not in scores_dict:
                raise ValueError(f"Falta el área: {area}")
        
        # Obtener top 2 áreas con mayor puntuación
        top_2_areas = self._get_top_areas(scores_dict, top_n=2)
        
        # Mapear áreas a categorías
        top_categories = [self.area_to_category[area] for area, score in top_2_areas]
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(top_2_areas, top_categories)
        
        return {
            'estudiante_puntuaciones': scores_dict,
            'top_areas': [
                {
                    'area': area.replace('PUNT_', ''),
                    'puntuacion': float(score),
                    'categoria': self.area_to_category[area]
                }
                for area, score in top_2_areas
            ],
            'recomendaciones': recommendations
        }
    
    def _get_top_areas(self, scores_dict, top_n=2):
        """Extraer top N áreas por puntuación"""
        # Crear lista de tuplas (área, puntuación)
        areas_scores = [(area, scores_dict[area]) for area in self.areas_list]
        # Ordenar por puntuación descendente
        sorted_areas = sorted(areas_scores, key=lambda x: x[1], reverse=True)
        # Retornar top N
        return sorted_areas[:top_n]
    
    def _generate_recommendations(self, top_areas, categories):
        """
        Generar 2 recomendaciones basadas en áreas top y sus categorías
        
        Lógica:
        - Si ambas top áreas pertenecen a la misma categoría: 
          generar 2 recomendaciones de esa categoría
        - Si pertenecen a categorías diferentes:
          1ra recomendación: categoría del área top 1
          2da recomendación: categoría del área top 2
        """
        recommendations = []
        
        if categories[0] == categories[1]:
            # Ambas áreas en la misma categoría
            category = categories[0]
            programs = self.category_to_programs.get(category, [])
            
            if len(programs) >= 2:
                recommendations.append({
                    'posicion': 1,
                    'carrera': programs[0],
                    'categoria': category,
                    'razon': f"Excelente desempeño en {top_areas[0][0].replace('PUNT_', '')} ({top_areas[0][1]:.0f}/100)",
                    'relevancia': round(min(top_areas[0][1] / 100, 1.0), 2)
                })
                recommendations.append({
                    'posicion': 2,
                    'carrera': programs[1],
                    'categoria': category,
                    'razon': f"Fuerte desempeño en {top_areas[1][0].replace('PUNT_', '')} ({top_areas[1][1]:.0f}/100)",
                    'relevancia': round(min(top_areas[1][1] / 100, 1.0), 2)
                })
            else:
                # Generar 1-2 recomendaciones si hay pocos programas
                for i, program in enumerate(programs[:2]):
                    recommendations.append({
                        'posicion': i + 1,
                        'carrera': program,
                        'categoria': category,
                        'razon': f"Desempeño destacado en {category}",
                        'relevancia': round(min((top_areas[0][1] + top_areas[1][1]) / 200, 1.0), 2)
                    })
        else:
            # Categorías diferentes
            for i, (area, score) in enumerate(top_areas):
                category = categories[i]
                programs = self.category_to_programs.get(category, [])
                
                if programs:
                    recommendations.append({
                        'posicion': i + 1,
                        'carrera': programs[0],
                        'categoria': category,
                        'razon': f"Fuerte desempeño en {area.replace('PUNT_', '')} ({score:.0f}/100)",
                        'relevancia': round(min(score / 100, 1.0), 2)
                    })
        
        return recommendations
    
    def get_recommendations_batch(self, df):
        """
        Generar recomendaciones para múltiples estudiantes
        
        Entrada:
            df: DataFrame con columnas [PUNT_INGLES, PUNT_MATEMATICAS, PUNT_SOCIALES_CIUDADANAS, PUNT_C_NATURALES, PUNT_LECTURA_CRITICA]
        
        Salida:
            lista de diccionarios con recomendaciones por estudiante
        """
        results = []
        
        for idx, row in df.iterrows():
            scores_dict = {
                'PUNT_INGLES': row['PUNT_INGLES'],
                'PUNT_MATEMATICAS': row['PUNT_MATEMATICAS'],
                'PUNT_SOCIALES_CIUDADANAS': row['PUNT_SOCIALES_CIUDADANAS'],
                'PUNT_C_NATURALES': row['PUNT_C_NATURALES'],
                'PUNT_LECTURA_CRITICA': row['PUNT_LECTURA_CRITICA']
            }
            
            try:
                rec = self.get_recommendations(scores_dict)
                results.append(rec)
            except Exception as e:
                print(f"Error procesando fila {idx}: {e}")
        
        return results
    
    def print_recommendation(self, recommendation):
        """Imprimir recomendación de forma legible"""
        print(f"\n{'='*70}")
        print("RECOMENDACIÓN DE ÁREAS DE ESTUDIO")
        print('='*70)
        
        print(f"\n📊 PUNTUACIONES DEL ESTUDIANTE:")
        for area, score in recommendation['estudiante_puntuaciones'].items():
            print(f"   {area.replace('PUNT_', '')}: {score:.0f}/100")
        
        print(f"\n🎯 ÁREAS TOP:")
        for top in recommendation['top_areas']:
            print(f"   {top['area']}: {top['puntuacion']:.0f}/100 → Categoría: {top['categoria']}")
        
        print(f"\n💼 RECOMENDACIONES:")
        for rec in recommendation['recomendaciones']:
            print(f"\n   Opción {rec['posicion']}: {rec['carrera']}")
            print(f"   Categoría: {rec['categoria']}")
            print(f"   Razón: {rec['razon']}")
            print(f"   Relevancia: {rec['relevancia']*100:.0f}%")
        
        print(f"\n{'='*70}\n")
