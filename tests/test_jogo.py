import pytest
from truco.jogo import Jogo
from truco.carta import Carta
from truco.truco import Truco
from truco.jogador import Jogador
from truco.bot import Bot
from truco.interface import Interface

# --- Testes de Hierarquia de Cartas (RN07) ---

@pytest.mark.parametrize("carta_forte, carta_fraca", [
    # Manilhas vs Manilhas
    (Carta(1, "ESPADAS"), Carta(1, "BASTOS")),   # RN07-1
    (Carta(1, "BASTOS"), Carta(7, "ESPADAS")),  # RN07-2
    (Carta(7, "ESPADAS"), Carta(7, "OUROS")),  # RN07-3
    # Manilha vs Comum
    (Carta(7, "OUROS"), Carta(3, "COPAS")),    # RN07-4
    # Comuns vs Comuns
    (Carta(3, "ESPADAS"), Carta(2, "BASTOS")),  # RN07-5
    (Carta(2, "BASTOS"), Carta(1, "OUROS")),   # RN07-6
    (Carta(1, "OUROS"), Carta(12, "COPAS")),
    (Carta(12, "COPAS"), Carta(11, "ESPADAS")),
    (Carta(11, "BASTOS"), Carta(10, "OUROS")),
    (Carta(10, "ESPADAS"), Carta(7, "COPAS")),
    (Carta(7, "COPAS"), Carta(6, "BASTOS")),
    (Carta(6, "OUROS"), Carta(5, "ESPADAS")),
    (Carta(5, "COPAS"), Carta(4, "BASTOS")),
])
def test_hierarquia_cartas_RN07(carta_forte, carta_fraca):
    """Testa todas as hierarquias de cartas (RN07) com parametrize."""
    jogo = Jogo()
    vencedora = jogo.verificar_carta_vencedora(carta_forte, carta_fraca)
    assert vencedora == carta_forte

@pytest.mark.xfail(reason="BUG: Jogo.verificar_carta_vencedora não retorna 'Empate'. Ela dá a vitória para a carta_jogador_01 por padrão. [RN03]")
def test_empate_cartas_comuns_falha_RN03():
    """
    Testa (RN03): Duas cartas de mesmo valor (não-manilha)
    deveriam resultar em "Empate", mas o código dá a vitória ao j1.
    """
    jogo = Jogo()
    carta_j1 = Carta(3, "COPAS")
    carta_j2 = Carta(3, "BASTOS") 
    
    vencedora = jogo.verificar_carta_vencedora(carta_j1, carta_j2)
    
    # O assert que o REQUISITO pede (e que vai falhar):
    assert vencedora == "Empate"
    
    # O assert que prova o BUG (o que o código realmente faz):
    # assert vencedora == carta_j1

# --- Testes de Regras de Empate (Parda) (RN03) ---

@pytest.mark.parametrize("vaza1_vencedor, vaza2_vencedor, vaza3_vencedor, j1_rodadas, j2_rodadas", [
    # (RN03-1) Vaza 1 parda, Vaza 2 j1 ganha -> J1 ganha a mão
    ("parda", 1, None, 1, 0),
    
    # (RN03-2) Vaza 1 j1 ganha, Vaza 2 parda -> J1 ganha a mão
    (1, "parda", None, 1, 0),
    
    # (RN03-3) Vaza 1 j1 ganha, Vaza 2 j2 ganha, Vaza 3 parda -> J1 ganha a mão (venceu a 1a)
    (1, 2, "parda", 1, 1),
    
    # (RN03-4) Vaza 1 parda, Vaza 2 parda, Vaza 3 j1 ganha -> J1 ganha a mão
    ("parda", "parda", 1, 1, 0),
    
    # (RN03-5) Três pardas -> "Mão" (j1) ganha a mão
    ("parda", "parda", "parda", 0, 0),
])
def test_regras_parda_RN03(cenario_rodadas, vaza1_vencedor, vaza2_vencedor, vaza3_vencedor, j1_rodadas, j2_rodadas):
    """Testa todas as regras de empate (RN03) com parametrize."""
    
    jogo, j1, j2, c1, c2 = cenario_rodadas
    # j1 é o "mão" (j1.primeiro == True) na fixture
    
    # Simula as vazas
    if vaza1_vencedor == 1:
        jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    elif vaza1_vencedor == 2:
        jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c2)

    if vaza2_vencedor == 1:
        jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    elif vaza2_vencedor == 2:
        jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c2)
        
    if vaza3_vencedor == 1:
        jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    elif vaza3_vencedor == 2:
        jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c2)

    # Assert: Verifica o estado final das rodadas ganhas
    assert j1.rodadas == j1_rodadas
    assert j2.rodadas == j2_rodadas
    
    # A lógica principal do __main__.py decidiria o vencedor da mão 
    # com base nesses contadores e em quem é 'j1.primeiro'.

