import gradio as gr
import json
import os
from datetime import datetime
from app.services.servicio_ideas import ServicioIdeas
from app.models.idea import Idea
from app.core.config import WEB_PORT, WEB_SHARE

class AppManagerIdeas:
    """Aplicación web para gestionar ideas usando Gradio"""
    
    def __init__(self):
        """Inicializa la aplicación web"""
        # Inicializar el servicio de ideas
        self.servicio = ServicioIdeas()
        
        # Crear la interfaz de Gradio
        self.demo = self._crear_interfaz()
    
    def _obtener_valor_seguro(self, diccionario, clave, valor_predeterminado=None):
        """Obtiene un valor de un diccionario de forma segura"""
        if diccionario and isinstance(diccionario, dict) and clave in diccionario:
            return diccionario[clave]
        return valor_predeterminado
    
    def _listar_ideas(self):
        """Lista todas las ideas disponibles"""
        try:
            print("DEBUG: _listar_ideas called")
            ideas = self.servicio.listar_ideas()
            print(f"DEBUG: Retrieved {len(ideas) if ideas else 0} ideas from database")
            
            if not ideas:
                print("DEBUG: No ideas found")
                return "No hay ideas disponibles."
            
            resultado = ""
            for i, idea in enumerate(ideas):
                titulo = self._obtener_valor_seguro(idea, 'titulo', 'Sin título')
                categoria = self._obtener_valor_seguro(idea, 'categoria', 'Sin categoría')
                estado = self._obtener_valor_seguro(idea, 'estado', 'Sin estado')
                
                resultado += f"{i+1}. {titulo} - {categoria} - {estado}\n"
            
            print(f"DEBUG: Returning result with {len(resultado)} characters")
            return resultado
        except Exception as e:
            print(f"ERROR in _listar_ideas: {str(e)}")
            return f"Error al listar ideas: {str(e)}"
    
    def _ver_detalle_idea(self, indice_str):
        """Muestra el detalle de una idea específica"""
        try:
            indice = int(indice_str) - 1
            if indice < 0:
                return "El índice debe ser un número positivo."
        except ValueError:
            return "Por favor, ingresa un número válido."
        
        ideas = self.servicio.listar_ideas()
        if not ideas or indice >= len(ideas):
            return "Idea no encontrada."
        
        idea = ideas[indice]
        
        titulo = self._obtener_valor_seguro(idea, 'titulo', 'Sin título')
        descripcion = self._obtener_valor_seguro(idea, 'descripcion', 'Sin descripción')
        categoria = self._obtener_valor_seguro(idea, 'categoria', 'Sin categoría')
        fecha = self._obtener_valor_seguro(idea, 'fecha_creacion', 'Fecha desconocida')
        estado = self._obtener_valor_seguro(idea, 'estado', 'Sin estado')
        tags = self._obtener_valor_seguro(idea, 'tags', [])
        recursos = self._obtener_valor_seguro(idea, 'recursos', [])
        
        resultado = f"# {titulo}\n\n"
        resultado += f"**Categoría:** {categoria}\n"
        resultado += f"**Estado:** {estado}\n"
        resultado += f"**Fecha de creación:** {fecha}\n\n"
        resultado += f"## Descripción\n{descripcion}\n\n"
        
        if tags:
            resultado += "## Tags\n"
            for tag in tags:
                resultado += f"- {tag}\n"
            resultado += "\n"
        
        if recursos:
            resultado += "## Recursos\n"
            for recurso in recursos:
                resultado += f"- {recurso}\n"
        
        return resultado
    
    def _agregar_idea(self, titulo, descripcion, categoria, estado, tags, recursos):
        """Agrega una nueva idea"""
        if not titulo:
            return "El título es obligatorio."
        
        # Crear objeto Idea
        nueva_idea = Idea(titulo, descripcion, categoria)
        nueva_idea.estado = estado
        
        # Agregar tags
        if tags:
            for tag in tags.split(','):
                tag = tag.strip()
                if tag:
                    nueva_idea.agregar_tag(tag)
        
        # Agregar recursos
        if recursos:
            for recurso in recursos.split(','):
                recurso = recurso.strip()
                if recurso:
                    nueva_idea.agregar_recurso(recurso)
        
        # Guardar la idea
        resultado = self.servicio.agregar_idea(nueva_idea)
        
        if resultado:
            return "Idea agregada correctamente."
        else:
            return "Error al agregar la idea."
    
    def _buscar_ideas(self, termino):
        """Busca ideas que contengan el término especificado"""
        if not termino:
            return "Por favor, ingresa un término de búsqueda."
        
        ideas = self.servicio.buscar_ideas(termino)
        
        if not ideas:
            return f"No se encontraron ideas que contengan '{termino}'."
        
        resultado = f"Resultados para '{termino}':\n\n"
        for i, idea in enumerate(ideas):
            titulo = self._obtener_valor_seguro(idea, 'titulo', 'Sin título')
            categoria = self._obtener_valor_seguro(idea, 'categoria', 'Sin categoría')
            
            resultado += f"{i+1}. {titulo} - {categoria}\n"
        
        return resultado
    
    def _filtrar_por_categoria(self, categoria):
        """Filtra ideas por categoría"""
        if not categoria:
            return "Por favor, selecciona una categoría."
        
        ideas = self.servicio.filtrar_por_categoria(categoria)
        
        if not ideas:
            return f"No se encontraron ideas en la categoría '{categoria}'."
        
        resultado = f"Ideas en la categoría '{categoria}':\n\n"
        for i, idea in enumerate(ideas):
            titulo = self._obtener_valor_seguro(idea, 'titulo', 'Sin título')
            estado = self._obtener_valor_seguro(idea, 'estado', 'Sin estado')
            
            resultado += f"{i+1}. {titulo} - {estado}\n"
        
        return resultado
    
    def _filtrar_por_estado(self, estado):
        """Filtra ideas por estado"""
        if not estado:
            return "Por favor, selecciona un estado."
        
        ideas = self.servicio.filtrar_por_estado(estado)
        
        if not ideas:
            return f"No se encontraron ideas con el estado '{estado}'."
        
        resultado = f"Ideas con el estado '{estado}':\n\n"
        for i, idea in enumerate(ideas):
            titulo = self._obtener_valor_seguro(idea, 'titulo', 'Sin título')
            categoria = self._obtener_valor_seguro(idea, 'categoria', 'Sin categoría')
            
            resultado += f"{i+1}. {titulo} - {categoria}\n"
        
        return resultado
    
    def _crear_interfaz(self):
        """Crea la interfaz de usuario con Gradio"""
        with gr.Blocks(title="Gestor de Ideas") as demo:
            gr.Markdown("# Gestor de Ideas")
            
            with gr.Tab("Listar Ideas"):
                with gr.Row():
                    listar_btn = gr.Button("Listar todas las ideas")
                    
                    resultado_listar = gr.Textbox(label="Resultado", lines=10)
                    print( resultado_listar)
                
                listar_btn.click(self._listar_ideas, inputs=[], outputs=[resultado_listar])
            
            with gr.Tab("Ver Detalle"):
                with gr.Row():
                    indice_input = gr.Textbox(label="Índice de la idea")
                    ver_btn = gr.Button("Ver detalle")
                
                resultado_ver = gr.Markdown(label="Detalle de la idea")
                
                ver_btn.click(self._ver_detalle_idea, inputs=[indice_input], outputs=[resultado_ver])
            
            with gr.Tab("Agregar Idea"):
                titulo_input = gr.Textbox(label="Título")
                descripcion_input = gr.Textbox(label="Descripción", lines=5)
                categoria_input = gr.Dropdown(
                    ["Desarrollo", "Diseño", "Marketing", "Producto", "Otro"],
                    label="Categoría"
                )
                estado_input = gr.Dropdown(
                    ["Nueva", "En progreso", "Completada", "Archivada"],
                    label="Estado"
                )
                tags_input = gr.Textbox(label="Tags (separados por comas)")
                recursos_input = gr.Textbox(label="Recursos (separados por comas)")
                
                agregar_btn = gr.Button("Agregar idea")
                resultado_agregar = gr.Textbox(label="Resultado")
                
                agregar_btn.click(
                    self._agregar_idea,
                    inputs=[
                        titulo_input, descripcion_input, categoria_input,
                        estado_input, tags_input, recursos_input
                    ],
                    outputs=[resultado_agregar]
                )
            
            with gr.Tab("Buscar"):
                termino_input = gr.Textbox(label="Término de búsqueda")
                buscar_btn = gr.Button("Buscar")
                resultado_buscar = gr.Textbox(label="Resultados", lines=10)
                
                buscar_btn.click(self._buscar_ideas, inputs=[termino_input], outputs=[resultado_buscar])
            
            with gr.Tab("Filtrar"):
                with gr.Row():
                    with gr.Column():
                        categoria_filtro = gr.Dropdown(
                            ["Desarrollo", "Diseño", "Marketing", "Producto", "Otro"],
                            label="Filtrar por categoría"
                        )
                        filtrar_cat_btn = gr.Button("Filtrar por categoría")
                    
                    with gr.Column():
                        estado_filtro = gr.Dropdown(
                            ["Nueva", "En progreso", "Completada", "Archivada"],
                            label="Filtrar por estado"
                        )
                        filtrar_est_btn = gr.Button("Filtrar por estado")
                
                resultado_filtrar = gr.Textbox(label="Resultados", lines=10)
                
                filtrar_cat_btn.click(
                    self._filtrar_por_categoria,
                    inputs=[categoria_filtro],
                    outputs=[resultado_filtrar]
                )
                
                filtrar_est_btn.click(
                    self._filtrar_por_estado,
                    inputs=[estado_filtro],
                    outputs=[resultado_filtrar]
                )
        
        return demo
    
    # Lanzar la aplicación
    def launch(self):
        """Lanza la aplicación web con la configuración establecida"""
        self.demo.launch(server_port=WEB_PORT, share=WEB_SHARE)

# Lanzar la aplicación
if __name__ == "__main__":
    app = AppManagerIdeas()
    app.launch()
    
    def __init__(self):
        self.servicio_ideas = ServicioIdeas()
        self.demo = self.create_interface()
        
        # Registrar función de cierre para cuando se detenga Gradio
        import atexit
        atexit.register(self.close_connections)
    
    def close_connections(self):
        # Acceder al factory a través del servicio y cerrar la conexión
        if hasattr(self.servicio_ideas, 'db_manager') and \
           hasattr(self.servicio_ideas.db_manager, 'factory') and \
           hasattr(self.servicio_ideas.db_manager.factory, 'close_connection'):
            self.servicio_ideas.db_manager.factory.close_connection()
            print("Conexión a la base de datos cerrada correctamente")