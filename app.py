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
        cronologia.append({"role": "user", "content": messaggio})
        cronologia.append({
            "role": "assistant",
            "content": (
                "ERRORE: La chiave GEMINI_API_KEY non è impostata nelle"
                " variabili d'ambiente di Render!"
            ),
        })
        return "", cronologia

    try:
        client = genai.Client(api_key=api_key)

        # Formatta lo storico dei messaggi nel formato richiesto da Gemini
        contents = []
        for msg in cronologia:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role, parts=[types.Part.from_text(text=msg["content"])]
                )
            )

        # Aggiunge il messaggio corrente
        contents.append(
            types.Content(
                role="user", parts=[types.Part.from_text(text=messaggio)]
            )
        )

        # Chiamata API al modello Gemini 3.6 Flash
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="Sei TONY, un assistente IA amichevole, brillante e utile."
            ),
        )

        testo_risposta = response.text

        # Aggiorna lo storico nel formato Dizionario richiesto da questa versione di Gradio
        cronologia.append({"role": "user", "content": messaggio})
        cronologia.append({"role": "assistant", "content": testo_risposta})

    except Exception as e:
        cronologia.append({"role": "user", "content": messaggio})
        cronologia.append({"role": "assistant", "content": f"ERRORE API: {str(e)}"})

    return "", cronologia


def svuota_chat():
    return []


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<center><h1>TONY - Assistente Virtuale</h1></center>")
    gr.Markdown(
        "<center><h3>Anche se non sono intelligente come Lorenzo, proverò ad"
        " aiutarti!</h3></center>"
    )

    chatbot = gr.Chatbot(height=450)
    msg = gr.Textbox(placeholder="Scrivi un messaggio a TONY...")
    clear = gr.Button("Cancella Chat")

    # Passiamo chatbot sia come input che come output per sincronizzare lo stato dei dizionari
    msg.submit(rispondi, [msg, chatbot], [msg, chatbot])
    clear.click(svuota_chat, inputs=None, outputs=[chatbot])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
