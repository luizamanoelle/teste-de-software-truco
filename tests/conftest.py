# Salve como: tests/conftest.py
# Este arquivo centraliza todas as fixtures (cenários de teste)
# para garantir que cada teste seja independente.

import pytest
from truco.jogador import Jogador
from truco.bot import Bot
from truco.baralho import Baralho
from truco.carta import Carta
from truco.truco import Truco
from truco.envido import Envido
from truco.flor import Flor
from truco.jogo import Jogo
from truco.interface import Interface

# --- Mocks (Simuladores) ---

@pytest.fixture
def mock_cbr():
    """Simula o CBR, configurado para sempre 'Aceitar' por padrão."""
    class MockCBR:
        
        # CORREÇÃO: Renomeie 'truco' para 'avaliar_truco'
        def avaliar_truco(self, *args): 
            return 1  # 1 = Aceitar
        
        # CORREÇÃO: Renomeie 'envido' para 'avaliar_envido'
        def avaliar_envido(self, *args): 
            return 1  # 1 = Aceitar
        
        def jogar_carta(self, *args):
            return 0 # Sempre joga a primeira carta

    return MockCBR()

@pytest.fixture
def mock_dados():
    """Simula a classe de Dados, não faz nada."""
    class MockDados:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    return MockDados()

@pytest.fixture
def iface():
    """Fornece uma instância real da Interface."""
    return Interface()

# --- Fixtures de Cenário Base ---

@pytest.fixture
def cenario_base(iface, mock_cbr, mock_dados):
    """
    Cenário mais básico com jogadores, bot e mocks.
    Cada teste que usar esta fixture receberá instâncias NOVAS.
    """
    j1 = Jogador("Humano")
    j2 = Bot("Robô")
    return j1, j2, iface, mock_cbr, mock_dados

@pytest.fixture
def cenario_distribuicao():
    """Cenário para testar a distribuição de cartas."""
    baralho = Baralho()
    j1 = Jogador("Humano")
    bot = Bot("Robô")
    return baralho, j1, bot

# --- Fixtures de Cenários de Jogo e Apostas ---

@pytest.fixture
def cenario_rodadas(cenario_base):
    """Cenário para testar a lógica de vazas (rodadas) e pardas."""
    j1, j2, iface, mock_cbr, mock_dados = cenario_base
    jogo = Jogo()
    
    # Define j1 como "mão"
    j1.primeiro = True
    j2.primeiro = False
    
    # Cartas genéricas para os testes
    c1 = Carta(7, "COPAS")
    c2 = Carta(6, "OUROS")
    
    return jogo, j1, j2, c1, c2

@pytest.fixture
def cenario_truco(cenario_base):
    """Cenário limpo para testes de Truco."""
    j1, j2, iface, mock_cbr, mock_dados = cenario_base
    truco = Truco()
    return truco, j1, j2, mock_cbr, mock_dados

@pytest.fixture
def cenario_envido(cenario_base):
    """Cenário para testes de Envido, com mãos e pontos pré-definidos."""
    j1, j2, iface, mock_cbr, mock_dados = cenario_base
    envido = Envido()
    
    # J1 (Humano) tem 33 de envido
    j1.mao = [Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")]
    j1.envido = j1.calcula_envido(j1.mao)  # 33
    
    # J2 (Bot) tem 25
    j2.mao = [Carta(5, "COPAS"), Carta(1, "COPAS"), Carta(3, "BASTOS")]
    j2.envido = j2.calcula_envido(j2.mao)  # 25
    
    # Define o J1 como "mão"
    j1.primeiro = True
    j2.primeiro = False
    
    return envido, j1, j2, mock_cbr, mock_dados, iface

@pytest.fixture
def cenario_flor(cenario_base):
    """Cenário limpo para testes de Flor."""
    j1, j2, iface, mock_cbr, mock_dados = cenario_base
    flor = Flor()
    # As mãos serão definidas dentro de cada teste
    return flor, j1, j2, iface

@pytest.fixture
def cenario_regras_invalidas(cenario_base):
    """Cenário completo para testar interações inválidas entre apostas."""
    j1, j2, iface, mock_cbr, mock_dados = cenario_base
    truco = Truco()
    envido = Envido()
    flor = Flor()
    return j1, j2, truco, envido, flor, iface, mock_cbr, mock_dados

@pytest.fixture
def cenario_main(monkeypatch):
    """
    Recria o ambiente de objetos globais que o __main__.py espera.
    Isso nos permite testar as funções turno_do_humano e turno_do_bot.
    """
    # 1. Cria todas as instâncias que o __main__ cria
    baralho = Baralho()
    
    # Mock do CBR e Dados (para não depender de arquivos)
    class MockCBR:
        def truco(self, *args): return 1 # Aceitar (Mude de 'truco')
        def envido(self, *args): return 1 # Aceitar (Mude de 'envido')
        def carta(self, *args): return 0
    
    class MockDados:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None

    cbr = MockCBR()
    dados = MockDados()
    interface = Interface()
    truco = Truco()
    flor = Flor()
    envido = Envido()
    
    # 2. Cria os jogadores
    jogador1 = Jogador("Humano")
    jogador2 = Bot("Robô")
    
    # 3. Importa as funções do __main__ (truque para "injeta" as variáveis)
    # Precisamos "enganar" o __main__ para que ele use nossos objetos
    
    # Para este teste, vamos focar em testar o FLUXO, não o __main__
    # Vamos re-implementar o turno_do_humano de forma testável
    
    # Devolve todos os objetos para o teste
    return baralho, cbr, dados, interface, truco, flor, envido, jogador1, jogador2
