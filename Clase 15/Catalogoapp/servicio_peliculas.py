# Catalogoapp/servicio_peliculas.py
import os
from DAO import PeliculaDAO
from pelicula import Pelicula

class ServicioPeliculas:
    
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(script_dir, 'catalogo_peliculas.db')
        self.dao = PeliculaDAO(database=self.db_name)
        

    def agregar_pelicula(self, pelicula):
        try:
            self.dao.insertar_pelicula(pelicula)
            return True
        except Exception as e:
            print(f"Error al agregar película: {e}")
            return False
   
    def listar_peliculas(self):
        try:
            peliculas = self.dao.obtener_todas_las_peliculas()
            print("--- Listado de películas: ---")
            if peliculas:
                for pelicula in peliculas:
                    print(f"ID: {pelicula[0]} | Nombre: {pelicula[1]} | Director: {pelicula[2]} | Año: {pelicula[3]}")
            else:
                print("No hay películas en el catálogo.")
            print("--- Fin del listado ---\n")
            return peliculas
        except Exception as e:
            print(f"Error al listar películas: {e}")
            return False    
    
    def eliminar_archivo(self, id_pelicula):        
        try:
            resultado = self.dao.eliminar_pelicula(id_pelicula)
            return resultado
        except Exception as e:
            print(f"Error al eliminar película: {e}")
            return False             


if __name__ == '__main__':
    print("=== Testing listar_peliculas method ===\n")
    
    # Create service instance
    servicio = ServicioPeliculas()

    #pelicula1 = Pelicula('Inception', 'Christopher Nolan', 2010)
    #pelicula2 = Pelicula('Interstellar', 'Christopher Nolan', 2014)
    #pelicula3 = Pelicula('Pulp Fiction', 'Quentin Tarantino', 1994)

    #servicio.agregar_pelicula(pelicula1)
    #ervicio.agregar_pelicula(pelicula2)
    #ervicio.agregar_pelicula(pelicula3)
    
    # --- Uso del DAO en el programa principal ---
    
    peliculas  = servicio.listar_peliculas()

   
    for pelicula in peliculas:
        print(pelicula)
        
 