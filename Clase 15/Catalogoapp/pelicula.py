# Catalogoapp/pelicula.py
class Pelicula:
    def __init__(self, nombre, director , anio):
        self.nombre = nombre
        self.director = director
        self.anio = anio

    def __str__(self):
        return f"Pelicula: {self.nombre}, Director: {self.director}, Año: {self.anio}"