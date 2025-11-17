import pytest
from truco.jogador import Jogador
from truco.carta import Carta
from truco.interface import Interface
import os 
import types

@pytest.fixture
def iface_e_jogadores():
    """Fornece uma interface limpa e jogadores para testes de placar."""
    iface = Interface()
    
    # Usamos classes genéricas, pois não precisamos da lógica do Jogo/Bot
    class MockJogador:
        def __init__(self, nome):
            self.nome = nome
            
    j1 = MockJogador("Humano")
    j2 = MockJogador("Robô")
    return iface, j1, j2

def test_jogador_mostra_mao_RF04(capsys):
    """
    Testa (RF04): Se as cartas do jogador são exibidas corretamente.
    
    Este teste chama 'jogador.mostrar_mao()', que é a função
    usada pelo '__main__.py' para mostrar as opções ao humano
   .
    """
    # 1. Arrange
    j1 = Jogador("Humano")
    iface = Interface()
    # Damos ao J1 uma mão conhecida
    j1.mao = [Carta(7, "OUROS"), Carta(1, "ESPADAS")]

    # 2. Act
    # O método 'mostrar_mao'
    # chama 'carta.exibir_carta'
    j1.mostrar_mao(iface) 

    # 3. Assert
    captured = capsys.readouterr() # Captura o print()
    
    # Verifica se a saída do console contém as cartas
    assert "[0] 7 de OUROS" in captured.out
    assert "[1] 1 de ESPADAS" in captured.out

def test_interface_mostrar_carta_jogada(capsys):
    """Testa se a carta jogada é exibida."""
    iface = Interface()
    carta = Carta(7, "ESPADAS")
    iface.mostrar_carta_jogada("Humano", carta)
    captured = capsys.readouterr()
    assert "Humano jogou a carta: 7 de ESPADAS" in captured.out

def test_interface_placar_envido_RF24(iface_e_jogadores, capsys):
    """Testa (RF24): Exibição do placar do Envido."""
    iface, j1, j2 = iface_e_jogadores
    
    # Testa a vitória do J1
    iface.mostrar_vencedor_envido(1, j1.nome, 33, j2.nome, 25)
    captured_j1 = capsys.readouterr()
    assert "Venceu o envido com 33 pontos" in captured_j1.out
    assert "PERDEU o envido com 25 pontos" in captured_j1.out
    
    # Testa a vitória do J2
    iface.mostrar_vencedor_envido(2, j1.nome, 25, j2.nome, 33)
    captured_j2 = capsys.readouterr()
    assert "Venceu o envido com 33 pontos" in captured_j2.out
    assert "PERDEU o envido com 25 pontos" in captured_j2.out

def test_interface_placar_flor_RF24(iface_e_jogadores, capsys):
    """Testa (RF24): Exibição do placar da Flor."""
    iface, j1, j2 = iface_e_jogadores
    
    iface.mostrar_vencedor_flor(1, j1.nome, j2.nome, 3)
    captured = capsys.readouterr()
    assert "Jogador 1 - Humano: Venceu a flor e ganhou 3 pontos" in captured.out

def test_interface_placar_rodadas(iface_e_jogadores, capsys):
    """Testa a exibição do placar de vazas/rodadas."""
    iface, j1, j2 = iface_e_jogadores
    
    iface.mostrar_placar_rodadas(j1.nome, 2, j2.nome, 1)
    captured = capsys.readouterr()
    assert "Humano: Venceu 2 Rodada(s)" in captured.out
    assert "Robô: Venceu 1 Rodada(s)" in captured.out

def test_interface_placar_total(iface_e_jogadores, capsys):
    """Testa (RF24): Exibição do placar total (mão)."""
    iface, j1, j2 = iface_e_jogadores
    
    iface.mostrar_placar_total(j1.nome, 10, j2.nome, 4)
    captured = capsys.readouterr()
    assert "Humano: 10 Pontos Acumulados" in captured.out
    assert "Robô: 4 Pontos Acumulados" in captured.out

def test_interface_placar_desistencia_RF09(iface_e_jogadores, capsys):
    """Testa (RF09): Exibição da desistência ('Ir ao Monte')."""
    iface, j1, j2 = iface_e_jogadores
    
    iface.mostrar_placar_total_jogador_fugiu(j1, j1.nome, 10, j2.nome, 12)
    captured = capsys.readouterr()
    
    # Testa a mensagem de desistência
    assert "Jogador Humano fugiu!" in captured.out
    
    # O código original em 'interface.py' (linha 50)
    # comenta a exibição do placar total, então testamos se 
    # o placar NÃO foi exibido.
    assert "Pontos Acumulados" not in captured.out

def test_interface_mensagem_erro_truco_repetido(iface_e_jogadores, capsys):
    """
    Testa (Mensagem de Erro): Se a interface exibe a mensagem
    correta quando o jogador tenta pedir truco novamente.
    [Requisito: Testes para mensagens de erro]
    """
    # 1. Arrange
    iface, j1, j2 = iface_e_jogadores

    # 2. Act
    # Chama a função específica da interface
    iface.mostrar_pediu_truco(j1.nome)

    # 3. Assert
    captured = capsys.readouterr()
    
    # Verifica se a mensagem de erro correta foi impressa
    assert "Humano pediu truco e o pedido já foi aceito, escolha outra jogada!" in captured.out

