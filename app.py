import os
import gradio as gr
from google import genai

# Invece di scriverla in chiaro, la legge in modo sicuro dalle impostazioni di Render
chiave = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=chiave)

def risposta_tony(messaggio, storia):
    risposta = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=messaggio,
        config={"system_instruction": "Sei TONY, un assistente virtuale amichevole e ironico creato da Lorenzo."}
    )
    return risposta.text

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("<center><h1>TONY - Assistente Virtuale</h1></center>")
    gr.Markdown("<center><h5>Anche se non sono intelligente come Lorenzo, proverò ad aiutarti!</h5></center>")
    
    chat = gr.ChatInterface(
        fn=risposta_tony,
        textbox=gr.Textbox(placeholder="Scrivi un messaggio a TONY...")
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
