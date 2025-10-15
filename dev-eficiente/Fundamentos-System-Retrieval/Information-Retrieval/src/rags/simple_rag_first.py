# ============================================================
# Exemplo didático de RAG (Retrieval-Augmented Generation)
# ============================================================

# Instalar dependências se necessário:
# pip install sentence-transformers faiss-cpu numpy

from sentence_transformers import SentenceTransformer, util
import faiss
import numpy as np

# ------------------------------------------------------------
# 1. Base de conhecimento (documentos locais)
# ------------------------------------------------------------
documentos = [
    "O modelo Transformer utiliza mecanismos de atenção para processar sequências de texto em paralelo.",
    "Redes neurais convolucionais são amplamente usadas em visão computacional.",
    "O algoritmo TF-IDF mede a importância de um termo em um conjunto de documentos.",
    "O BM25 é uma evolução do TF-IDF, usado para ranqueamento de buscas.",
    "RAG combina recuperação de informações (IR) com geração de linguagem (LLM)."
]

# ------------------------------------------------------------
# 2. Modelo de Embedding
# ------------------------------------------------------------
modelo = SentenceTransformer("all-MiniLM-L6-v2")

# Gera embeddings vetoriais dos documentos
embeddings_docs = modelo.encode(documentos, convert_to_tensor=False)

# ------------------------------------------------------------
# 3. Indexação Vetorial (FAISS)
# ------------------------------------------------------------
dim = embeddings_docs.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings_docs))


# ------------------------------------------------------------
# 4. Função de Recuperação (Retriever)
# ------------------------------------------------------------
def buscar_documentos(query, top_k=2):
    query_emb = modelo.encode([query], convert_to_tensor=False)
    D, I = index.search(np.array(query_emb), top_k)
    resultados = [documentos[i] for i in I[0]]
    return resultados


# ------------------------------------------------------------
# 5. Gerador Simples (LLM simulado)
# ------------------------------------------------------------
def gerar_resposta(query, contextos):
    contexto_textual = " ".join(contextos)
    resposta = f"Pergunta: {query}\n\nCom base nos textos encontrados:\n{contexto_textual}\n\nResumo: "

    # Simulação de um LLM: apenas sumariza de forma simples
    if "transformer" in query.lower():
        resposta += "O modelo Transformer usa atenção para processar sequências em paralelo."
    elif "tf-idf" in query.lower():
        resposta += "TF-IDF mede a importância de palavras em documentos."
    elif "rag" in query.lower():
        resposta += "RAG combina busca de informações e geração de texto."
    else:
        resposta += "Os textos fornecem contexto, mas é necessário mais informação."

    return resposta


# ------------------------------------------------------------
# 6. Execução de Exemplo
# ------------------------------------------------------------
consulta = "O que é RAG em LLMs?"
contextos = buscar_documentos(consulta, top_k=2)
resposta = gerar_resposta(consulta, contextos)

print("=== Documentos Recuperados ===")
for i, c in enumerate(contextos):
    print(f"{i + 1}. {c}")
print("\n=== Resposta Gerada ===")
print(resposta)
