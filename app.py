import os
import gradio as gr
from google import genai
from google.genai import types

# Recupera la chiave API
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def rispondi(messaggio, cronologia):
    if cronologia is None:
        cronologia = []

    # Formatta lo storico dei messaggi per l'API di Gemini
    contents = []
    for item in cronologia:
        if isinstance(item, dict):
            role = "user" if item.get("role") == "user" else "model"
            content = item.get("content", "")
        else:
            role = "user"
            content = item[0] if len(item) > 0 else ""

        if content:
            contents.append(
                types.Content(
                    role=role, parts=[types.Part.from_text(text=content)]
                )
            )

    # Aggiunge l'ultimo messaggio dell'utente
    contents.append(
        types.Content(
            role="user", parts=[types.Part.from_text(text=messaggio)]
        )
    )

    # Chiamata al modello Gemini 2.5 Flash
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction="Sei TONY, un assistente IA amichevole, brillante e utile."
        ),
    )

    testo_risposta = response.text

    # Aggiorna la cronologia in formato compatibile (dizionario)
    cronologia.append({"role": "user", "content": messaggio})
    cronologia.append({"role": "assistant", "content": testo_risposta})

    return "", cronologia


def svuota_chat():
    return [], []


# Interfaccia Gradio multi-utente
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<center><h1>TONY - Assistente Virtuale</h1></center>")
    gr.Markdown(
        "<center><h3>Anche se non sono intelligente come Lorenzo, proverò ad"
        " aiutarti!</h3></center>"
    )

    # Inizializzazione pulita senza argomenti non supportati
    chatbot = gr.Chatbot(height=450)

    msg = gr.Textbox(placeholder="Scrivi un messaggio a TONY...")
    clear = gr.Button("Cancella Chat")

    stato_chat = gr.State([])

    msg.submit(rispondi, [msg, chatbot], [msg, chatbot])
    clear.click(svuota_chat, inputs=None, outputs=[chatbot, stato_chat])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
