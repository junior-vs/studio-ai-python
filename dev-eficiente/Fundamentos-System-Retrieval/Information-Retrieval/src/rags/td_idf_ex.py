"""
Implementação de um Sistema de Recuperação de Informação usando TF-IDF
=======================================================================

Este programa demonstra os conceitos fundamentais do modelo Vetorial de Recuperação de Informação,
implementando o algoritmo TF-IDF (Term Frequency - Inverse Document Frequency) para busca e 
ranqueamento de documentos por similaridade.

Conceitos Abordados:
- Pré-processamento de texto (tokenização, normalização)
- Criação de matriz TF-IDF 
- Cálculo de similaridade do cosseno
- Ranqueamento de resultados de busca

Requisitos: uv add nltk scikit-learn numpy
Ou pip install: pip install nltk scikit-learn numpy
"""

import logging
from math import log
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

# ===============================================================================
# CONFIGURAÇÃO DO SISTEMA DE LOGGING
# ===============================================================================
# Configuração do logger para registrar eventos importantes do sistema
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ===============================================================================
# 1. CONFIGURAÇÃO INICIAL E DOWNLOAD DE RECURSOS NLTK
# ===============================================================================
# Verifica e baixa recursos necessários do NLTK (tokenizador e stopwords)
# Essencial para o pré-processamento de texto em português
try:
    nltk.data.find('tokenizers/punkt')    # Tokenizador de sentenças e palavras
    nltk.data.find('corpora/stopwords')   # Lista de palavras comuns (stopwords)
    logger.info("Recursos NLTK já estão disponíveis")
except nltk.downloader.DownloadError:
    logger.info("Baixando pacotes NLTK necessários...")
    nltk.download('punkt')      # Para tokenização
    nltk.download('stopwords')  # Para remoção de palavras irrelevantes
    logger.info("Download dos pacotes NLTK concluído")

# ===============================================================================
# 2. DEFINIÇÃO DO CORPUS DE DOCUMENTOS
# ===============================================================================
# Corpus de Exemplo: 11 documentos sobre Machine Learning
# Cada documento representa um "documento" em nossa base de conhecimento
documents = [
    "Machine learning é um campo da inteligência artificial que permite que computadores aprendam padrões a partir de dados.",
    "O aprendizado de máquina dá aos sistemas a capacidade de melhorar seu desempenho sem serem explicitamente programados.",
    "Em vez de seguir apenas regras fixas, o machine learning descobre relações escondidas nos dados.",
    "Esse campo combina estatística, algoritmos e poder computacional para extrair conhecimento.",
    "O objetivo é criar modelos capazes de generalizar além dos exemplos vistos no treinamento.",
    "Aplicações de machine learning vão desde recomendações de filmes até diagnósticos médicos.",
    "Os algoritmos de aprendizado de máquina transformam dados brutos em previsões úteis.",
    "Diferente de um software tradicional, o ML adapta-se conforme novos dados chegam.",
    "O aprendizado pode ser supervisionado, não supervisionado ou por reforço, dependendo do tipo de problema.",
    "Na prática, machine learning é o motor que impulsiona muitos avanços em visão computacional e processamento de linguagem natural.",
    "Mais do que encontrar padrões, o machine learning ajuda a tomar decisões baseadas em evidências."
]

# ===============================================================================
# 3. FUNÇÃO DE PRÉ-PROCESSAMENTO DE TEXTO
# ===============================================================================
def preprocess(text) -> list[str]: 
    """
    Executa o pré-processamento básico de texto para normalização.
    
    Etapas do pré-processamento:
    1. Conversão para minúsculas (normalização de case)
    2. Tokenização (separação em palavras individuais)
    3. Filtragem alfanumérica (remove pontuação e símbolos)
    
    Args:
        text (str): Texto bruto a ser processado
        
    Returns:
        list: Lista de tokens limpos e normalizados
        
    Note:
        A remoção de stopwords será feita posteriormente pelo TfidfVectorizer
        para manter compatibilidade com o scikit-learn
    """
    logger.info(f"Pré-processando texto: {text[:30]}...")  # Log do início do texto
    text_lower = text.lower()  # Normalização: "Machine" -> "machine"
    tokens = nltk.word_tokenize(text_lower)  # Tokenização: "machine learning" -> ["machine", "learning"]
    
    # Filtro alfanumérico: remove pontuação mas preserva palavras válidas
    # Exemplo: ["machine", "learning", ".", "!"] -> ["machine", "learning"]
    logger.info(f"Tokens gerados: {tokens}")
    return [word for word in tokens if word.isalnum()]

