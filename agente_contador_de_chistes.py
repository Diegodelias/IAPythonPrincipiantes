
# --------------------------------------------------------------
# Script: agente_contador_de_chistes.py
# Descripción: Agente de IA que cuenta chistes usando el SDK de OpenAI Agents
# --------------------------------------------------------------

# Requisitos previos:
# pip install openai-agents python-dotenv

from dotenv import load_dotenv
from agents import Agent, Runner, trace

# Cargar variables de entorno (.env) para acceder a OPENAI_API_KEY
load_dotenv(override=True)

# Crear un agente de chistes con personalidad humorística
chiste_agent = Agent(
    name="Contador de Chistes",
    instructions="Eres un comediante de stand-up muy divertido. Responde a todo con un chiste.",
)

# Mensaje de entrada de ejemplo
entrada = "¿Puedes contarme un chiste sobre programadores?"

# Ejecutar el agente y obtener respuesta con trazabilidad
if __name__ == "__main__":
    print("🎤 Bienvenido al show del Contador de Chistes...\n")
    with trace("Chiste sobre programadores"):
        resultado = Runner.run_sync(chiste_agent, entrada)
        print("😂 Chiste del agente:")
        print(resultado.final_output)

    print("\n📍 Podés ver la traza completa iniciando sesión en: https://platform.openai.com/trace")
