import operator
import os
from typing import Annotated, Dict, List, TypedDict, Union

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

# Bibliotecas do Ecossistema LangChain/LangGraph
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

# --- 1. Configuração Inicial ---
# Carrega variáveis de ambiente (certifique-se de ter o arquivo .env com OPENAI_API_KEY)
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("Por favor, defina a OPENAI_API_KEY no seu arquivo .env")

# Instancia o modelo LLM (pode ser GPT-3.5 ou GPT-4)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# --- 2. Definição do Estado (State) ---
# O Estado é a estrutura de dados que trafega pelo grafo.
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]  # Histórico de mensagens (append only)
    cliente: Dict  # Dados do cliente simulado
    intencao: str  # Intenção classificada (fatura, cancelamento, etc)
    info_fatura: str  # Dados recuperados de fatura
    info_cancelamento: str  # Status de cancelamento
    oferta: str  # Oferta gerada


# --- 3. Funções Mockadas (Simulando APIs Externas) ---
# Em um cenário real, estas fariam requests para seu backend.


def api_consultar_fatura(cliente_id: str) -> str:
    """Simula consulta de fatura no banco de dados."""
    return f"Fatura de R$ 150,00 vencendo em 20/09/2024 para o cliente {cliente_id}."


def api_registrar_cancelamento(cliente_id: str) -> bool:
    """Simula registro de cancelamento no CRM."""
    print(f"LOG: Cancelamento registrado para cliente {cliente_id}")
    return True


# --- 4. Nós do Grafo (Nodes) ---
# Cada função recebe o Estado atual e retorna as chaves que deseja atualizar.


def classificar_intencao(state: AgentState):
    """Nó responsável por entender o que o usuário quer."""
    messages = state["messages"]

    # Prompt do sistema para classificação
    system_prompt = """Você é um classificador de intenções de um SAC.
    Analise a conversa e classifique a intenção do usuário em uma das seguintes categorias:
    - 'fatura': O usuário quer saber sobre pagamentos ou valores.
    - 'cancelar': O usuário quer cancelar o serviço.
    - 'faq': Dúvidas gerais ou saudações.
    
    Responda APENAS com a palavra da categoria (fatura, cancelar, faq)."""

    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    intencao_detectada = response.content.strip().lower()  # type: ignore

    print(f"--- Decisão: Intenção classificada como: {intencao_detectada} ---")

    # Retorna apenas a parte do estado que mudou
    return {"intencao": intencao_detectada}


def node_consultar_fatura(state: AgentState):
    """Nó especialista em faturas."""
    print("--- Executando: Consultar Fatura ---")
    cliente_id = state["cliente"].get("id", "desconhecido")
    dados_fatura = api_consultar_fatura(cliente_id)
    return {"info_fatura": dados_fatura}


def node_registrar_cancelamento(state: AgentState):
    """Nó especialista em cancelamento."""
    print("--- Executando: Registrar Cancelamento ---")
    cliente_id = state["cliente"].get("id", "desconhecido")
    sucesso = api_registrar_cancelamento(cliente_id)
    status = "Cancelamento efetuado com sucesso." if sucesso else "Erro ao cancelar."
    return {"info_cancelamento": status}


def node_gerar_oferta(state: AgentState):
    """Nó de retenção: tenta gerar uma oferta antes de cancelar."""
    print("--- Executando: Gerar Oferta de Retenção ---")
    oferta = "Desconto de 50% na próxima fatura se você ficar!"
    return {"oferta": oferta}


def node_responder_faq(state: AgentState):
    """Nó para responder perguntas gerais."""
    print("--- Executando: Responder FAQ ---")
    response = llm.invoke(
        [SystemMessage(content="Responda educadamente à pergunta do usuário.")] + state["messages"]
    )
    return {"messages": [response]}  # Adiciona a resposta ao histórico


def node_finalizar_fatura(state: AgentState):
    """Gera a resposta final sobre a fatura."""
    info = state.get("info_fatura")
    msg = f"Aqui estão os dados: {info}"
    return {
        "messages": [HumanMessage(content=msg)]
    }  # Simplificação usando HumanMessage para retorno