# --- Testes de Vitória e Fluxo (RN04, RN11, UC-01) ---

def test_RN04_1_vencer_2_vazas_concede_pontos_da_aposta(cenario_rodadas):
    """Testa RN04-1: Vencer 2 vazas deve dar os pontos da aposta (1 por padrão)."""
    jogo, j1, j2, c1, c2 = cenario_rodadas
    truco = Truco()
    valor_aposta = truco.retornar_valor_aposta() # 1 ponto
    
    assert j1.retorna_pontos_totais() == 0
    assert j1.rodadas == 0
    
    # J1 ganha 2 vazas
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    
    # Simula a lógica do __main__.py
    if j1.rodadas == 2:
        j1.adicionar_pontos(valor_aposta)

    assert j1.rodadas == 2
    assert j1.retorna_pontos_totais() == 1 # Ganhou 1 ponto

def test_alternar_mao_e_pe_a_cada_rodada_RN11(cenario_rodadas):
    """Testa (RN11): Se a função de "Mão" e "Pé" alterna a cada rodada."""
    jogo, j1, j2, _, _ = cenario_rodadas
    
    # Estado Inicial (Fixture): j1 é "mão"
    j1.primeiro, j1.ultimo = True, False
    j2.primeiro, j2.ultimo = False, True
    
    # Início da Rodada 2
    jogo.quem_inicia_rodada(j1, j2)
    # J2 deve ser "mão"
    assert j2.primeiro is True and j1.primeiro is False
    assert j1.ultimo is True and j2.ultimo is False
    
    # Início da Rodada 3
    jogo.quem_inicia_rodada(j1, j2)
    # J1 deve ser "mão" novamente
    assert j1.primeiro is True and j2.primeiro is False
    assert j2.ultimo is True and j1.ultimo is False

def test_vencedor_da_vaza_joga_primeiro_na_proxima_vaza_UC01(cenario_rodadas):
    """Testa (UC-01): Vencedor da vaza joga primeiro na próxima."""
    jogo, j1, j2, c1, c2 = cenario_rodadas
    
    # Vaza 1: j1 (mão) joga. Ganhador é c1 (j1).
    jogo.quem_joga_primeiro(j1, j2, c1, c2, ganhador=c1)
    # Início da Vaza 2: j1 deve ser 'primeiro'
    assert j1.primeiro is True and j2.primeiro is False
    
    # Vaza 2: j1 joga primeiro. Ganhador é c2 (j2).
    jogo.quem_joga_primeiro(j1, j2, c1, c2, ganhador=c2)
    # Início da Vaza 3: j2 deve ser 'primeiro'
    assert j2.primeiro is True and j1.primeiro is False

@pytest.mark.xfail(reason="BUG: Jogo.jogador_fugiu() não implementa a RN01 (dar pontos ao oponente).")
def test_desistencia_no_modelo_jogo_nao_da_pontos_ao_oponente_RN01(cenario_rodadas):
    """
    Testa (RN01 / RF09): Prova que Jogo.jogador_fugiu() está incompleto
    e não dá pontos ao oponente conforme a regra RN01.
    """
    jogo, j1, j2, _, _ = cenario_rodadas
    truco = Truco()
    truco.valor_aposta = 2 # Mão valendo 2
    
    # J1 foge. J2 deveria ganhar 2 pontos.
    jogo.jogador_fugiu(j1, j1, j2, truco.retornar_valor_aposta())

    # O assert que o REQUISITO pede (e que vai falhar):
    assert j2.retorna_pontos_totais() == 2
    
    # O assert que prova o BUG (o que o código realmente faz):
    # assert j2.retorna_pontos_totais() == 0

