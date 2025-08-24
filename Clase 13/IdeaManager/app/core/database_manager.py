from data.sql.factory import SQLFactory

class DatabaseManager:
    def __init__(self, factory=None):
        self.factory = factory or SQLFactory()  # Default
    
    def set_factory(self, factory):
        self.factory = factory
    
    def get_repository(self, entity_type):
        return self.factory.create_repository(entity_type)

   