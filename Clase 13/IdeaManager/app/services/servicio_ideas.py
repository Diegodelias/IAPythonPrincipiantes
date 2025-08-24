import json
import os
from datetime import datetime
from ..models.idea import Idea
from app.core.database_manager import DatabaseManager
from app.core.config import DATA_ACCESS_TYPE, JSON_BACKUP_FILE
from data.sql import SQLFactory
from data.orm.factory import ORMFactory

class ServicioIdeas:
    """Clase para gestionar el banco de ideas"""
    
    def __init__(self, factory_type=None):
        """
        Inicializa el servicio de ideas con el tipo de factory especificado
        
        Args:
            factory_type (str, optional): Tipo de factory a utilizar ('sql' o 'orm').
                                         Si no se especifica, se usa el valor de configuración.
        """
        # Usar el tipo de factory especificado o el valor de configuración
        factory_type = factory_type or DATA_ACCESS_TYPE
        
        # Seleccionar el factory adecuado según el tipo
        if factory_type.lower() == "orm":
            factory = ORMFactory()
        else:  # Por defecto, usar SQL
            factory = SQLFactory()
            
        # Inicializar el gestor de base de datos con el factory seleccionado
        self.db_manager = DatabaseManager(factory)
        
        # TODO: Implementar múltiples repositorios para cada entidad del dominio
        # - Inicializar repositorios para tags y recursos además de ideas
        # - Ejemplo:
        #   self.ideas_repo = self.db_manager.get_repository("ideas")
        #   self.tags_repo = self.db_manager.get_repository("tags")
        #   self.recursos_repo = self.db_manager.get_repository("recursos")
        # - Refactorizar métodos para usar los repositorios específicos
        
        self.ideas_repo = self.db_manager.get_repository("ideas")
        self.nombre_archivo = JSON_BACKUP_FILE  # Usar el valor de configuración
    
    def _cargar_ideas(self):
        """Carga las ideas desde el archivo JSON (mantener para compatibilidad)"""
        if not os.path.exists(self.nombre_archivo):
            return []
        
        try:
            with open(self.nombre_archivo, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            # Si hay un error al decodificar el JSON, devolver una lista vacía
            return []
    
    def _guardar_ideas(self, ideas):
        """Guarda las ideas en el archivo JSON (mantener para compatibilidad)"""
        with open(self.nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(ideas, archivo, indent=4, ensure_ascii=False)
    
    def agregar_idea(self, idea):
        """Agrega una nueva idea al banco de ideas"""
        # Convertir la idea a un diccionario
        idea_dict = {
            'titulo': idea.titulo,
            'descripcion': idea.descripcion,
            'categoria': idea.categoria,
            'fecha_creacion': idea.fecha_creacion,
            'estado': idea.estado
        }
        
        # Usar el repositorio para crear la idea
        tags = idea.tags if hasattr(idea, 'tags') and idea.tags else []
        recursos = idea.recursos if hasattr(idea, 'recursos') and idea.recursos else []
        
        idea_id = self.ideas_repo.create_idea(idea_dict, tags, recursos)
        return idea_id is not None
    
    def listar_ideas(self):
        """Devuelve una lista de todas las ideas"""
        return self.ideas_repo.find_all()
    
    def obtener_idea(self, indice):
        """Obtiene una idea específica por su índice"""
        # Nota: Este método necesita ser adaptado para trabajar con IDs en lugar de índices
        # Por ahora, mantenemos la compatibilidad con el código existente
        ideas = self.listar_ideas()
        
        if ideas and 0 <= indice < len(ideas):
            return ideas[indice]
        else:
            return None
    
    def actualizar_idea(self, indice, idea_actualizada):
        """Actualiza una idea existente"""
        # Este método necesita ser adaptado para trabajar con el repositorio
        # Por ahora, mantenemos la compatibilidad con el código existente
        ideas = self._cargar_ideas()
        
        if 0 <= indice < len(ideas):
            ideas[indice] = idea_actualizada
            self._guardar_ideas(ideas)
            return True
        else:
            return False
    
    def eliminar_idea(self, indice):
        """Elimina una idea por su índice"""
        # Este método necesita ser adaptado para trabajar con el repositorio
        # Por ahora, mantenemos la compatibilidad con el código existente
        ideas = self._cargar_ideas()
        
        if 0 <= indice < len(ideas):
            ideas.pop(indice)
            self._guardar_ideas(ideas)
            return True
        else:
            return False
    
    def buscar_ideas(self, termino):
        """Busca ideas que contengan el término en título, descripción o tags"""
        # Este método necesita ser adaptado para trabajar con el repositorio
        # Por ahora, implementamos una búsqueda en memoria con los datos del repositorio
        ideas = self.listar_ideas()
        resultados = []
        
        termino = termino.lower()
        
        for idea in ideas:
            titulo = idea.get('titulo', '').lower()
            descripcion = idea.get('descripcion', '').lower()
            tags = idea.get('tags', [])
            
            if (termino in titulo or 
                termino in descripcion or 
                any(termino in tag.lower() for tag in tags if isinstance(tags, list))):
                resultados.append(idea)
        
        return resultados
    
    def filtrar_por_categoria(self, categoria):
        """Filtra ideas por categoría"""
        # Este método necesita ser adaptado para trabajar con el repositorio
        # Por ahora, implementamos un filtro en memoria con los datos del repositorio
        ideas = self.listar_ideas()
        return [idea for idea in ideas if idea.get('categoria', '').lower() == categoria.lower()]
    
    def filtrar_por_estado(self, estado):
        """Filtra ideas por estado"""
        # Este método necesita ser adaptado para trabajar con el repositorio
        # Por ahora, implementamos un filtro en memoria con los datos del repositorio
        ideas = self.listar_ideas()
        return [idea for idea in ideas if idea.get('estado') == estado]
    
    def eliminar_archivo(self):
        """Elimina el archivo de banco de ideas"""
        # Este método ya no es necesario con el repositorio, pero lo mantenemos por compatibilidad
        if os.path.exists(self.nombre_archivo):
            os.remove(self.nombre_archivo)
            return True
        else:
            return False
    
    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self.db_manager, 'factory') and hasattr(self.db_manager.factory, 'close_connection'):
            self.db_manager.factory.close_connection()
            return True
        return False