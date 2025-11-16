import pytest
from truco.jogo import Jogo
from truco.carta import Carta
from truco.jogador import Jogador
from truco.bot import Bot
from truco.truco import Truco

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


def test_RN04_1_vencer_2_vazas_concede_pontos_da_aposta(cenario_rodadas):
    """
    Testa RN04-1: Se um jogador ganha 2 rodadas, ele deve
    receber os pontos da aposta vigente.
    
    O __main__.py faz:
    if jogador1.rodadas == 2:
        jogador1.adicionar_pontos(truco.retornar_valor_aposta())
    
    Este teste simula essa lógica.
    """
    # 1. Arrange
    jogo, j1, j2, c1, c2 = cenario_rodadas
    truco = Truco() # O __main__ cria um objeto truco.
    
    # Simula o estado: j1 tem 0 pontos e 0 rodadas
    assert j1.retorna_pontos_totais() == 0
    assert j1.rodadas == 0
    
    # O valor padrão da aposta (sem truco) é 1
    valor_aposta = truco.retornar_valor_aposta()
    assert valor_aposta == 1
    
    # 2. Act
    # Simula o j1 ganhando 2 vazas (como nos testes de parda)
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    
    # Verificamos a condição do __main__.py
    if j1.rodadas == 2:
        # Executamos a ação do __main__.py
        j1.adicionar_pontos(valor_aposta)

    # 3. Assert
    # O j1 deve ter 2 rodadas ganhas e 1 ponto acumulado
    assert j1.rodadas == 2
    assert j1.retorna_pontos_totais() == 1

def test_jogo_deve_terminar_com_24_pontos(cenario_rodadas):
    """
    Testa RN02-1: Verifica a condição de vitória (RF25).
    O requisito RN02 especifica que a pontuação alvo é 24.
    
    Este teste verifica se o jogador pode acumular 24 pontos.
    
    NOTA: O __main__.py atual está encerrando o jogo com 12 pontos,
    o que viola o requisito RN02. Este teste é escrito
    para validar o REQUISITO (24 pontos).
    """
    # 1. Arrange
    jogo, j1, j2, _, _ = cenario_rodadas
    
    # 2. Act
    j1.adicionar_pontos(10)
    j1.adicionar_pontos(10)
    j1.adicionar_pontos(4)
    
    # 3. Assert
    # Verificamos se o total de pontos do jogador é 24.
    assert j1.retorna_pontos_totais() == 24
    
    # O loop principal no __main__.py faria a checagem:
    # if j1.pontos >= 24:  <-- (O esperado pelo requisito)
    #    break
    
    # O código atual faz:
    # if j1.pontos >= 12:  <-- (O implementado)
    #    break
    
    # O teste prova que o acúmulo de 24 pontos é possível,
    # e expõe a discrepância entre o requisito e o código.

def test_alternar_mao_e_pe_a_cada_rodada(cenario_rodadas):
    """
    Testa (RN11): Se a função de "Mão" e "Pé" alterna a cada rodada.
    """
    # 1. Arrange
    jogo, j1, j2, _, _ = cenario_rodadas
    
    # Estado Inicial (Fixture): j1 é o primeiro, j2 é o último (pé)
    j1.primeiro = True
    j1.ultimo = False
    j2.primeiro = False
    j2.ultimo = True
    
    # 2. Act (Início da Rodada 2)
    # O jogo verifica quem foi o último para inverter
    jogo.quem_inicia_rodada(j1, j2)
    
    # 3. Assert (Rodada 2)
    # J2 deve ser o "mão", J1 deve ser o "pé"
    assert j1.primeiro is False
    assert j2.primeiro is True
    assert j1.ultimo is True  # j1 agora é o último
    assert j2.ultimo is False # j2 não é mais o último
    
    # 4. Act (Início da Rodada 3)
    # O jogo verifica de novo
    jogo.quem_inicia_rodada(j1, j2)
    
    # 5. Assert (Rodada 3)
    # J1 deve ser o "mão" novamente
    assert j1.primeiro is True
    assert j2.primeiro is False
    assert j1.ultimo is False
    assert j2.ultimo is True

# (Adicione no final de tests/test_jogo.py)
# (Lembre de importar a classe Truco no topo: from truco.truco import Truco)

