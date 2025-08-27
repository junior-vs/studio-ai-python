from json import load
from operator import ge
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

MODELO_PADRAO = "gemini-2.5-flash"

prompt_sistema = "Liste apenas os nomes dos produtos e ofereça uma breve descrição."



config_model = {
    "max_output_tokens": 8192,
    "temperature": 2.0,
    "top_p": 0.8,
    "top_k": 64    
}

llm = genai.GenerativeModel(
    model_name=MODELO_PADRAO,
    system_instruction=prompt_sistema,    
    generation_config=config_model,
)


#pergunta = "Liste três produtos de moda sustentável para ir ao shopping."
pergunta = "Liste três produtos de moda sustentável para ir ao shopping."

resposta = llm.generate_content(pergunta)


print(f"A resposta gerada para pergunta é: {resposta.text}")

