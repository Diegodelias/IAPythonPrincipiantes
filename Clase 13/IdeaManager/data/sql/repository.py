class SQLRepository:
    def __init__(self, connection, entity_type):
        self.connection = connection
        self.entity_type = entity_type

    def find_all(self):
        print(f"DEBUG: SQLRepository.find_all called for {self.entity_type}")
        # Force a new query execution each time by closing and reopening the cursor
        if hasattr(self.connection, 'cursor') and self.connection.cursor:
            self.connection.cursor.close()
            self.connection.cursor = self.connection.connection.cursor(dictionary=True)
        
        result = self.connection.execute_query(f"SELECT * FROM {self.entity_type}")
        print(f"DEBUG: SQLRepository.find_all returning {len(result) if result else 0} records")
        return result

    def find_by_id(self, id):
        # Usar el nombre correcto de la columna ID según la entidad
        id_column = 'idea_id' if self.entity_type == 'ideas' else 'id'
        return self.connection.execute_query(
            f"SELECT * FROM {self.entity_type} WHERE {id_column} = %s", [id]
        )
        
    def create_idea(self, idea_data, tags=None, recursos=None):
        """
        Crea una nueva idea con sus relaciones (tags y recursos)
        
        Args:
            idea_data (dict): Datos de la idea (titulo, descripcion, etc.)
            tags (list): Lista de nombres de etiquetas a asociar con la idea
            recursos (list): Lista de nombres de recursos a asociar con la idea
            
        Returns:
            int: ID de la idea creada o None si falló la creación
        """
        try:
            # Iniciar transacción
            self.connection.execute_query("START TRANSACTION")
            
            # 1. Insertar la idea principal
            valid_columns = ['titulo', 'descripcion', 'categoria', 'fecha_creacion', 
                           'estado']
            filtered_data = {k: v for k, v in idea_data.items() if k in valid_columns}
            
            # Construir la consulta SQL
            columns = ', '.join(filtered_data.keys())
            placeholders = ', '.join(['%s'] * len(filtered_data))
            values = list(filtered_data.values())
            
            query = f"INSERT INTO ideas ({columns}) VALUES ({placeholders})"
            
            # Ejecutar la consulta
            self.connection.execute_query(query, values)
            
            # Obtener el ID de la idea recién creada
            id_query = "SELECT LAST_INSERT_ID()"
            id_result = self.connection.execute_query(id_query)
            
            if not id_result or len(id_result) == 0:
                # Rollback si no se pudo obtener el ID
                self.connection.execute_query("ROLLBACK")
                return None
                
            idea_id = id_result[0]['LAST_INSERT_ID()']
            
            # 2. Procesar tags si existen
            if tags and isinstance(tags, list):
                for tag_name in tags:
                    # Verificar si el tag ya existe
                    tag_query = "SELECT tag_id FROM tags WHERE tag_name = %s"
                    tag_result = self.connection.execute_query(tag_query, [tag_name])
                    
                    if tag_result and len(tag_result) > 0:
                        # El tag existe, obtener su ID
                        tag_id = tag_result[0]['tag_id']
                    else:
                        # El tag no existe, crearlo
                        create_tag_query = "INSERT INTO tags (tag_name) VALUES (%s)"
                        self.connection.execute_query(create_tag_query, [tag_name])
                        
                        # Obtener el ID del tag recién creado
                        tag_id_query = "SELECT LAST_INSERT_ID()"
                        tag_id_result = self.connection.execute_query(tag_id_query)
                        tag_id = tag_id_result[0]['LAST_INSERT_ID()']
                    
                    # Crear la relación entre idea y tag
                    idea_tag_query = "INSERT INTO idea_tags (idea_id, tag_id) VALUES (%s, %s)"
                    self.connection.execute_query(idea_tag_query, [idea_id, tag_id])
            
            # 3. Procesar recursos si existen
            if recursos and isinstance(recursos, list):
                for recurso_name in recursos:
                    # Verificar si el recurso ya existe
                    recurso_query = "SELECT recurso_id FROM recursos WHERE recurso_name = %s"
                    recurso_result = self.connection.execute_query(recurso_query, [recurso_name])
                    
                    if recurso_result and len(recurso_result) > 0:
                        # El recurso existe, obtener su ID
                        recurso_id = recurso_result[0]['recurso_id']
                    else:
                        # El recurso no existe, crearlo
                        create_recurso_query = "INSERT INTO recursos (recurso_name) VALUES (%s)"
                        self.connection.execute_query(create_recurso_query, [recurso_name])
                        
                        # Obtener el ID del recurso recién creado
                        recurso_id_query = "SELECT LAST_INSERT_ID()"
                        recurso_id_result = self.connection.execute_query(recurso_id_query)
                        recurso_id = recurso_id_result[0]['LAST_INSERT_ID()']
                    
                    # Crear la relación entre idea y recurso
                    idea_recurso_query = "INSERT INTO idea_recursos (idea_id, recurso_id) VALUES (%s, %s)"
                    self.connection.execute_query(idea_recurso_query, [idea_id, recurso_id])
            
            # Confirmar la transacción
            self.connection.execute_query("COMMIT")
            return idea_id
            
        except Exception as e:
            # Rollback en caso de error
            self.connection.execute_query("ROLLBACK")
            print(f"Error al crear idea: {str(e)}")
            return None
