#!/usr/bin/env python3
"""
IdeaManager - Demo script for testing services with different factory types
"""
import datetime
from app.services.servicio_ideas import ServicioIdeas
from app.models.idea import Idea

def test_service(factory_type):
    """Test the service with a specific factory type"""
    print(f"\n=== Testing with {factory_type.upper()} factory ===")
    
    # Inicializar el servicio con el factory especificado
    servicio = ServicioIdeas(factory_type=factory_type)
    
    # Mostrar todas las ideas existentes
    print("\nIdeas existentes:")
    ideas = servicio.listar_ideas()
    if ideas:
        for i, idea in enumerate(ideas, 1):
            print(f"{i}. ID: {idea.get('idea_id')}, Título: {idea.get('titulo')}")
    else:
        print("No hay ideas guardadas.")
    
    # Crear una idea de prueba
    print("\nCreando idea de prueba...")
    
    # Crear objeto Idea
    nueva_idea = Idea(
        f"Idea de prueba con {factory_type}",
        f"Esta idea fue creada para probar el factory de tipo {factory_type}",
        "Prueba"
    )
    nueva_idea.estado = "Nueva"
    
    # Agregar tags y recursos
    nueva_idea.agregar_tag(factory_type)
    nueva_idea.agregar_tag("prueba")
    nueva_idea.agregar_recurso(f"Recurso de {factory_type}")
    
    # Guardar la idea
    resultado = servicio.agregar_idea(nueva_idea)
    if resultado:
        print(f"Idea creada correctamente con {factory_type}")
    else:
        print(f"Error al crear la idea con {factory_type}")
    
    # Mostrar las ideas actualizadas
    print("\nIdeas después de agregar:")
    ideas = servicio.listar_ideas()
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. ID: {idea.get('idea_id')}, Título: {idea.get('titulo')}")
    
    print(f"\n=== Fin de prueba con {factory_type.upper()} ===")

def main():
    """Main entry point for the demo script"""
    # Probar con SQL factory (predeterminado)
    test_service("sql")
    
    # Probar con ORM factory
    test_service("orm")
    
    return 0

if __name__ == "__main__":
    main()
