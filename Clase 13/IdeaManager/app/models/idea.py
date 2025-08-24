# idea_manager/idea.py
from datetime import datetime

class Idea:
    def __init__(self, titulo, descripcion, categoria="General"):
        self.titulo = titulo
        self.descripcion = descripcion
        self.categoria = categoria
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.estado = "Nueva"  # Nueva, En Desarrollo, Completada, Archivada
        self.tags = []
        self.recursos = []  # Enlaces, archivos relacionados, etc.
        self.notas = ""
        
    def __str__(self):
        return f"Idea: {self.titulo} ({self.categoria}) - {self.estado}"
        
    def agregar_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            
    def agregar_recurso(self, recurso):
        self.recursos.append(recurso)
        
    def agregar_nota(self, nota):
        self.notas += f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {nota}\n"
        
    def cambiar_estado(self, nuevo_estado):
        estados_validos = ["Nueva", "En Desarrollo", "Completada", "Archivada"]
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
            return True
        return False