
# --------------------------------------------------------------
# Script: lab2_sales_pipeline_sendgrid.py
# Descripción: Flujo SDR con múltiples agentes de ventas, selección del mejor,
#              handoff a "Email Manager" que formatea a HTML y envía por SendGrid.
#              Versión LIVE (sin DRY_RUN) y con emails de la notebook original.
# --------------------------------------------------------------
# Requisitos:
#   pip install openai-agents python-dotenv sendgrid
# Variables de entorno necesarias (.env):
#   OPENAI_API_KEY=sk-...
#   SENDGRID_API_KEY=SG-...
# --------------------------------------------------------------

from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from typing import Dict, List
import asyncio
import os

# --- Email (SendGrid) ---
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

# Cargar entorno
load_dotenv(override=True)

def require_env(var: str) -> str:
    val = os.getenv(var)
    if not val:
        raise RuntimeError(f"Falta la variable de entorno: {var}")
    return val

# Claves necesarias
OPENAI_API_KEY = require_env("OPENAI_API_KEY")
SENDGRID_API_KEY = require_env("SENDGRID_API_KEY")

# Correos fijos de la notebook original
FROM_EMAIL_ADDR = "ia@prosperaria.com"
TO_EMAIL_ADDR   = "ariel.alegre@graduadosfiuba.org"

# ------------------------
# Tools de envío de correo (LIVE)
# ------------------------
@function_tool
def send_email(body: str) -> Dict[str, str]:
    """
    Envía un correo de texto plano.
    """
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(FROM_EMAIL_ADDR)
    to_email = To(TO_EMAIL_ADDR)
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Email de ventas (texto)", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(f"[send_email] status={response.status_code}")
    return {"status": "success", "code": response.status_code}

@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """
    Envía un correo en formato HTML.
    """
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(FROM_EMAIL_ADDR)
    to_email = To(TO_EMAIL_ADDR)
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(f"[send_html_email] status={response.status_code}")
    return {"status": "success", "code": response.status_code}

# ------------------------
# Agentes auxiliares -> tools
# ------------------------
subject_instructions = (
    "Puedes escribir un asunto para un correo electrónico de ventas en frío. "
    "Se te proporciona un mensaje y necesitas escribir un asunto corto, claro y atractivo "
    "para un correo electrónico que probablemente obtenga respuesta."
)
subject_writer = Agent(
    name="Escritor de asunto de correo electrónico",
    instructions=subject_instructions,
    model="gpt-4o-mini",
)
subject_tool = subject_writer.as_tool(
    tool_name="subject_writer",
    tool_description="Escribe un asunto atractivo para un correo de ventas en frío",
)

html_instructions = (
    "Puedes convertir un cuerpo de correo electrónico de texto a HTML. "
    "Se te proporciona un cuerpo de correo electrónico (puede contener markdown) y debes "
    "convertirlo a HTML con un diseño simple, claro y atractivo."
)
html_converter = Agent(
    name="Conversor de cuerpo de email a HTML",
    instructions=html_instructions,
    model="gpt-4o-mini",
)
html_tool = html_converter.as_tool(
    tool_name="html_converter",
    tool_description="Convierte el cuerpo de un email en HTML simple y legible",
)

# ------------------------
# Email Manager + handoff target
# ------------------------
emailer_instructions = (
    "Eres un formateador y remitente de correos electrónicos. "
    "Recibes el cuerpo de un correo electrónico para enviarlo. "
    "Primero usas la herramienta subject_writer para escribir un asunto, "
    "luego usas la herramienta html_converter para convertir el cuerpo a HTML, "
    "y finalmente usas la herramienta send_html_email para enviar el correo con el asunto y el HTML."
)
emailer_tools = [subject_tool, html_tool, send_html_email]
emailer_agent = Agent(
    name="Email Manager",
    instructions=emailer_instructions,
    tools=emailer_tools,
    model="gpt-4o-mini",
    handoff_description="Convierte un email a HTML y lo envía",
)

# ------------------------
# Agentes de ventas (3 estilos)
# ------------------------
instructions1 = (
    "Eres un agente de ventas profesional y serio que trabaja para ComplAI, "
    "una herramienta SaaS para garantizar el cumplimiento de SOC2 y prepararse para auditorías, impulsada por IA. "
    "Redactas correos electrónicos en frío profesionales."
)
instructions2 = (
    "Eres un agente de ventas ingenioso y atractivo que trabaja para ComplAI, "
    "una herramienta SaaS para garantizar el cumplimiento de SOC2 y prepararse para auditorías, impulsada por IA. "
    "Redactas correos en frío ingeniosos que obtienen respuesta."
)
instructions3 = (
    "Eres un agente de ventas conciso y directo que trabaja para ComplAI, "
    "una herramienta SaaS para garantizar el cumplimiento de SOC2 y prepararse para auditorías, impulsada por IA. "
    "Redactas correos en frío breves y al punto."
)

sales_agent1 = Agent(name="Agente de ventas profesional", instructions=instructions1, model="gpt-4o-mini")
sales_agent2 = Agent(name="Agente de ventas atractivo",   instructions=instructions2, model="gpt-4o-mini")
sales_agent3 = Agent(name="Agente de ventas directo",     instructions=instructions3, model="gpt-4o-mini")

# ------------------------
# Manager que elige y hace handoff
# ------------------------
sales_manager_instructions = (
    "Eres un manager de ventas. Recibes múltiples propuestas de correos en frío, "
    "eliges la mejor usando tu propio criterio de efectividad (claridad, relevancia, CTA), "
    "y transfieres (handoff) el correo elegido al 'Email Manager' para formatearlo y enviarlo."
)
handoffs = [emailer_agent]
sales_manager = Agent(
    name="Manager de ventas",
    instructions=sales_manager_instructions,
    tools=[],
    handoffs=handoffs,
    model="gpt-4o-mini",
)

# ------------------------
# Ejecución
# ------------------------
async def generate_candidates(message: str) -> List[str]:
    """Genera 3 candidatos de email en paralelo (uno por estilo de agente)."""
    with trace("SDR: generación de candidatos"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )
    return [r.final_output for r in results]

async def pick_and_send(best_candidates: List[str]) -> str:
    """
    El manager elige el mejor entre 'best_candidates' y hace handoff al Email Manager,
    que lo formatea (asunto + HTML) y lo envía.
    """
    joined = "\n\n---\n\n".join(best_candidates)
    manager_message = (
        "Aquí tienes múltiples candidatos de correo en frío. "
        "Selecciona el mejor y transfiérelo (handoff) al 'Email Manager' para formatear y enviar.\n\n"
        f"{joined}"
    )
    with trace("SDR: selección y envío (handoff)"):
        result = await Runner.run(sales_manager, manager_message)
    return result.final_output

async def main():
    message = "Escribe un correo electrónico de ventas en frío dirigido a 'Estimado director ejecutivo'."
    print("🚀 Iniciando flujo SDR (LIVE)...\n")

    candidates = await generate_candidates(message)
    print("📄 Candidatos generados:\n")
    for i, c in enumerate(candidates, 1):
        print(f"[Candidato {i}]\n{c}\n")

    final_result = await pick_and_send(candidates)
    print("\n✅ Resultado final (tras handoff al Email Manager):\n")
    print(final_result)

    print("\n📍 Podés ver la traza completa iniciando sesión en: https://platform.openai.com/trace")

if __name__ == '__main__':
    asyncio.run(main())