@pytest.mark.xfail(reason="BUG: A falha em detectar pardas (RN03) quebra o fluxo do jogo.")
def test_bug_empate_quebra_regra_parda_RN03(cenario_rodadas):
    """
    Testa o impacto do bug da parda (RN03) no fluxo do jogo.
    
    Cenário (RN03-1):
    - Vaza 1: Parda (Empate)
    - Vaza 2: Bot (J2) ganha
    - Regra Correta: Bot (J2) ganha a mão. A mão termina na Vaza 2.
    """
    
    # 1. Arrange
    # A fixture 'cenario_rodadas' nos dá jogo, j1, j2
    jogo, j1, j2, _, _ = cenario_rodadas 
    
    # Cartas da Vaza 1 (Parda)
    c1_vaza1 = Carta(3, "COPAS")
    c2_vaza1 = Carta(3, "BASTOS")
    
    # Cartas da Vaza 2 (Bot/J2 ganha)
    c1_vaza2 = Carta(4, "OUROS")
    c2_vaza2 = Carta(7, "ESPADAS") # Manilha, J2 ganha

    # 2. Act (Simulando o fluxo do __main__.py)
    
    # --- VAZA 1 ---
    # O __main__ chama verificar_carta_vencedora
    # AQUI O BUG ACONTECE: 'verificar_carta_vencedora'
    # deveria retornar "Empate", mas retorna c1_vaza1.
    ganhador_v1 = jogo.verificar_carta_vencedora(c1_vaza1, c2_vaza1)
    
    # O __main__ então adiciona a rodada
    jogo.adicionar_rodada(j1, j2, c1_vaza1, c2_vaza1, ganhador_v1)
    
    # --- VAZA 2 ---
    # O jogo continua (erradamente)
    ganhador_v2 = jogo.verificar_carta_vencedora(c1_vaza2, c2_vaza2)
    jogo.adicionar_rodada(j1, j2, c1_vaza2, c2_vaza2, ganhador_v2)

    # 3. Assert (Verificando as consequências do bug)
    
    # O que DEVERIA acontecer (Regra RN03):
    # O ganhador_v1 deveria ser "Empate"
    # j1.rodadas == 0, j2.rodadas == 1
    # E o jogo deveria parar (is_mao_terminada == True)
    
    # O que REALMENTE acontece (provado pelo teste):
    
    # 1. A Vaza 1 (Parda) foi (incorretamente) dada ao J1
    assert ganhador_v1 == c1_vaza1 
    
    # 2. O placar de rodadas está 1 a 1 (em vez de 0 a 1)
    assert j1.rodadas == 1
    assert j2.rodadas == 1
    
    # 3. O jogo NÃO terminou (pois ninguém tem 2 rodadas),
    #    embora a regra (RN03) diga que deveria ter terminado.
    assert (j1.rodadas == 2 or j2.rodadas == 2) is False

def test_jogo_init_estado_inicial_correto():
    """
    Verifica se a classe Jogo é instanciada com os valores padrão corretos.
   
    """
    # 1. Arrange / Act
    jogo = Jogo()
    
    # 3. Assert
    assert jogo.rodadas == []
    assert jogo.trucoPontos == 1

def test_criar_jogador_retorna_jogador_com_mao(cenario_distribuicao):
    """
    Verifica se 'criar_jogador' retorna uma instância de Jogador
    e se a mão do jogador foi criada (tem 3 cartas).
   
    """
    # 1. Arrange
    baralho, _, _ = cenario_distribuicao
    jogo = Jogo()
    
    # 2. Act
    jogador_criado = jogo.criar_jogador("Humano Teste", baralho)
    
    # 3. Assert
    assert isinstance(jogador_criado, Jogador)
    assert len(jogador_criado.mao) == 3
    assert len(baralho.cartas) == 37 # 40 - 3

def test_criar_bot_retorna_bot_com_mao(cenario_distribuicao):
    """
    Verifica se 'criar_bot' retorna uma instância de Bot
    e se a mão do bot foi criada (tem 3 cartas).
   
    """
    # 1. Arrange
    baralho, _, _ = cenario_distribuicao
    jogo = Jogo()
    
    # 2. Act
    bot_criado = jogo.criar_bot("Robô Teste", baralho)
    
    # 3. Assert
    assert isinstance(bot_criado, Bot)
    assert len(bot_criado.mao) == 3
    assert len(baralho.cartas) == 37 # 40 - 3

def test_adicionar_rodada_caminhos_if_else(cenario_rodadas):
    """
    Verifica todos os caminhos de retorno (1, 2, "Erro")
    da função 'adicionar_rodada'.
   
    """
    # 1. Arrange
    jogo, j1, j2, c1, c2 = cenario_rodadas
    
    # 2. Act / 3. Assert
    
    # Caminho 1: Ganhador == carta1
    retorno1 = jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c1)
    assert retorno1 == 1
    assert j1.rodadas == 1
    
    # Caminho 2: Ganhador == carta2
    retorno2 = jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=c2)
    assert retorno2 == 2
    assert j2.rodadas == 1
    
    # Caminho 3: Ganhador != carta1 e != carta2 (Else)
    retorno_erro = jogo.adicionar_rodada(j1, j2, c1, c2, ganhador=None)
    assert retorno_erro == "Erro"

