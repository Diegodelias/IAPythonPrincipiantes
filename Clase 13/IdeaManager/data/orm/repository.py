class ORMRepository:
    def __init__(self, connection, entity_type):
        self.connection = connection
        self.entity_type = entity_type
    
    def find_all(self):
        print(f"ORM: Finding all {self.entity_type} objects")
        # Return empty list for now to avoid errors
        return []
    
    def find_by_id(self, id):
        print(f"ORM: Finding {self.entity_type} with id {id}")
        # Return empty list for now to avoid errors
        return []
        
    def create_idea(self, idea_data, tags=None, recursos=None):
        """
        Mock implementation of create_idea for ORM
        """
        print(f"ORM: Creating new {self.entity_type}")
        # Return a mock ID
        return 999