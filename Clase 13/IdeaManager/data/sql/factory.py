from data.interfaces.factory import DataAccessFactory
from .connection import SQLConnection
from .repository import SQLRepository

class SQLFactory(DataAccessFactory):
    def __init__(self):
        self.connection = None

    def create_connection(self):
        if not self.connection:
            self.connection = SQLConnection()
        return self.connection

    def create_repository(self, entity_type):
        print("Creating repository for entity type:", entity_type)
        return SQLRepository(self.create_connection(), entity_type)

    def close_connection(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None


  