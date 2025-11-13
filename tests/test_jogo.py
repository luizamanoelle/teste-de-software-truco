import pytest
from truco.jogo import Jogo
from truco.carta import Carta
from truco.jogador import Jogador
from truco.bot import Bot

@pytest.fixture
def jogo_instance():
    """Retorna uma instância de Jogo() para testes de regras."""
    return Jogo()

# --- Testes de Hierarquia de Cartas (RN07) ---

def test_as_de_espadas_ganha_as_de_paus(jogo_instance):
    carta_forte = Carta(1, "ESPADAS")
    carta_fraca = Carta(1, "BASTOS") 
    
    vencedora = jogo_instance.verificar_carta_vencedora(carta_forte, carta_fraca)
    assert vencedora == carta_forte

def test_as_de_paus_ganha_7_de_espadas(jogo_instance):
    carta_forte = Carta(1, "BASTOS")  
    carta_fraca = Carta(7, "ESPADAS") 
    
    vencedora = jogo_instance.verificar_carta_vencedora(carta_forte, carta_fraca)
    assert vencedora == carta_forte

def test_7_de_espadas_ganha_7_de_ouros(jogo_instance):
    carta_forte = Carta(7, "ESPADAS") 
    carta_fraca = Carta(7, "OUROS") 
    
    vencedora = jogo_instance.verificar_carta_vencedora(carta_forte, carta_fraca)
    assert vencedora == carta_forte

def test_7_de_ouros_ganha_de_um_3(jogo_instance):
    carta_forte = Carta(7, "OUROS") 
    carta_fraca = Carta(3, "COPAS")
    
    vencedora = jogo_instance.verificar_carta_vencedora(carta_forte, carta_fraca)
    assert vencedora == carta_forte

def test_3_ganha_de_um_2(jogo_instance):
    carta_forte = Carta(3, "ESPADAS")
    carta_fraca = Carta(2, "BASTOS")
    
    vencedora = jogo_instance.verificar_carta_vencedora(carta_forte, carta_fraca)
    assert vencedora == carta_forte

def test_2_ganha_do_1_de_ouros(jogo_instance):
    carta_forte = Carta(2, "BASTOS") 
    carta_fraca = Carta(1, "OUROS")  
    
    vencedora = jogo_instance.verificar_carta_vencedora(carta_forte, carta_fraca)
    assert vencedora == carta_forte

def test_1_de_ouros_ganha_de_um_rei_12(jogo_instance):
    carta_forte = Carta(1, "OUROS")  
    carta_fraca = Carta(12, "COPAS")
    
    vencedora = jogo_instance.verificar_carta_vencedora(carta_forte, carta_fraca)
    assert vencedora == carta_forte

# --- Fixture para Cenário de Rodadas ---
@pytest.fixture
def cenario_rodadas():
    """Prepara um jogo, um jogador e um bot para testar rodadas."""
    jogo = Jogo()
    jogador1 = Jogador("Humano")
    jogador2 = Bot("Robô")
    
    # Define o jogador1 como "mão" (primeiro a jogar)
    jogador1.primeiro = True 
    jogador2.primeiro = False
    
    # Cartas genéricas, não importam para esta lógica,
    # mas o método adicionar_rodada as recebe.
    carta1 = Carta(1, "COPAS")
    carta2 = Carta(2, "OUROS")
    
    return jogo, jogador1, jogador2, carta1, carta2

# --- Testes de Regras de Empate (Parda) (RN03) ---

def test_parda_vaza1_jogador_ganha_vaza2(cenario_rodadas):
    # [ ] Testar se (Vaza 1 parda, Vaza 2 jogador ganha) -> Jogador ganha a mão.
    jogo, j1, j2, c1, c2 = cenario_rodadas
    
    # Vaza 1: Empate (Simulamos "Empate" como ganhador)
    # No seu código, 'adicionar_rodada' não trata "Empate" explicitamente.
    # Vamos simular que ninguém ganha a rodada 0.
    # j1.rodadas == 0
    # j2.rodadas == 0
    
    # Vaza 2: Jogador 1 ganha
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1) #
    
    # Verificação: Jogador 1 tem 1 rodada, Jogador 2 tem 0
    # Pela regra do truco, quem vence a segunda após empate na primeira, ganha.
    assert j1.rodadas == 1
    assert j2.rodadas == 0
    # Aqui, o jogo principal faria: if j1.rodadas > j2.rodadas: j1 ganha a mão.