def test_quem_joga_primeiro_nao_muda_em_empate(cenario_rodadas):
    """
    Testa (Objetivo: Testes para if's):
    Verifica o caminho 'else' (implícito) de 'quem_joga_primeiro',
    onde o 'ganhador' não é nem c1 nem c2 (ex: "Empate").
    As flags 'primeiro' não devem mudar.
   
    """
    # 1. Arrange
    jogo, j1, j2, c1, c2 = cenario_rodadas
    j1.primeiro = True # Estado inicial
    j2.primeiro = False # Estado inicial
    
    # 2. Act
    # Passamos um ganhador que não é c1 nem c2
    jogo.quem_joga_primeiro(j1, j2, c1, c2, ganhador="Empate")
    
    # 3. Assert
    # O estado deve permanecer o mesmo
    assert j1.primeiro is True
    assert j2.primeiro is False

def test_quem_inicia_rodada_nao_faz_nada_se_rodada_nao_for_zero(cenario_rodadas):
    """
    Testa (Objetivo: Testes para if's):
    Verifica o 'if' principal de 'quem_inicia_rodada'. Se as rodadas
    não forem 0, nada deve acontecer.
   
    """
    # 1. Arrange
    jogo, j1, j2, _, _ = cenario_rodadas
    
    # Define o estado inicial (diferente do 'test_alternar_mao')
    j1.rodadas = 1
    j2.rodadas = 0
    j1.primeiro = True
    j2.primeiro = False
    
    # 2. Act
    jogo.quem_inicia_rodada(j1, j2)
    
    # 3. Assert
    # O 'if' principal (rodadas == 0) falhou, nada deve mudar
    assert j1.primeiro is True
    assert j2.primeiro is False

def test_jogador_fugiu_imprime_mensagem_e_reseta_turno(cenario_rodadas, capsys):
    """
    Testa (Objetivo: Mensagem de Erro / Retorno de Função):
    Verifica se 'jogador_fugiu' imprime a mensagem "Jogador fugiu!"
    e reseta as flags de turno corretamente.
   
    """
    # 1. Arrange
    jogo, j1, j2, _, _ = cenario_rodadas
    
    # Polui o estado do turno (Vez do J2)
    j1.primeiro = False
    j2.primeiro = True
    
    # 2. Act
    jogo.jogador_fugiu(j1, j1, j2, 1) # 'jogador' (parâmetro 1) não é usado
    
    # 3. Assert
    captured = capsys.readouterr()
    
    # Testa a Mensagem de Erro
    assert "Jogador fugiu!" in captured.out
    
    # Testa o Retorno de Função (flags resetadas)
    assert j1.primeiro is True
    assert j2.primeiro is False

@pytest.mark.xfail(reason="BUG: SUT (jogo.py) não trata KeyError se uma carta (ex: 8) não estiver no dicionário 'CARTAS_VALORES'.")
def test_verificar_carta_vencedora_levanta_keyerror_com_carta_invalida():
    """
    Testa (Objetivo: Testes para Exceções):
    Verifica se 'verificar_carta_vencedora' levanta um KeyError
    se uma carta inválida (ex: 8 de Copas) for passada,
    pois '8' não está em 'CARTAS_VALORES'.
   
    """
    # 1. Arrange
    jogo = Jogo()
    carta_valida = Carta(4, "OUROS")
    carta_invalida = Carta(8, "COPAS") # '8' não existe em CARTAS_VALORES
    
    # 2. Act / 3. Assert
    # O teste passa se 'KeyError' for levantado
    with pytest.raises(KeyError):
        # A lógica do SUT tentará acessar CARTAS_VALORES['8']
        jogo.verificar_carta_vencedora(carta_invalida, carta_valida)

def test_verificar_ganhador_chama_interface(cenario_rodadas): # Remova o 'monkeypatch'
    """
    Testa (Objetivo: Mensagem de Erro / Spy):
    Verifica se 'verificar_ganhador' chama corretamente
    o método 'mostrar_carta_ganhadora' da interface.
   
    """
    # 1. Arrange
    jogo, j1, j2, c1, c2 = cenario_rodadas
    
    # Criamos um "Spy" (espião) para o método da interface
    foi_chamado = False
    carta_ganhadora_spy = None

    def spy_mostrar_carta_ganhadora(ganhador):
        nonlocal foi_chamado, carta_ganhadora_spy
        foi_chamado = True
        carta_ganhadora_spy = ganhador

    # Criamos um Mock da Interface
    class MockInterface:
        pass # É só um objeto vazio
    
    iface = MockInterface()
    
    iface.mostrar_carta_ganhadora = spy_mostrar_carta_ganhadora
    # ------------------
    
    # 2. Act
    # (c1 é mais forte que c2 na fixture cenario_rodadas)
    jogo.verificar_ganhador(c1, c2, iface) 
    
    # 3. Assert
    assert foi_chamado is True
    assert carta_ganhadora_spy == c1 # Verifica se a carta correta foi passada