def node_enviar_oferta(state: AgentState):
    """Apresenta a oferta ao usuário."""
    oferta = state.get("oferta")
    msg = f"Espere! Antes de ir, temos uma oferta: {oferta}"
    return {"messages": [HumanMessage(content=msg)]}


# --- 5. Construção do Grafo (Wiring) ---

workflow = StateGraph(AgentState)

# Adicionando os nós
workflow.add_node("classificador", classificar_intencao)
workflow.add_node("tratar_fatura", node_consultar_fatura)
workflow.add_node("finalizar_fatura", node_finalizar_fatura)
workflow.add_node("gerar_oferta", node_gerar_oferta)
workflow.add_node("enviar_oferta", node_enviar_oferta)
workflow.add_node(
    "tratar_cancelamento", node_registrar_cancelamento
)  # Em um fluxo real, viria depois da recusa da oferta
workflow.add_node("responder_faq", node_responder_faq)

# Definindo o ponto de entrada
workflow.set_entry_point("classificador")


# --- Lógica de Roteamento Condicional ---
def roteador_de_intencao(state: AgentState):
    """Função que decide para qual nó ir com base no estado 'intencao'."""
    intencao = state["intencao"]
    if intencao == "fatura":
        return "ir_fatura"
    elif intencao == "cancelar":
        return "ir_oferta"  # Tenta reter o cliente primeiro
    else:
        return "ir_faq"


# Adicionando arestas condicionais
workflow.add_conditional_edges(
    "classificador",  # Nó de origem
    roteador_de_intencao,  # Função de decisão
    {  # Mapeamento: Resultado da função -> Próximo Nó
        "ir_fatura": "tratar_fatura",
        "ir_oferta": "gerar_oferta",
        "ir_faq": "responder_faq",
    },
)

# Adicionando arestas normais (lineares)
workflow.add_edge("tratar_fatura", "finalizar_fatura")
workflow.add_edge("finalizar_fatura", END)  # Fim do fluxo

workflow.add_edge("gerar_oferta", "enviar_oferta")
workflow.add_edge(
    "enviar_oferta", END
)  # Paramos aqui para demonstração (em real, esperaria resposta do user)

workflow.add_edge("responder_faq", END)

# Compilando o grafo
app = workflow.compile()

# --- 6. Execução ---


def executar_exemplo(user_input: str):
    print(f"\n>>> USUÁRIO DIZ: '{user_input}'")

    # Estado inicial
    inputs = {
        "messages": [HumanMessage(content=user_input)],
        "cliente": {"id": "12345", "nome": "Aluno FIAP"},
        "intencao": "",
        "info_fatura": "",
        "info_cancelamento": "",
        "oferta": "",
    }

    # Executa o grafo e imprime o fluxo
    for output in app.stream(inputs):  # type: ignore
        for key, value in output.items():
            print(f"   [Nó Finalizado]: {key}")


def main():
    """Loop interativo para receber perguntas via linha de comando."""
    print("=" * 60)
    print("BEM-VINDO AO AGENTE DE SAC COM LANGGRAPH")
    print("=" * 60)
    print("Digite suas perguntas ou comandos abaixo.")
    print("Digite 'sair' ou 'exit' para encerrar.\n")

    while True:
        try:
            # Recebe input do usuário
            user_input = input(">>> Sua pergunta: ").strip()

            # Verifica se o usuário quer sair
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\nAté logo! Obrigado por usar nosso SAC.")
                break

            # Valida se o input está vazio
            if not user_input:
                print("Por favor, digite uma pergunta válida.\n")
                continue

            # Executa o exemplo com o input do usuário
            executar_exemplo(user_input)

        except KeyboardInterrupt:
            print("\n\nEncerrando... Até logo!")
            break
        except Exception as e:
            print(f"Erro ao processar sua pergunta: {e}\n")


# Testes e execução
if __name__ == "__main__":
    main()
