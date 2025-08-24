from data.interfaces.connection import DatabaseConnection

class ORMConnection(DatabaseConnection):
    def connect(self):
        print("Connecting via ORM")
        # Implementation
    
    def execute_query(self, query, params=None):
        print(f"Executing via ORM session: {query}")
        # Implementation