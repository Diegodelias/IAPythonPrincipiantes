#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar la conexión a la base de datos y las tablas necesarias
para la aplicación IdeaManager.
"""

import os
import sys
import mysql.connector
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verificar_mysql_server():
    """Verifica si el servidor MySQL está en ejecución"""
    print("Verificando servidor MySQL...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        conn.close()
        print("✅ Servidor MySQL en ejecución")
        return True
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar al servidor MySQL: {err}")
        return False

def verificar_base_datos():
    """Verifica si la base de datos existe y la crea si no existe"""
    print(f"Verificando base de datos '{os.getenv('DB_NAME')}'...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe
        cursor.execute(f"SHOW DATABASES LIKE '{os.getenv('DB_NAME')}'")
        result = cursor.fetchone()
        
        if not result:
            print(f"Base de datos '{os.getenv('DB_NAME')}' no encontrada. Creando...")
            cursor.execute(f"CREATE DATABASE {os.getenv('DB_NAME')}")
            print(f"✅ Base de datos '{os.getenv('DB_NAME')}' creada correctamente")
        else:
            print(f"✅ Base de datos '{os.getenv('DB_NAME')}' existe")
        
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"❌ Error al verificar/crear la base de datos: {err}")
        return False

def verificar_tablas():
    """Verifica si las tablas necesarias existen y las crea si no existen"""
    print("Verificando tablas...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME')
        )
        cursor = conn.cursor()
        
        # Verificar tabla ideas
        cursor.execute("SHOW TABLES LIKE 'ideas'")
        if not cursor.fetchone():
            print("Tabla 'ideas' no encontrada. Creando...")
            create_ideas_table = """
            CREATE TABLE ideas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                descripcion TEXT,
                categoria VARCHAR(100),
                fecha_creacion VARCHAR(50),
                estado VARCHAR(50),
                tags TEXT,
                recursos TEXT,
                notas TEXT
            )
            """
            cursor.execute(create_ideas_table)
            print("✅ Tabla 'ideas' creada correctamente")
        else:
            print("✅ Tabla 'ideas' existe")
        
        conn.commit()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"❌ Error al verificar/crear las tablas: {err}")
        return False

def insertar_datos_prueba():
    """Inserta datos de prueba en la tabla ideas"""
    print("Insertando datos de prueba...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME')
        )
        cursor = conn.cursor()
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM ideas")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Insertar datos de prueba
            insert_query = """
            INSERT INTO ideas (titulo, descripcion, categoria, fecha_creacion, estado)
            VALUES 
            ('Idea de prueba 1', 'Descripción de la idea 1', 'Tecnología', '2023-08-21', 'Pendiente'),
            ('Idea de prueba 2', 'Descripción de la idea 2', 'Negocios', '2023-08-21', 'En progreso')
            """
            cursor.execute(insert_query)
            conn.commit()
            print(f"✅ {cursor.rowcount} ideas de prueba insertadas correctamente")
        else:
            print(f"✅ Ya existen {count} ideas en la base de datos")
        
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"❌ Error al insertar datos de prueba: {err}")
        return False

def main():
    """Función principal"""
    print("=== Verificación de la base de datos para IdeaManager ===")
    
    # Verificar servidor MySQL
    if not verificar_mysql_server():
        print("\n❌ El servidor MySQL no está en ejecución o no es accesible.")
        print("Por favor, verifique que el servidor MySQL esté en ejecución y")
        print("que las credenciales en el archivo .env sean correctas.")
        sys.exit(1)
    
    # Verificar base de datos
    if not verificar_base_datos():
        print("\n❌ No se pudo verificar/crear la base de datos.")
        print("Por favor, verifique las credenciales y permisos del usuario MySQL.")
        sys.exit(1)
    
    # Verificar tablas
    if not verificar_tablas():
        print("\n❌ No se pudieron verificar/crear las tablas necesarias.")
        print("Por favor, verifique los permisos del usuario MySQL.")
        sys.exit(1)
    
    # Insertar datos de prueba
    insertar_datos_prueba()
    
    print("\n✅ Verificación completada con éxito!")
    print("La base de datos está configurada correctamente para IdeaManager.")

if __name__ == "__main__":
    main()