# ===============================================================================
# 4. PRÉ-PROCESSAMENTO DO CORPUS COMPLETO
# ===============================================================================
# Processa todos os documentos e reconstrói como strings limpas
# O TfidfVectorizer do scikit-learn espera strings, não listas de tokens
preprocessed_docs = []
for doc in documents:
    tokens = preprocess(doc)  # Aplica pré-processamento: tokenização + limpeza
    # Reconstrói como string: ["machine", "learning"] -> "machine learning"
    preprocessed_docs.append(" ".join(tokens))

logger.info(f"Pré-processamento concluído: {len(preprocessed_docs)} documentos processados")

# ===============================================================================
# 5. CONFIGURAÇÃO E TREINAMENTO DO VECTORIZER TF-IDF
# ===============================================================================
logger.info("=== 1. Configuração do Vectorizer e Fit/Transform ===")

# Carrega stopwords em português para filtrar palavras irrelevantes
# Stopwords: palavras comuns que não agregam significado semântico (de, da, que, para, etc.)
stop_words_pt = stopwords.words('portuguese')

# Configuração do TF-IDF Vectorizer com parâmetros otimizados
vectorizer = TfidfVectorizer(
    stop_words=stop_words_pt,              # Remove palavras irrelevantes em português
    tokenizer=lambda x: x.split(),         # Usa nosso pré-processamento (tokens já limpos)
    token_pattern=None                     # Desabilita regex padrão (usamos tokenizer customizado)
)

# Treinamento do modelo: cria vocabulário e calcula pesos TF-IDF
# fit_transform executa duas operações:
# 1. fit(): constrói o vocabulário a partir do corpus
# 2. transform(): converte documentos em vetores TF-IDF
tfidf_matrix = vectorizer.fit_transform(preprocessed_docs)

# Informações sobre a matriz resultante
num_docs, num_terms = tfidf_matrix.shape
logger.info(f"Shape da Matriz TF-IDF: {num_docs} documentos, {num_terms} termos únicos")
logger.info("✅ Matriz TF-IDF criada com sucesso!")
logger.info(f"   - Cada documento é representado por um vetor de {num_terms} dimensões")
logger.info("   - Matriz esparsa: armazena apenas valores não-zero para eficiência")

