# Salve como: tests/test_jogador.py
import pytest
from truco.jogador import Jogador
from truco.carta import Carta

def test_jogador_tem_3_cartas_RF03(cenario_distribuicao):
    """Testa se o jogador humano recebe 3 cartas (RF03)."""
    # A fixture cenario_distribuicao vem do conftest.py
    baralho, j1, bot = cenario_distribuicao
    
    # Ação: Jogador (j1) cria sua mão
    j1.criar_mao(baralho) 
    
    # Verifica se o jogador tem 3 cartas na mão
    assert len(j1.mao) == 3

# --- Testes de Pontuação (RN02 / RF25) ---

def test_vitoria_implementada_com_12_pontos_RF25():
    """
    Testa (RF25): Valida a condição de término (12 pontos)
    conforme implementado no __main__.py,
    embora o requisito RN02 peça 24.
    """
    jogador = Jogador("Vencedor")
    jogador.adicionar_pontos(10)
    assert jogador.retorna_pontos_totais() < 12
    
    jogador.adicionar_pontos(2)
    assert jogador.retorna_pontos_totais() == 12
    # Esta é a verificação exata que o __main__.py faz:
    assert jogador.retorna_pontos_totais() >= 12

def test_vitoria_requisito_com_24_pontos_RN02():
    """
    Testa (RN02): Valida se o jogador pode acumular 24 pontos
    (conforme o requisito), mesmo que o jogo termine antes.
    """
    jogador = Jogador("Vencedor")
    jogador.adicionar_pontos(12)
    jogador.adicionar_pontos(10)
    assert jogador.retorna_pontos_totais() == 22
    
    jogador.adicionar_pontos(2)
    assert jogador.retorna_pontos_totais() == 24
    assert jogador.retorna_pontos_totais() >= 24

# --- Testes de Cálculo de Envido (RN10) ---