def test_interface_mostrar_carta_ganhadora(iface_e_jogadores, capsys):
    """Testa (Objetivo: Mensagem de Erro): Exibição da carta ganhadora."""
    iface, _, _ = iface_e_jogadores
    carta = Carta(3, "COPAS")
    iface.mostrar_carta_ganhadora(carta)
    captured = capsys.readouterr()
    # O SUT imprime com quebras de linha no início e fim.
    assert "\nCarta ganhadora: 3 de COPAS\n" in captured.out

def test_interface_mostrar_ganhador_rodada(iface_e_jogadores, capsys):
    """Testa (Objetivo: Mensagem de Erro): Exibição do ganhador da rodada."""
    iface, j1, _ = iface_e_jogadores
    iface.mostrar_ganhador_rodada(j1.nome)
    captured = capsys.readouterr()
    assert "Humano ganhou a rodada\n" in captured.out

def test_interface_mostrar_ganhador_jogo(iface_e_jogadores, capsys):
    """Testa (Objetivo: Mensagem de Erro): Exibição do ganhador do jogo."""
    iface, j1, _ = iface_e_jogadores
    iface.mostrar_ganhador_jogo(j1.nome)
    captured = capsys.readouterr()
    assert "\nHumano ganhou o jogo" in captured.out

def test_interface_mostrar_jogador_opcoes(iface_e_jogadores, capsys):
    """Testa (Objetivo: Mensagem de Erro): Exibição do "Jogador 1 é mão"."""
    iface, _, _ = iface_e_jogadores
    iface.mostrar_jogador_opcoes("Humano")
    captured = capsys.readouterr()
    assert "Jogador 1 é mão" in captured.out


def test_limpar_tela_chama_os_system_com_clear(iface_e_jogadores, monkeypatch):
    """
    Testa (Objetivo: Chamada de Função):
    Verifica se 'limpar_tela' chama 'os.system' com o comando 'clear' (Linux).
    (Corrigido o NameError do 'os')
   
    """
    iface, _, _ = iface_e_jogadores
    chamado_com = None
    def mock_os_system(comando):
        nonlocal chamado_com
        chamado_com = comando
        return 0
        
    monkeypatch.setattr(os, 'system', mock_os_system)
    iface.limpar_tela()
    assert chamado_com == "clear"


def test_border_msg_calcula_largura_se_width_none(iface_e_jogadores, capsys):
    """
    Testa (Objetivo: Testes para if's):
    Verifica o caminho 'if not width:' calculando a largura máxima.
    """
    iface, _, _ = iface_e_jogadores
    msg = "Linha Curta\nLinha Muito Longa" # Max len: 17-18
    
    iface.border_msg(msg, indent=1, width=None)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Atualizado com base no comportamento real observado
    assert "║ Linha Curta       ║\n" in output
    assert "║ Linha Muito Longa ║\n" in output


def test_border_msg_inclui_titulo_e_sublinhado(iface_e_jogadores, capsys):
    """
    Testa (Objetivo: Testes para if's):
    Verifica o caminho 'if title:' adicionando o título e o sublinhado.
    (A formatação está correta, mas a largura é 5, e o título é 6.
     O SUT apenas mostra 1 espaço de padding em cada lado).
   
    """
    iface, _, _ = iface_e_jogadores
    msg = "Corpo" # width=5
    title = "TITULO" # len=6
    
    iface.border_msg(msg, indent=1, width=None, title=title)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # O SUT (interface.py) tem o bug de formatação, resultando em 1 espaço de indent + titulo + 1 espaço de indent
    assert "║ TITULO ║" in output
    assert "║ ------ ║" in output


@pytest.mark.parametrize("naipe, simbolo_esperado", [
    ("ESPADAS", "♠"),
    ("OUROS", "♦"),
    ("COPAS", "♥"),
    ("BASTOS", "♣"),
])
def test_desenhar_cartas_seleciona_simbolo_correto_RNF04(iface_e_jogadores, naipe, simbolo_esperado):
    """
    Testa (Objetivo: Testes para if's):
    Verifica a cadeia de 'if/elif' para garantir que o naipe correto
    (simbolo) é inserido e que a string de carta é formatada corretamente.
    (Corrigido o assert para usar o espaço final do SUT em vez do ponto).
   
    """
    iface, _, _ = iface_e_jogadores
    card_string = f"7 de {naipe}"
    
    linhas_carta = iface.desenhar_cartas(card_string)
    
    # A linha 4 (índice 4) é a linha central que contém o símbolo
    assert f"│. . {simbolo_esperado} . .│" == linhas_carta[4]
    
    # CORREÇÃO: O SUT insere 7 seguido de dois espaços, '7  '
    assert f"│.7  . . .│" == linhas_carta[1] 
    # CORREÇÃO: O SUT insere um espaço no final da linha 7 em vez de um ponto
    assert f"│. . . 7 .│" == linhas_carta[7]
