from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
import gradio as gr
import gspread

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

from config import INSTITUCION, PROMPT_BASE, ARCHIVO_RESUMEN

from google.oauth2.service_account import Credentials

load_dotenv(override=True)


# Función para enviar notificación con Pushover
def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def guardar_en_planilla(email, name="Nombre no indicado", notes="no proporcionadas"):
    credenciales = os.getenv("GOOGLE_SHEETS_KEYFILE")

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    
    creds = Credentials.from_service_account_file(
        credenciales,
        scopes=scopes
    )

    cliente = gspread.authorize(creds)

    sheet_id = "1xt0RKlSmG4T9XwQNCAWU_DsRUkUPMuNPhnYWBfo9kiw"
    spreadsheet = cliente.open_by_key(sheet_id)
    hoja = spreadsheet.worksheet("Hoja 1")  # nombre visible en la pestaña

    hoja.append_row([name, email, notes])

    print(f"[LOG] Contacto guardado en planilla: {name}, {email}, {notes}", flush=True)
    return {"planilla": "ok"}

def centralIAs_user_details(email, name="Nombre no indicado", notes="no proporcionadas"):
    mensaje = f"📩 Interesado en Central IAS:\nNombre: {name}\nEmail: {email}\nNotas: {notes}"
    push(mensaje)
    return {"recorded": "ok"}

def enviar_temario(destinatario, asunto="Sin asunto", cuerpo="Mensaje sin contenido"):
    try:
        message = Mail(
            from_email=os.getenv("SENDGRID_FROM"),
            to_emails=destinatario,
            subject=asunto,
            plain_text_content=cuerpo
        )
        sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)

        print(f"[EMAIL] Enviado a {destinatario} | Estado: {response.status_code}", flush=True)
        return {"email": "enviado", "status_code": response.status_code}
    except Exception as e:
        print(f"[ERROR] Falló el envío de mail: {e}", flush=True)
        return {"email": "error", "detalle": str(e)}


guardar_en_planilla_json = {
    "name": "guardar_en_planilla",
    "description": "Guarda los datos del usuario en una hoja de cálculo de Google Sheets.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "Correo electrónico del usuario"
            },
            "name": {
                "type": "string",
                "description": "Nombre del usuario"
            },
            "notes": {
                "type": "string",
                "description": "Comentarios o notas sobre el interés del usuario"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

centralIAs_user_details_json = {
    "name": "centralIAs_user_details",
    "description": "Utiliza esta herramienta para registrar que un usuario está interesado en la Central de IAs y proporcionó una dirección de correo electrónico.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "La dirección de email del usuario"
            },
            "name": {
                "type": "string",
                "description": "El nombre del usuario, si se indica"
            },
            "notes": {
                "type": "string",
                "description": "¿Alguna información adicional sobre la conversación que valga la pena registrar para dar contexto?"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

enviar_temario_json = {
    "name": "enviar_temario",
    "description": "Envía el temario de un curso específico al correo del usuario. Usar solo si el usuario lo solicita explícitamente que le envíen el temario de un curso.",
    "parameters": {
        "type": "object",
        "properties": {
            "destinatario": {
                "type": "string",
                "description": "Email del usuario que solicitó el temario"
            },
            "asunto": {
                "type": "string",
                "description": "Asunto del correo que se enviará"
            },
            "cuerpo": {
                "type": "string",
                "description": "Texto del cuerpo del correo con el temario del curso solicitado"
            }
        },
        "required": ["destinatario", "asunto", "cuerpo"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": guardar_en_planilla_json},
    {"type": "function", "function": centralIAs_user_details_json},
    {"type": "function", "function": enviar_temario_json}
]



#The code provided is a Python function named `handle_tool_calls` that processes a list of tool calls. It avoids using an `if` statement by utilizing the `globals().get()` function to dynamically retrieve a tool function based on its name. Here's a breakdown of what the code does:
# Esta es una forma más elegante de evitar el IF statement.

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Herramienta llamada: {tool_name}", flush=True)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results





class Me:


    def __init__(self):
        self.openai = OpenAI()
        self.name = INSTITUCION
        try:
            with open(ARCHIVO_RESUMEN, "r", encoding="utf-8") as f:
                self.summary = f.read()
                print(f"[INFO] Se cargó el archivo {ARCHIVO_RESUMEN} con este contenido inicial:")
                print(self.summary[:200])  # Muestra los primeros 200 caracteres
        except FileNotFoundError:
                self.summary = "No se encontró el resumen. Por favor, cargá 'me/summary.txt'."
                print(f"[ADVERTENCIA] No se encontró el archivo {ARCHIVO_RESUMEN}. Se usará mensaje de respaldo.")


    
    def system_prompt(self):
        system_prompt = PROMPT_BASE
        system_prompt += f"\n\n## Resumen:\n{self.summary}\n\n"
        system_prompt += f"""En este contexto, por favor chatea con el usuario, manteniéndote siempre en el personaje de asesor de cursos de IA de {self.name}. Si el usuario menciona la Central de IAs, usá la herramienta 'centralIAs_user_details' para registrar su interés enviando una notificación."""
        system_prompt += f"""Si el usuario pide el temario de un curso, pedile su dirección de correo electrónico y el nombre del curso. Luego usá la herramienta 'enviar_temario' para enviarle esa información."""
        

        return system_prompt
    
    
    def chat(self, message, history):
        print("[LOG] Iniciando conversación...", flush=True)
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            print("[LOG] Enviando mensaje al modelo...", flush=True)
            response = self.openai.chat.completions.create(model="gpt-4o", messages=messages, tools=tools, tool_choice="auto")

            print("[LOG] Respuesta recibida", flush=True)
            reply = response.choices[0].message

            if response.choices[0].finish_reason == "tool_calls":
                print("[LOG] El modelo quiere usar una herramienta...", flush=True)
                tool_calls = reply.tool_calls
                results = handle_tool_calls(tool_calls)
                messages.append(reply)
                messages.extend(results)
            else:
                done = True
                print("[LOG] Respuesta final:", reply.content, flush=True)
                return reply.content

    

if __name__ == "__main__":
    me = Me()
gr.ChatInterface(me.chat, type="messages").launch(share=True)
    
