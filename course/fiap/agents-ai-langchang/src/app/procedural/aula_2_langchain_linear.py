# nome_arquivo: aula_2_langchain_linear.py

import os

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

# Importações do LangChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Carrega variáveis de ambiente
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Defina a OPENAI_API_KEY no arquivo .env")

# 1. Configuração
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()

# 2. Simulação de Base de Conhecimento (Vector Store)
# Em um cenário real, isso viria de PDFs ou Banco de Dados
textos_base = [
    "O LangGraph cria nós e arestas para orquestrar agentes.",
    "LangChain dá ferramentas para prompts e integrações.",
    "Grafos permitem rotas condicionais explícitas."
]
docs = [Document(page_content=t) for t in textos_base]

# Criação do índice vetorial (FAISS)
vectorstore = FAISS.from_documents(docs, embeddings)

# 3. Definição do Prompt
template = """
Responda à pergunta com base no contexto abaixo:
Contexto: {contexto}

Pergunta: {pergunta}
"""
prompt = PromptTemplate.from_template(template)

# 4. Execução Linear (O "Jeito Antigo")
def executar_pipeline_linear(pergunta: str):
    print(f"--- Processando pergunta: {pergunta} ---")
    
    # Passo A: Recuperação (Retrieval)
    docs_recuperados = vectorstore.similarity_search(pergunta, k=1)
    contexto = docs_recuperados[0].page_content
    print(f"Contexto recuperado: {contexto}")
    
    # Passo B: Geração (Generation)
    chain = prompt | llm
    resposta = chain.invoke({"contexto": contexto, "pergunta": pergunta})
    
    return resposta.content

# Teste
if __name__ == "__main__":
    user_query = "Como o LangGraph organiza fluxos?"
    resposta_final = executar_pipeline_linear(user_query)
    print(f"\nResposta da LLM:\n{resposta_final}")