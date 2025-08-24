from data.interfaces.factory import DataAccessFactory
from .connection import ORMConnection
from .repository import ORMRepository

class ORMFactory(DataAccessFactory):
    def create_connection(self):
        return ORMConnection()
    
    def create_repository(self, entity_type):
        return ORMRepository(self.create_connection(), entity_type)