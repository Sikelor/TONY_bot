import os
import gradio as gr
from google import genai
from google.genai import types

# Inizializza il client prendendo la chiave API dalle variabili d'ambiente
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def rispondi(messaggio, cronologia):
    if cronologia is None:
        cronologia = []

    # Costruisce lo storico per Gemini usando il formato tupla (user, bot)
    contents = []
    for user_msg, bot_msg in cronologia:
        contents.append(
            types.Content(
                role="user", parts=[types.Part.from_text(text=str(user_msg))]
            )
        )
        contents.append(
            types.Content(
                role="model", parts=[types.Part.from_text(text=str(bot_msg))]
            )
        )

    # Aggiunge il messaggio corrente dell'utente
    contents.append(
        types.Content(
            role="user", parts=[types.Part.from_text(text=messaggio)]
        )
    )

    # Chiamata al modello Gemini 2.5 Flash
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction="Sei TONY, un assistente IA amichevole, brillante e utile."
        ),
    )

    testo_risposta = response.text

    # Aggiorna la cronologia aggiungendo la nuova tupla (messaggio, risposta)
    cronologia.append((messaggio, testo_risposta))

    return "", cronologia


def svuota_chat():
    return [], []


# Interfaccia Gradio
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

    # Collegamento corretto degli eventi con lo stato isolato
    msg.submit(rispondi, [msg, stato_chat], [msg, chatbot])
    clear.click(svuota_chat, inputs=None, outputs=[chatbot, stato_chat])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