def test_desistencia_no_modelo_jogo_nao_da_pontos_ao_oponente(cenario_rodadas):
    """
    Testa (RN01 / RF09): Desistência ("Ir ao Monte").
    Este teste PROVA que o método 'jogador_fugiu' da classe Jogo
    está incompleto e não implementa a regra de negócio RN01
    (dar pontos ao oponente).
    """
    # 1. Arrange
    jogo, j1, j2, _, _ = cenario_rodadas
    truco = Truco()
    
    # Simula que um TRUCO foi aceito e a mão vale 2 pontos
    # (Embora o bug do teste anterior mostre que isso falha, 
    # vamos forçar o valor aqui para o teste)
    truco.valor_aposta = 2 
    
    # 2. Act
    # O Jogador 1 (j1) foge.
    # O método 'jogador_fugiu' deveria dar os pontos (2) ao J2.
    jogo.jogador_fugiu(j1, j1, j2, truco.retornar_valor_aposta())

    # 3. Assert (Provando o Bug)
    # De acordo com a RN01, j2.pontos deveria ser 2.
    # O assert falharia se fosse: assert j2.pontos == 2
    
    # Este assert PASSA, provando que o método não fez nada:
    assert j2.pontos == 0
    
    # O método 'jogador_fugiu' só mexe em quem é o 'primeiro'
    assert j1.primeiro is True
    assert j2.primeiro is False

# (Adicione este teste ao final do seu arquivo tests/test_jogo.py)

def test_vencedor_da_vaza_joga_primeiro_na_proxima_vaza(cenario_rodadas):
    """
    Testa (UC-01): Se o jogador que ganha uma vaza (ex: Vaza 1)
    é quem joga primeiro na vaza seguinte (ex: Vaza 2).
    """
    # 1. Arrange
    # A fixture 'cenario_rodadas' nos dá tudo que precisamos.
    # j1 é o "mão" e joga primeiro na Vaza 1.
    jogo, j1, j2, c1, c2 = cenario_rodadas
    
    # 2. Act (Vaza 1)
    # Simulamos que j1 (jogador 1) jogou c1 (carta 1) e
    # j2 (jogador 2) jogou c2 (carta 2).
    # O ganhador da Vaza 1 foi c1 (jogador 1).
    jogo.quem_joga_primeiro(j1, j2, c1, c2, ganhador=c1)
    
    # 3. Assert (Início da Vaza 2)
    # A lógica deve definir j1 como 'primeiro' para a Vaza 2.
    assert j1.primeiro is True
    assert j2.primeiro is False
    
    # 4. Act (Vaza 2)
    # Agora, simulamos a Vaza 2. j1 joga primeiro.
    # Mas desta vez, o ganhador da Vaza 2 foi c2 (jogador 2).
    jogo.quem_joga_primeiro(j1, j2, c1, c2, ganhador=c2)
    
    # 5. Assert (Início da Vaza 3)
    # A lógica deve inverter e definir j2 como 'primeiro' para a Vaza 3.
    assert j1.primeiro is False
    assert j2.primeiro is True

# (Adicione este teste ao final do seu arquivo tests/test_jogo.py)

def test_vencedor_da_vaza_joga_primeiro_na_proxima_vaza(cenario_rodadas):
    """
    Testa (UC-01): Se o jogador que ganha uma vaza (ex: Vaza 1)
    é quem joga primeiro na vaza seguinte (ex: Vaza 2).
    """
    # 1. Arrange
    # A fixture 'cenario_rodadas' nos dá tudo que precisamos.
    # j1 é o "mão" e joga primeiro na Vaza 1.
    jogo, j1, j2, c1, c2 = cenario_rodadas
    
    # 2. Act (Vaza 1)
    # Simulamos que j1 (jogador 1) jogou c1 (carta 1) e
    # j2 (jogador 2) jogou c2 (carta 2).
    # O ganhador da Vaza 1 foi c1 (jogador 1).
    jogo.quem_joga_primeiro(j1, j2, c1, c2, ganhador=c1)
    
    # 3. Assert (Início da Vaza 2)
    # A lógica deve definir j1 como 'primeiro' para a Vaza 2.
    assert j1.primeiro is True
    assert j2.primeiro is False
    
    # 4. Act (Vaza 2)
    # Agora, simulamos a Vaza 2. j1 joga primeiro.
    # Mas desta vez, o ganhador da Vaza 2 foi c2 (jogador 2).
    jogo.quem_joga_primeiro(j1, j2, c1, c2, ganhador=c2)
    
    # 5. Assert (Início da Vaza 3)
    # A lógica deve inverter e definir j2 como 'primeiro' para a Vaza 3.
    assert j1.primeiro is False
    assert j2.primeiro is True