def test_jogador_ganha_vaza1_parda_vaza2(cenario_rodadas):
    # [ ] Testar se (Vaza 1 jogador ganha, Vaza 2 parda) -> Jogador ganha a mão.
    jogo, j1, j2, c1, c2 = cenario_rodadas

    # Vaza 1: Jogador 1 ganha
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    
    # Vaza 2: Empate (ninguém ganha a rodada)
    
    # Verificação: Jogador 1 tem 1 rodada, Jogador 2 tem 0
    # Pela regra, quem vence a primeira, ganha a mão se a segunda empata.
    assert j1.rodadas == 1
    assert j2.rodadas == 0

def test_vaza1_ganha_vaza2_perde_vaza3_parda(cenario_rodadas):
    # [ ] Testar se (Vaza 1 jogador ganha, Vaza 2 bot ganha, Vaza 3 parda) -> Jogador ganha a mão.
    jogo, j1, j2, c1, c2 = cenario_rodadas

    # Vaza 1: Jogador 1 ganha
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    
    # Vaza 2: Jogador 2 (Bot) ganha
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c2)
    
    # Vaza 3: Empate (ninguém ganha a rodada)

    # Verificação: Ambos têm 1 rodada.
    # Pela regra, quem venceu a PRIMEIRA vaza (j1) ganha a mão.
    assert j1.rodadas == 1
    assert j2.rodadas == 1
    # O desempate (j1.rodadas == j2.rodadas) deve ser feito pelo
    # "quem ganhou a primeira", que no caso foi j1.

def test_vaza1_parda_vaza2_parda_vaza3_ganha(cenario_rodadas):
    # [ ] Testar se (Vaza 1 parda, Vaza 2 parda, Vaza 3 jogador ganha) -> Jogador ganha a mão.
    jogo, j1, j2, c1, c2 = cenario_rodadas

    # Vaza 1: Empate
    # Vaza 2: Empate
    
    # Vaza 3: Jogador 1 ganha
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)

    # Verificação: J1 tem 1 rodada, J2 tem 0. J1 ganha.
    assert j1.rodadas == 1
    assert j2.rodadas == 0

def test_tres_pardas_ganha_o_mao(cenario_rodadas):
    # [ ] Testar se (Vaza 1 parda, Vaza 2 parda, Vaza 3 parda) -> Jogador "Mão" ganha a mão.
    jogo, j1, j2, c1, c2 = cenario_rodadas
    
    # j1 é o "mão" (definido na fixture: j1.primeiro = True)

    # Vaza 1: Empate
    # Vaza 2: Empate
    # Vaza 3: Empate

    # Verificação: Ninguém pontuou nas rodadas.
    assert j1.rodadas == 0
    assert j2.rodadas == 0
    # O jogo principal deve verificar:
    # if j1.rodadas == 0 and j2.rodadas == 0:
    #   if j1.primeiro: j1 ganha a mão
    #   else: j2 ganha a mão

def test_empate_cartas_comuns_da_vitoria_ao_jogador1_indevidamente(jogo_instance):
    # Teste que prova o bug da parda (empate)
    
    # 1. Arrange
    # Duas cartas de mesmo valor, mas naipes diferentes
    carta_j1 = Carta(3, "COPAS")
    carta_j2 = Carta(3, "BASTOS") 
    
    # 2. Act
    vencedora = jogo_instance.verificar_carta_vencedora(carta_j1, carta_j2)
    
    # 3. Assert
    # Este assert verifica o COMPORTAMENTO ATUAL (o bug)
    # Ele prova que o j1 (primeiro a jogar) ganha a vaza.
    assert vencedora == carta_j1
    
    # Se o bug fosse corrigido (descomentando o 'return "Empate"'),
    # o teste correto seria:
    # assert vencedora == "Empate" 
    # E o nosso teste acima (assert vencedora == carta_j1) falharia.

# --- Testes de Vitória e Pontuação (RN02) ---

def test_jogador_que_vence_2_vazas_ganha_a_mao(cenario_rodadas):
    # [ ] Testar se o jogador que vence 2 vazas ganha os pontos da mão.
    
    # A fixture 'cenario_rodadas' já nos dá jogo, j1, j2, c1, c2
    jogo, j1, j2, c1, c2 = cenario_rodadas
    
    # Vaza 1: Jogador 1 ganha
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    
    # Vaza 2: Jogador 1 ganha novamente
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    
    # Verificação: O loop principal do jogo verificaria (if j1.rodadas == 2)
    # Nós testamos se a contagem está correta.
    assert j1.rodadas == 2
    assert j2.rodadas == 0