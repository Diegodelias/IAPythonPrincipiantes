import mysql.connector
import os
from dotenv import load_dotenv
from data.interfaces.connection import DatabaseConnection

# Load environment variables from .env file
load_dotenv()

class SQLConnection(DatabaseConnection):
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = int(port or os.getenv('DB_PORT', 3306))
        self.user = user or os.getenv('DB_USER', 'root')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.database = database or os.getenv('DB_NAME', 'idea_manager')
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establishes a connection to the MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor(dictionary=True)  # Return rows as dictionaries
            print(f"Connected to MySQL database {self.database} on {self.host}")
            return True
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return False
    
    def disconnect(self):
        """Closes the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            print("Disconnected from MySQL database")
    
    def refresh_connection(self):
        """Refreshes the database connection to ensure fresh results"""
        if self.connection and self.cursor:
            # Close the current cursor and create a new one
            self.cursor.close()
            self.cursor = self.connection.cursor(dictionary=True)
            print("Database cursor refreshed")
        else:
            # If no connection exists, create a new one
            self.connect()
            
    def execute_query(self, query, params=None):
        """Executes a SQL query with optional parameters"""
        if not self.connection:
            self.connect()
        
        # For SELECT queries, refresh the connection to ensure fresh results
        if query.strip().upper().startswith("SELECT"):
            self.refresh_connection()
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            # For SELECT queries, return results
            if query.strip().upper().startswith("SELECT"):
                results = self.cursor.fetchall()
                return results
            # For other queries (INSERT, UPDATE, DELETE), commit and return affected rows
            else:
                self.connection.commit()
                return self.cursor.rowcount
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            return None
    
    def create_tables(self):
        """Creates necessary tables if they don't exist"""
        create_ideas_table = """
        CREATE TABLE IF NOT EXISTS ideas (
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
        self.execute_query(create_ideas_table)
        print("Tables created or already exist")