import random
import math

# --- 1. Representação de Dados ---
# Cada "cidade" ou ponto de entrega é uma tupla de coordenadas (x, y).
# Exemplo de pontos de entrega:
cidades = {
    "A": (60, 200),
    "B": (180, 200),
    "C": (80, 180),
    "D": (140, 180),
    "E": (20, 160),
    "F": (100, 160),
    "G": (200, 160),
    "H": (140, 120),
    "I": (40, 120),
    "J": (120, 80)
}

# Lista de nomes das cidades para fácil manipulação
nomes_cidades = list(cidades.keys())

# --- 2. Funções Essenciais ---

def distancia(cidade1, cidade2):
    """Calcula a distância euclidiana entre duas cidades."""
    x1, y1 = cidades[cidade1]
    x2, y2 = cidades[cidade2]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def calcular_aptidao(rota):
    """Calcula a aptidão de uma rota (o inverso da distância total)."""
    distancia_total = 0
    for i in range(len(rota) - 1):
        distancia_total += distancia(rota[i], rota[i+1])
    # Adiciona a distância de volta ao ponto de partida
    distancia_total += distancia(rota[-1], rota[0])
    
    # A aptidão é o inverso da distância: quanto menor a distância, maior a aptidão.
    # Evita divisão por zero.
    if distancia_total == 0:
        return float('inf')
    return 1 / distancia_total

def selecao(populacao, num_selecionados):
    """Seleciona as rotas mais aptas da população."""
    populacao_ordenada = sorted(populacao, key=calcular_aptidao, reverse=True)
    return populacao_ordenada[:num_selecionados]

def crossover(parente1, parente2):
    """Cria um novo descendente a partir de dois pais (método de cruzamento de ordem)."""
    tamanho = len(parente1)
    filho = [""] * tamanho
    
    # Define os pontos de corte
    start = random.randint(0, tamanho - 1)
    end = random.randint(start + 1, tamanho)
    
    # Copia o segmento do primeiro pai para o filho
    filho[start:end] = parente1[start:end]
    
    # Preenche o restante do filho com os genes do segundo pai
    # que ainda não foram usados.
    j = 0
    for i in range(tamanho):
        if not filho[i]:
            while parente2[j] in filho:
                j += 1
            filho[i] = parente2[j]
            j += 1
            
    return filho

def mutacao(rota, taxa_mutacao):
    """Aplica uma mutação aleatória na rota (troca de dois pontos)."""
    for _ in range(len(rota)):
        if random.random() < taxa_mutacao:
            idx1, idx2 = random.sample(range(len(rota)), 2)
            rota[idx1], rota[idx2] = rota[idx2], rota[idx1]
    return rota

# --- 3. Função Principal do Algoritmo Genético ---

def algoritmo_genetico_tsp(tamanho_populacao, num_geracoes, taxa_mutacao):
    """Executa o algoritmo genético para encontrar a melhor rota."""
    
    # 3.1. Inicialização da População
    populacao = [random.sample(nomes_cidades, len(nomes_cidades)) for _ in range(tamanho_populacao)]
    
    melhor_rota = None
    melhor_distancia = float('inf')
    
    # 3.2. Loop de Gerações
    for geracao in range(num_geracoes):
        # 3.3. Avaliação da Aptidão
        distancias = [1 / calcular_aptidao(rota) for rota in populacao]
        
        # 3.4. Atualização da Melhor Rota Global
        distancia_atual = min(distancias)
        if distancia_atual < melhor_distancia:
            melhor_distancia = distancia_atual
            melhor_rota = populacao[distancias.index(melhor_distancia)]
            print(f"Geração {geracao}: Nova melhor rota encontrada! Distância: {melhor_distancia:.2f}")

        # 3.5. Criação da Próxima Geração
        nova_geracao = []
        
        # Elitismo: Mantém os 10% melhores indivíduos da população anterior.
        num_elitismo = int(tamanho_populacao * 0.1)
        selecionados = selecao(populacao, num_elitismo)
        nova_geracao.extend(selecionados)
        
        # Criação de novos indivíduos por Crossover e Mutação
        while len(nova_geracao) < tamanho_populacao:
            pai1 = random.choice(selecionados)
            pai2 = random.choice(selecionados)
            
            filho = crossover(pai1, pai2)
            filho = mutacao(filho, taxa_mutacao)
            nova_geracao.append(filho)
            
        populacao = nova_geracao
        
    return melhor_rota, melhor_distancia

# --- 4. Execução e Parâmetros ---

if __name__ == "__main__":
    tamanho_populacao = 100
    num_geracoes = 500
    taxa_mutacao = 0.02
    
    print("Iniciando otimização de rotas...")
    melhor_rota, distancia_otimizada = algoritmo_genetico_tsp(
        tamanho_populacao=tamanho_populacao,
        num_geracoes=num_geracoes,
        taxa_mutacao=taxa_mutacao
    )
    
    print("\n--- Resultados Finais ---")
    print(f"Melhor Rota Encontrada: {' -> '.join(melhor_rota)} -> {melhor_rota[0]}")
    print(f"Distância Total da Rota: {distancia_otimizada:.2f} unidades")