# ===============================================================================
# 6. FUNÇÃO DE BUSCA E RANQUEAMENTO (CORE DO SISTEMA DE RECUPERAÇÃO)
# ===============================================================================
def search_tfidf(query, vectorizer, tfidf_matrix, top_n=5):
    """
    Implementa o algoritmo de busca vetorial usando similaridade do cosseno.
    
    Processo de Busca:
    1. Pré-processa a query (mesmo pipeline dos documentos)
    2. Transforma query em vetor TF-IDF usando vocabulário existente
    3. Calcula similaridade do cosseno entre query e todos os documentos
    4. Ranqueia resultados por relevância (score decrescente)
    
    Args:
        query (str): Consulta do usuário em linguagem natural
        vectorizer (TfidfVectorizer): Modelo TF-IDF já treinado
        tfidf_matrix (sparse matrix): Matriz com vetores TF-IDF dos documentos
        top_n (int): Número máximo de resultados a retornar
        
    Returns:
        list: Lista de tuplas (índice_documento, score_similaridade) ordenada por relevância
    """
    # ETAPA 1: Pré-processamento da query (mesma normalização dos documentos)
    processed_query = [" ".join(preprocess(query))]
    
    # ETAPA 2: Vetorização da query usando vocabulário já construído
    # transform() (não fit_transform!) usa o vocabulário existente
    query_vector = vectorizer.transform(processed_query)
    
    # ETAPA 3: Cálculo de Similaridade do Cosseno
    # Compara o vetor da query com cada documento do corpus
    # Resultado: matriz 2D de shape (1, num_documentos)
    similarities_matrix = cosine_similarity(query_vector, tfidf_matrix)
    
    # ETAPA 4: Conversão para array 1D para processamento
    similarities = similarities_matrix.flatten()  # (1, n) -> (n,)
    
    # ETAPA 5: Associação de índices para tracking dos documentos originais
    # enumerate cria pares (índice_documento, score_similaridade)
    indexed_similarities = enumerate(similarities)
    
    # ETAPA 6: Ranqueamento por relevância (score decrescente)
    # key=lambda x: x[1] ordena pelo score (segundo elemento da tupla)
    # reverse=True coloca scores mais altos primeiro (mais relevantes)
    results = sorted(indexed_similarities, key=lambda x: x[1], reverse=True)
    
    # ETAPA 7: Retorna apenas os Top-N mais relevantes
    return results[:top_n]

# ===============================================================================
# 7. EXECUÇÃO DO SISTEMA DE BUSCA
# ===============================================================================

# Query de teste: simulação de uma busca real do usuário
query_text = "machine learning ajuda a tomar decisões"

logger.info(f"--- 2. Resultados da Busca para a Query: '{query_text}' ---")
logger.info("🔍 Processando consulta...")

# Executa busca e recupera os 3 documentos mais relevantes
top_results = search_tfidf(query_text, vectorizer, tfidf_matrix, top_n=3)

# ===============================================================================
# 8. APRESENTAÇÃO DOS RESULTADOS RANQUEADOS
# ===============================================================================
logger.info("\n📊 [Documentos Ranqueados por Similaridade do Cosseno]:")

for rank, (doc_index, score) in enumerate(top_results):
    # Formatação clara dos resultados
    logger.info(f"--- Rank {rank + 1} (Score: {score:.4f}) ---")
    logger.info(f"Documento {doc_index}: {documents[doc_index]}")
    
    # Análise do score para contexto educacional  
    if score > 0.5:
        relevance = "🎯 ALTA relevância"
    elif score > 0.1:
        relevance = "⚡ MÉDIA relevância"  
    else:
        relevance = "📉 BAIXA relevância"
    
    logger.info(f"   {relevance} - Score: {score:.4f}")
    logger.info("-" * 80)

logger.info("\n✅ Execução concluída com sucesso!")
logger.info("\n💡 Análise dos Resultados:")
logger.info("   • Score próximo de 1.0: Alta similaridade semântica")
logger.info("   • Score próximo de 0.0: Baixa similaridade semântica") 
logger.info("   • O algoritmo TF-IDF capturou termos-chave da query nos documentos relevantes")

# ===============================================================================
# 9. INFORMAÇÕES ADICIONAIS PARA DEBUG/ANÁLISE (OPCIONAL)
# ===============================================================================
# Funções de debug disponíveis (descomente conforme necessário):
# 
# def show_debug_info():
#     """Exibe informações detalhadas sobre o modelo e processamento"""
#     logger.info(f"🔧 [Debug Info]")
#     logger.info(f"Vocabulário total: {len(vectorizer.get_feature_names_out())} termos únicos")
#     logger.info(f"Top 10 termos do vocabulário: {list(vectorizer.get_feature_names_out()[:10])}")
#     logger.info(f"Query pré-processada: {' '.join(preprocess(query_text))}")
#     
#     # Estatísticas da matriz TF-IDF
#     density = tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])
#     logger.info(f"Densidade da matriz: {density:.4f} ({density*100:.2f}% de valores não-zero)")
#
# Descomente a linha abaixo para executar o debug:
# show_debug_info()