@pytest.mark.parametrize("mao, pontos_esperados", [
    # (RN10) - 7 de ouros + 6 de ouros = 33 pontos
    ([Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")], 33),
    
    # (RN10) - Figuras (10, 11, 12) valem 0
    ([Carta(12, "COPAS"), Carta(11, "COPAS"), Carta(5, "ESPADAS")], 20),
    
    # (RN10) - Sem mesmo naipe, vale a mais alta
    ([Carta(7, "OUROS"), Carta(5, "ESPADAS"), Carta(2, "BASTOS")], 7),
    
    # Caso com 3 do mesmo naipe (calcula as 2 mais altas)
    ([Carta(7, "BASTOS"), Carta(6, "BASTOS"), Carta(1, "BASTOS")], 33), # 20 + 7 + 6
])
def test_calculo_envido_RN10(mao, pontos_esperados):
    """Testa o cálculo de pontos de Envido (RN10) com vários cenários."""
    jogador = Jogador("Teste")
    pontos_envido = jogador.calcula_envido(mao)
    assert pontos_envido == pontos_esperados

# --- Testes de Detecção de Flor (RN09 / RF16) ---

def test_jogador_checa_flor_detecta_corretamente_RF16():
    """Testa (RF16): 3 cartas do mesmo naipe == True."""
    jogador = Jogador("Teste")
    jogador.mao = [Carta(1, "COPAS"), Carta(5, "COPAS"), Carta(12, "COPAS")]
    assert jogador.checa_flor() is True

def test_jogador_checa_flor_nao_detecta_incorretamente_RN09():
    """Testa (RN09): Cartas de naipes mistos == False."""
    jogador = Jogador("Teste")
    jogador.mao = [Carta(1, "COPAS"), Carta(5, "COPAS"), Carta(12, "ESPADAS")]
    assert jogador.checa_flor() is False

# --- Testes de Exceção ---

def test_jogar_carta_que_nao_esta_na_mao_levanta_excecao():
    """
    Testa (Exceção): Jogar uma carta por um índice
    que não existe na mão levanta um IndexError.
    """
    jogador = Jogador("Teste")
    jogador.mao = [Carta(1, "COPAS"), Carta(2, "OUROS"), Carta(3, "ESPADAS")]
    
    # Verifica se o código levanta 'IndexError'
    # ao tentar jogar a carta no índice 10 (que não existe)
    with pytest.raises(IndexError):
        jogador.jogar_carta(10)

# Adicione ao final de: tests/test_jogador.py
# (Você precisará de: from truco.carta import Carta)

@pytest.mark.parametrize("mao, pontos_esperados", [
    ([], 0), # Mão vazia (início do loop)
    ([Carta(7, "OUROS")], 7), # Mão com 1 carta (início do loop)
])
def test_calculo_envido_com_mao_incompleta_RN10(mao, pontos_esperados):
    """
    Testa (Loop / Exceção): O que acontece se 'calcula_envido'
    for chamado com 0 ou 1 carta (limite do loop).
    (Espera-se que falhe com ValueError: max() de lista vazia).
    """
    # 1. Arrange
    jogador = Jogador("Teste")
    
    # 2. Act
    # O SUT (jogador.py) falha aqui se a mão tem < 2 cartas,
    # pois a lista 'pontos_envido' fica vazia.
    pontos_envido = jogador.calcula_envido(mao)
    
    # 3. Assert
    assert pontos_envido == pontos_esperados

def test_jogador_init_estado_inicial_correto():
    """
    Testa (Objetivo: Retorno de Função / __init__):
    Verifica se a classe Jogador é instanciada com os valores padrão corretos.
    """
    # 1. Arrange / Act
    jogador = Jogador("Teste")
    
    # 3. Assert
    assert jogador.nome == "Teste"
    assert jogador.mao == []
    assert jogador.pontos == 0
    assert jogador.rodadas == 0
    assert jogador.primeiro is False
    assert jogador.pediu_truco is False

def test_simples_setters_e_getters_RF25():
    """
    Testa (Objetivo: Retorno de Função):
    Verifica a funcionalidade básica de métodos simples de set/get.
    """
    # 1. Arrange
    jogador = Jogador("Teste")
    
    # 2. Act & 3. Assert
    
    # Teste: adicionar_rodada / checa_mao
    jogador.adicionar_rodada()
    assert jogador.rodadas == 1
    assert jogador.checa_mao() == [] # Mao está vazia, retorna lista vazia
    
    # Teste: retorna_pontos_envido (assume init=0)
    assert jogador.retorna_pontos_envido() == 0
    
    # Teste: retorna_pontos_totais (já coberto, mas bom para completar)
    jogador.adicionar_pontos(5)
    assert jogador.retorna_pontos_totais() == 5

def test_resetar_limpa_estado_da_rodada():
    """
    Testa (Objetivo: Retorno de Função / Estado):
    Verifica se 'resetar' retorna o objeto ao seu estado padrão
    após ter sido modificado.
    """
    # 1. Arrange (Poluir o estado)
    jogador = Jogador("Teste")
    jogador.rodadas = 2
    jogador.flor = True
    jogador.pediu_truco = True
    
    # 2. Act
    jogador.resetar()
    
    # 3. Assert
    assert jogador.rodadas == 0
    assert jogador.mao == []
    assert jogador.flor is False
    assert jogador.pediu_truco is False

@pytest.mark.parametrize("mao_size, pediu_truco, checa_flor_result, expected_prints", [
    # Caminho 1: Tudo ativo (3 cartas, sem truco pedido, tem flor)
    (3, False, True, ['[4] Truco', '[5] Flor', '[6] Envido', '[9] Ir ao baralho']),
    # Caminho 2: Apenas Truco e Envido (3 cartas, sem truco pedido, sem flor)
    (3, False, False, ['[4] Truco', '[6] Envido', '[9] Ir ao baralho']),
    # Caminho 3: Apenas Envido (3 cartas, truco já pedido)
    (3, True, True, ['[6] Envido', '[9] Ir ao baralho']),
    # Caminho 4: Apenas Truco (2 cartas, sem truco pedido)
    (2, False, False, ['[4] Truco', '[9] Ir ao baralho']),
    # Caminho 5: Apenas Desistencia (1 carta)
    (1, False, False, ['[9] Ir ao baralho']),
])
def test_mostrar_opcoes_imprime_opcoes_condicionais(cenario_base, monkeypatch, capsys, mao_size, pediu_truco, checa_flor_result, expected_prints):
    """
    Testa (Objetivo: Testes para if's / Mensagens de Erro):
    Verifica se 'mostrar_opcoes' imprime apenas as opções válidas
    para o estado atual da mão (combinações de IFs).
   
    """
    # 1. Arrange
    j1, j2, iface, mock_cbr, mock_dados = cenario_base
    
    # Mock das dependências (checa_flor)
    monkeypatch.setattr(j1, 'checa_flor', lambda: checa_flor_result)
    
    # Configuração do estado
    j1.mao = [Carta(1, "E")] * mao_size
    j1.pediu_truco = pediu_truco
    j1.flor = False
    
    # 2. Act
    j1.mostrar_opcoes(iface)
    
    # 3. Assert
    captured = capsys.readouterr()
    output_lines = [line.strip() for line in captured.out.split('\n')]
    
    for expected in expected_prints:
        # Verifica se todas as opções esperadas estão presentes
        assert expected in output_lines
    
    # Verifica se a Flor foi setada para True se ela foi impressa (efeito colateral/bug)
    if '[5] Flor' in output_lines:
        assert j1.flor is True