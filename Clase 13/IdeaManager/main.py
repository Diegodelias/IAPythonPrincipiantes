#!/usr/bin/env python3
"""
IdeaManager - Main entry point
"""
import sys
from ui.web import AppManagerIdeas

def main():
    """Main entry point for the IdeaManager application"""
    
    # Iniciar la aplicación web que ya contiene su propia instancia del servicio
    app = AppManagerIdeas()
    app.launch()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())