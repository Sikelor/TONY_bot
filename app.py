import os
import gradio as gr
from google import genai
from google.genai import types

# Recupera la chiave API
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def rispondi(messaggio, cronologia):
    if cronologia is None:
        cronologia = []

    # Formattta lo storico della chat per Gemini
    contents = []
    for user_msg, bot_msg in cronologia:
        contents.append(
            types.Content(
                role="user", parts=[types.Part.from_text(text=user_msg)]
            )
        )
        contents.append(
            types.Content(
                role="model", parts=[types.Part.from_text(text=bot_msg)]
            )
        )

    contents.append(
        types.Content(
            role="user", parts=[types.Part.from_text(text=messaggio)]
        )
    )

    # Genera la risposta col modello Gemini 2.5 Flash
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction="Sei TONY, un assistente IA amichevole, brillante e utile."
        ),
    )

    testo_risposta = response.text
    cronologia.append((messaggio, testo_risposta))

    return "", cronologia


# Interfaccia Gradio multi-utente con memoria isolata
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<center><h1>TONY - Assistente Virtuale</h1></center>")
    gr.Markdown("<center><h3>Anche se non sono intelligente come Lorenzo, proverò ad aiutarti!</h3></center>")
    msg = gr.Textbox(placeholder="Scrivi un messaggio a TONY...")
    clear = gr.Button("Cancella Chat")

    # gr.State() garantisce che Beatrice e te abbiate due chat separate
    stato_chat = gr.State([])

    msg.submit(rispondi, [msg, stato_chat], [msg, chatbot])
    clear.click(lambda: ([], []), None, [chatbot, stato_chat])

demo.launch()
