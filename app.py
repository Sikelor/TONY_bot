import os
import gradio as gr
from google import genai
from google.genai import types

# Recupera la chiave API
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def rispondi(messaggio, cronologia):
    if cronologia is None:
        cronologia = []

    # Formatta lo storico per l'API di Gemini
    contents = []
    for msg in cronologia:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role, parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # Aggiunge l'ultimo messaggio dell'utente per Gemini
    contents.append(
        types.Content(
            role="user", parts=[types.Part.from_text(text=messaggio)]
        )
    )

    # Chiamata a Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction="Sei TONY, un assistente IA amichevole, brillante e utile."
        ),
    )

    testo_risposta = response.text

    # Nuovo formato dizionario per le versioni recenti di Gradio
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

    # type="messages" abilita il supporto al nuovo formato di Gradio
    chatbot = gr.Chatbot(height=450, type="messages")

    msg = gr.Textbox(placeholder="Scrivi un messaggio a TONY...")
    clear = gr.Button("Cancella Chat")

    stato_chat = gr.State([])

    msg.submit(rispondi, [msg, chatbot], [msg, chatbot])
    clear.click(svuota_chat, inputs=None, outputs=[chatbot, stato_chat])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
