# nome_arquivo: aula_3_agente_langgraph.py

import operator
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

# Carrega variáveis
load_dotenv()


# --- 1. Definição do Estado Compartilhado ---
class AgentState(TypedDict):
    # Annotated[..., operator.add] significa que novas mensagens são adicionadas à lista existente (append)
    messages: Annotated[list[BaseMessage], operator.add]
    cliente: dict
    intencao: str
    info_fatura: str
    status_cancelamento: str
    oferta: str


# --- 2. Funções de Negócio (Mockadas/Simuladas) ---
def mock_api_fatura(cliente_id: str) -> str:
    return "R$ 250,00 com vencimento em 15/10."


def mock_api_cancelamento(cliente_id: str) -> str:
    return "Cancelamento processado com sucesso."


# --- 3. Nós do Grafo (Nodes) ---
# Cada nó recebe o estado, processa e retorna um dicionário com as chaves a serem atualizadas.


def node_classificador(state: AgentState):
    """Analisa a última mensagem e define a intenção (simplificado via keywords para demo)."""
    # Em produção, usaríamos a LLM aqui para classificar
    content = state["messages"][-1].content

    # Garante que content é uma string antes de chamar lower()
    if isinstance(content, list):
        # Se content for uma lista, junta os elementos em uma string
        last_msg = " ".join(str(item) for item in content).lower()
    else:
        # Se content for uma string, usa diretamente
        last_msg = str(content).lower()

    if "fatura" in last_msg:
        return {"intencao": "fatura"}
    elif "cancelar" in last_msg:
        return {"intencao": "cancelar"}
    else:
        return {"intencao": "faq"}


def node_consultar_fatura(state: AgentState):
    print(">>> Nó: Consultando Fatura")
    info = mock_api_fatura(state["cliente"]["id"])
    return {"info_fatura": info}


def node_resumir_fatura(state: AgentState):
    print(">>> Nó: Resumindo Fatura")
    info = state["info_fatura"]
    msg = f"Sua fatura atual é de {info}"
    return {"messages": [SystemMessage(content=msg)]}


def node_gerar_oferta(state: AgentState):
    print(">>> Nó: Gerando Oferta de Retenção")
    return {"oferta": "50% de desconto na próxima mensalidade"}


def node_enviar_oferta(state: AgentState):
    print(">>> Nó: Enviando Oferta")
    oferta = state["oferta"]
    msg = f"Como você é um cliente VIP, temos uma oferta: {oferta}. Deseja aceitar?"
    return {"messages": [SystemMessage(content=msg)]}


def node_registrar_cancelamento(state: AgentState):
    print(">>> Nó: Registrando Cancelamento")
    status = mock_api_cancelamento(state["cliente"]["id"])
    return {"status_cancelamento": status, "messages": [SystemMessage(content=status)]}


def node_responder_faq(state: AgentState):
    print(">>> Nó: Responder FAQ")
    return {
        "messages": [
            SystemMessage(
                content="Sou um assistente virtual, posso ajudar com faturas ou cancelamentos."
            )
        ]
    }


# --- 4. Lógica Condicional (Roteamento) ---


def route_intencao(state: AgentState):
    return state["intencao"]


def route_vip_check(state: AgentState):
    if state["cliente"].get("vip", False):
        return "eh_vip"
    return "normal"


# --- 5. Construção do Grafo ---

workflow = StateGraph(AgentState)

# Adicionando Nós
workflow.add_node("classificador", node_classificador)
workflow.add_node("consultar_fatura", node_consultar_fatura)
workflow.add_node("resumir_fatura", node_resumir_fatura)
workflow.add_node("gerar_oferta", node_gerar_oferta)
workflow.add_node("enviar_oferta", node_enviar_oferta)
workflow.add_node("registrar_cancelamento", node_registrar_cancelamento)
workflow.add_node("responder_faq", node_responder_faq)

# Definindo ponto de entrada
workflow.set_entry_point("classificador")

# Adicionando Arestas Condicionais (Onde a mágica acontece)
workflow.add_conditional_edges(
    "classificador",
    route_intencao,
    {
        "fatura": "consultar_fatura",
        "cancelar": "gerar_oferta",  # Primeiro vai para lógica de VIP check (ver abaixo)
        "faq": "responder_faq",
    },
)

# Aresta normal
workflow.add_edge("consultar_fatura", "resumir_fatura")
workflow.add_edge("resumir_fatura", END)
workflow.add_edge("responder_faq", END)

# Lógica específica para cancelamento com verificação VIP
# Aqui, ao invés de ir direto do classificador, criamos uma lógica de decisão
# Nota: No vídeo, a lógica VIP é aplicada. Vamos ajustar a aresta condicional 'cancelar' para refletir isso.
# Vamos redefinir a aresta condicional de saída do classificador para 'cancelar' apontar para um nó de decisão ou usar logica direta.
# Para simplificar conforme o vídeo, assumimos que o fluxo 'cancelar' cai na decisão de oferta/cancelamento.


def route_cancelamento_vip(state: AgentState):
    """Roteamento para cancelamento considerando status VIP"""
    if state["intencao"] == "cancelar" and state["cliente"]["vip"]:
        return "vip"
    elif state["intencao"] == "cancelar":
        return "cancelar_direto"
    else:
        return state["intencao"]


workflow.add_conditional_edges(
    "classificador",  # Na verdade, o vídeo sugere uma lógica onde o 'cancelar' verifica VIP
    route_cancelamento_vip,
    {
        "fatura": "consultar_fatura",
        "vip": "gerar_oferta",
        "cancelar_direto": "registrar_cancelamento",
        "faq": "responder_faq",
    },
)
# Nota de correção: No código original do vídeo, ele usa nós de decisão.
# Ajustei acima para usar a lambda complexa para simular o roteamento do video num único passo.

workflow.add_edge("gerar_oferta", "enviar_oferta")
workflow.add_edge("enviar_oferta", END)  # Fim por enquanto
workflow.add_edge("registrar_cancelamento", END)

# Compilação
app = workflow.compile()

# --- 6. Execução ---
if __name__ == "__main__":
    print("--- Teste 1: Cliente VIP querendo cancelar ---")
    inputs_vip: AgentState = {
        "messages": [HumanMessage(content="Quero cancelar minha assinatura")],
        "cliente": {"id": "123", "vip": True},
        "intencao": "",
        "info_fatura": "",
        "oferta": "",
        "status_cancelamento": "",
    }

    for output in app.stream(inputs_vip):
        pass  # O print está dentro dos nós

    print("\n--- Teste 2: Cliente Normal querendo fatura ---")
    inputs_normal: AgentState = {
        "messages": [HumanMessage(content="Qual o valor da minha fatura?")],
        "cliente": {"id": "456", "vip": False},
        "intencao": "",
        "info_fatura": "",
        "oferta": "",
        "status_cancelamento": "",
    }

    for output in app.stream(inputs_normal):
        pass
