import os
import gradio as gr
from google import genai
from google.genai import types

# Recupera la chiave API da Render
api_key = os.environ.get("GEMINI_API_KEY")


def rispondi(messaggio, cronologia):
    if cronologia is None:
        cronologia = []

    if not api_key:
        cronologia.append((
            messaggio,
            "ERRORE: La chiave GEMINI_API_KEY non è impostata nelle variabili"
            " d'ambiente di Render!",
        ))
        return "", cronologia

    try:
        # Inizializza il client Google GenAI
        client = genai.Client(api_key=api_key)

        # Prepara lo storico
        contents = []
        for user_msg, bot_msg in cronologia:
            contents.append(
                types.Content(
                    role="user", parts=[types.Part.from_text(text=str(user_msg))]
                )
            )
            contents.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=str(bot_msg))],
                )
            )

        contents.append(
            types.Content(
                role="user", parts=[types.Part.from_text(text=messaggio)]
            )
        )

        # Chiamata API al modello gemini-2.5-flash
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="Sei TONY, un assistente IA amichevole, brillante e utile."
            ),
        )

        testo_risposta = response.text
        cronologia.append((messaggio, testo_risposta))

    except Exception as e:
        # Mostra l'errore esatto dentro la chat anziché far crashare l'interfaccia
        cronologia.append((messaggio, f"ERRORE API: {str(e)}"))

    return "", cronologia


def svuota_chat():
    return [], []


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<center><h1>TONY - Assistente Virtuale</h1></center>")
    gr.Markdown(
        "<center><h3>Anche se non sono intelligente come Lorenzo, proverò ad"
        " aiutarti!</h3></center>"
    )

    chatbot = gr.Chatbot(height=450)
    msg = gr.Textbox(placeholder="Scrivi un messaggio a TONY...")
    clear = gr.Button("Cancella Chat")

    stato_chat = gr.State([])

    msg.submit(rispondi, [msg, stato_chat], [msg, chatbot])
    clear.click(svuota_chat, inputs=None, outputs=[chatbot, stato_chat])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
