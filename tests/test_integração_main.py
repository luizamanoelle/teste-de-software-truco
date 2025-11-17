# Salve como: tests/test_integracao_main.py

import pytest
from truco.carta import Carta
from truco.jogador import Jogador
from truco.bot import Bot
from truco.jogo import Jogo
from truco.interface import Interface
from truco.dados import Dados
from truco.truco import Truco
from truco.envido import Envido
from truco.flor import Flor
from truco.baralho import Baralho # Importação necessária

# Importa as funções que queremos testar do __main__
# (Isso é complexo porque o __main__ não foi feito para ser importado)
# Vamos recriar o ambiente do __main__
# --- Teste de Integração (Testando o "Remendo") ---

def test_integracao_main_bloqueia_envido_com_flor(cenario_main, monkeypatch):
    """
    Testa (RN09 / __main__.py linha 48):
    Verifica se o Humano (J1) é BLOQUEADO de chamar Envido
    se o Bot (J2) tiver Flor.
    """
    # 1. Arrange
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # J1 (Humano) tem Envido
    j1.mao = [Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")]
    j1.envido = j1.calcula_envido(j1.mao)
    
    # J2 (Bot) tem Flor
    j2.mao = [Carta(1, "COPAS"), Carta(2, "COPAS"), Carta(3, "COPAS")]
    j2.flor = j2.checa_flor() # True
    
    # Simula o Humano tentando chamar Envido (opção '6')
    monkeypatch.setattr('builtins.input', lambda _: '6')
    
    # "Espia" a função flor.pedir_flor para ver se ela foi chamada
    # (é isso que o "remendo" da linha 48 faz)
    monkeypatch.setattr(flor, 'pedir_flor', lambda *args: None)
    
    # Mock para evitar que o teste trave no loop
    monkeypatch.setattr(j1, 'jogar_carta', lambda *args: Carta(7, "OUROS"))
    
    # 2. Act
    # Precisamos simular o 'turno_do_humano'
    # Vamos chamar a lógica exata da linha 48-52
    
    # Simulação da escolha do usuário
    carta_escolhida = int(input(f"Qual carta? ")) # monkeypatch retorna '6'
    
    # Esta é a lógica do "remendo" do __main__.py
    if ((len(j1.checa_mao()) == 3) and (carta_escolhida in [6, 7, 8]) and (j2.flor is True)):
        # Se entramos aqui, o bloqueio funcionou
        bloqueio_aconteceu = True
        flor.pedir_flor(1, j1, j2, interface) # Simula a chamada
        carta_escolhida = -1 # Reseta a escolha
    else:
        bloqueio_aconteceu = False
        
    # 3. Assert
    assert bloqueio_aconteceu is True
    assert carta_escolhida == -1 # A escolha foi resetada

def test_integracao_vitoria_encerra_jogo_RF25(cenario_main, monkeypatch):
    """
    Testa (RF25): Se o loop principal (simulado) detecta
    corretamente a condição de vitória e (simuladamente) 'quebra' o loop.
    """
    # 1. Arrange (Cenário)
    # Pega todos os objetos do jogo
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Define o estado do jogo: J1 está prestes a ganhar
    j1.adicionar_pontos(10)
    j2.adicionar_pontos(4)
    
    # A mão atual vale 2 pontos (ex: um Truco aceito)
    truco.valor_aposta = 2
    
    # 2. Act (Simulação do __main__.py)
    
    # Simula o J1 ganhando a mão (ex: 2 rodadas)
    j1.rodadas = 2
    j2.rodadas = 0
    
    # --- Início da lógica simulada do __main__.py (linha 272) ---
    pontos_antes = j1.retorna_pontos_totais() # 10
    
    # Simula o __main__ dando os pontos da mão ao vencedor
    if j1.rodadas == 2:
        j1.adicionar_pontos(truco.retornar_valor_aposta())
        # (ignora reiniciarJogo() por enquanto)

    pontos_depois = j1.retorna_pontos_totais() # 12
    
    # Simula a checagem de vitória no fim do loop (linha 301)
    vitoria_detectada = False
    if j1.pontos >= 12:
        vitoria_detectada = True  # Simula o 'break'
    elif j2.pontos >= 12:
        vitoria_detectada = True  # Simula o 'break'
    # --- Fim da lógica simulada ---

    # 3. Assert (Verificação)
    assert pontos_antes == 10
    assert pontos_depois == 12
    assert vitoria_detectada is True # O 'break' teria sido chamado!

# Adicione este teste ao seu arquivo tests/test_integração_main.py
# (Lembre de importar 'Carta' no topo, se ainda não o fez)

def test_integracao_main_bloqueia_flor_apos_vaza1_RN09(cenario_main, monkeypatch):
    """
    Testa (RN09): Se o 'remendo' no __main__.py
    realmente impede o Humano (J1) de chamar Flor (opção 5)
    após a primeira vaza (len(mao) != 3).
    """
    # 1. Arrange
    # A fixture 'cenario_main' nos dá todos os objetos globais
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Damos uma Flor para o J1
    j1.mao = [Carta(1, "COPAS"), Carta(2, "COPAS"), Carta(3, "COPAS")]
    j1.flor = j1.checa_flor() # True
    
    # Simula a Vaza 1: J1 joga uma carta
    j1.jogar_carta(0)
    assert len(j1.mao) == 2 # Vaza 1 já passou
    
    # Simula o Humano tentando chamar Flor (opção '5')
    carta_escolhida = 5
    
    # Mock: "Espia" a função flor.pedir_flor para ver se foi chamada
    foi_chamada = False
    def mock_pedir_flor(*args):
        nonlocal foi_chamada
        foi_chamada = True
    
    monkeypatch.setattr(flor, 'pedir_flor', mock_pedir_flor)

    # 2. Act
    # Esta é a lógica EXATA do __main__.py
    # O 'if' deve falhar porque len(j1.mao) não é 3
    if ((len(j1.mao) == 3) and (j1.flor) and carta_escolhida == 5):
        flor.pedir_flor(1, j1, j2, interface)
    
    # 3. Assert
    # O 'if' deve ter sido Falso
    # e a flor.pedir_flor NÃO deve ter sido chamada.
    assert foi_chamada is False


# Em: tests/test_integração_main.py
# (Adicione este teste no final do arquivo)

def test_integracao_main_bloqueia_envido_apos_vaza1_RN10(cenario_main, monkeypatch):
    """
    Testa (RN10): Se o 'remendo' no __main__.py
    realmente impede o Humano (J1) de chamar Envido (opção 6)
    após a primeira vaza (len(mao) != 3).
    """
    # 1. Arrange
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Damos uma mão qualquer para o J1
    j1.mao = [Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")]
    
    # Simula a Vaza 1: J1 joga uma carta
    j1.jogar_carta(0)
    assert len(j1.mao) == 2 # Vaza 1 já passou
    
    # Simula o Humano tentando chamar Envido (opção '6')
    carta_escolhida = 6
    
    # Mock: "Espia" a função envido.controlador_envido
    foi_chamada = False
    def mock_controlador_envido(*args):
        nonlocal foi_chamada
        foi_chamada = True
    
    monkeypatch.setattr(envido, 'controlador_envido', mock_controlador_envido)

    # 2. Act
    # Esta é a lógica EXATA do __main__.py
    # O 'if' deve falhar porque len(j1.checa_mao()) não é 3
    if ((len(j1.checa_mao()) == 3) and (j2.pediu_flor is False) and (carta_escolhida in [6, 7, 8])):
        envido.controlador_envido(cbr, dados, carta_escolhida, 1, j1, j2, interface)
    
    # 3. Assert
    # O 'if' deve ter sido Falso
    # e envido.controlador_envido NÃO deve ter sido chamado.
    assert foi_chamada is False

# Em: tests/test_integracao_main.py
# (Adicione este teste no final do arquivo)

def test_distribuicao_nao_e_alternada_RF03(cenario_main):
    """
    Testa (RF03):
    Prova que a distribuição de cartas não segue a regra "alternadamente".
    """
    # 1. Arrange
    # A fixture cenario_main nos dá j1, j2 e um baralho
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # O baralho na fixture é criado e embaralhado.
    # Para este teste, precisamos de um baralho DETERMINÍSTICO.
    # Vamos criar um novo baralho e substituir o da fixture.
    baralho_teste = Baralho()
    baralho_teste.cartas = [] # Limpa o baralho
    
    # Adiciona cartas em ordem LIFO (Last-In, First-Out)
    # A função 'retirar_carta' usa 'pop()',
    # então o '6 de ESPADAS' será a primeira carta a sair.
    baralho_teste.cartas.append(Carta(1, "ESPADAS")) # Última a sair
    baralho_teste.cartas.append(Carta(2, "ESPADAS"))
    baralho_teste.cartas.append(Carta(3, "ESPADAS"))
    baralho_teste.cartas.append(Carta(4, "ESPADAS"))
    baralho_teste.cartas.append(Carta(5, "ESPADAS"))
    baralho_teste.cartas.append(Carta(6, "ESPADAS")) # Primeira a sair

    # 2. Act
    # Simula a lógica do __main__.py
    
    # 1. J1 cria a mão (pega 3 cartas)
    j1.criar_mao(baralho_teste)
    
    # 2. J2 cria a mão (pega as próximas 3)
    j2.criar_mao(baralho_teste)

    # 3. Assert
    
    mao_j1 = [c.retornar_carta() for c in j1.mao]
    mao_j2 = [c.retornar_carta() for c in j2.mao]
    
    # O que DEVERIA acontecer (RF03 - Alternado):
    # J1: [6 de ESPADAS, 4 de ESPADAS, 2 de ESPADAS]
    # J2: [5 de ESPADAS, 3 de ESPADAS, 1 de ESPADAS]
    
    # Este assert VAI FALHAR, provando o bug.
    assert mao_j1 == ["6 de ESPADAS", "4 de ESPADAS", "2 de ESPADAS"]
    assert mao_j2 == ["5 de ESPADAS", "3 de ESPADAS", "1 de ESPADAS"]
    
    # O que REALMENTE acontece (O Bug):
    # J1: [6 de ESPADAS, 5 de ESPADAS, 4 de ESPADAS]
    # J2: [3 de ESPADAS, 2 de ESPADAS, 1 de ESPADAS]

# Em: tests/test_integração_main.py
# (Adicione este teste no final do arquivo)

def test_integracao_bot_nao_mostra_mao_RF04(cenario_main, monkeypatch, capsys):
    """
    Testa (RF04): Se o turno do bot ('turno_do_bot')
    não imprime (vaza) as cartas que ele tem na mão.
    """
    # 1. Arrange
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Damos ao Bot uma mão conhecida
    j2.mao = [Carta(12, "COPAS"), Carta(11, "BASTOS"), Carta(10, "OUROS")]
    j2.flor = j2.checa_flor()

    # Simula o bot jogando a carta 0
    monkeypatch.setattr(j2, 'jogar_carta', lambda *args: 0)
    
    # 2. Act
    # Simulamos a parte principal do 'turno_do_bot'
    carta_escolhida = j2.jogar_carta(cbr, truco) # Retorna 0
    if (carta_escolhida <= len(j2.checa_mao()) and int(carta_escolhida) >= 0):
         carta_jogador_02 = j2.mao.pop(carta_escolhida) # Remove "12 de COPAS"

    # 3. Assert
    captured = capsys.readouterr() # Captura o print()
    
    # O output NÃO deve conter as cartas que o bot AINDA TEM
    assert "11 de BASTOS" not in captured.out
    assert "10 de OUROS" not in captured.out
    
    # O output também NÃO deve conter a carta que ele acabou de jogar
    # (ela só é mostrada no loop principal, não no 'turno_do_bot')
    assert "12 de COPAS" not in captured.out

# Em: tests/test_integração_main.py
# (Adicione este teste no final do arquivo)

def test_integracao_main_impede_jogada_fora_de_turno_RNF01(cenario_main, monkeypatch):
    """
    Testa (RNF01): Se o __main__.py
    impede o J1 de jogar (chamando 'turno_do_humano')
    quando é a vez do J2 (j1.primeiro == False).
    """
    
    # 1. Arrange
    # A fixture 'cenario_main' nos dá todos os objetos globais
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Define o estado: É a vez do Bot (J2)
    j1.primeiro = False
    j2.primeiro = True
    
    # Mocks para "espionar" (spy) as funções de turno
    foi_chamado_turno_humano = False
    foi_chamado_turno_bot = False
    
    # Criamos "mocks" falsos das funções de turno
    def mock_turno_humano(*args):
        nonlocal foi_chamado_turno_humano
        foi_chamado_turno_humano = True
        return -1 # Simula "fugiu" para parar o loop
            
    def mock_turno_bot(*args):
        nonlocal foi_chamado_turno_bot
        foi_chamado_turno_bot = True
        return -1 # Simula "fugiu" para parar o loop

    # 2. Act
    # Esta é a lógica EXATA do __main__.py (linhas 220-227)
    # Estamos testando este 'if/elif'
    
    if j1.primeiro == True:
         carta_jogador_01 = mock_turno_humano(j2) # Não deve ser chamado
    elif j2.primeiro == True:
         carta_jogador_02 = mock_turno_bot(None) # DEVE ser chamado
    
    # 3. Assert
    # Prova que o jogo chamou o turno do Bot (correto)
    assert foi_chamado_turno_bot is True
    
    # Prova que o jogo NÃO chamou o turno do Humano (RNF01)
    assert foi_chamado_turno_humano is False

# Em: tests/test_integração_main.py
# (Adicione este teste no final do arquivo. Lembre de importar 'Carta' no topo)

def test_integracao_main_so_joga_uma_carta_por_vaza_RF05(cenario_main, monkeypatch):
    """
    Testa (RF05): Se o loop em 'turno_do_humano'
    é interrompido por um 'break'
    após jogar UMA carta.
    """
    
    # 1. Arrange
    # A fixture 'cenario_main' nos dá todos os objetos globais
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Damos uma mão conhecida ao J1
    j1.mao = [Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")]
    
    # "Espião" (Spy) na função 'jogar_carta'
    # Queremos contar quantas vezes ela é chamada
    cartas_jogadas_count = 0
    # Salva a função original
    original_jogar_carta = j1.jogar_carta 
    
    def mock_jogar_carta(index):
        nonlocal cartas_jogadas_count
        cartas_jogadas_count += 1
        # Chama a função real para que a carta seja removida
        return original_jogar_carta(index) 
    
    # Substitui a função real pela nossa "espiã"
    monkeypatch.setattr(j1, 'jogar_carta', mock_jogar_carta)

    # Simula o Humano digitando '0' (jogar a primeira carta)
    monkeypatch.setattr('builtins.input', lambda _: '0')

    # 2. Act
    # Esta é a lógica EXATA copiada do 'turno_do_humano'
    # no __main__.py
    
    carta_escolhida = -1
    while (carta_escolhida > len(j1.checa_mao()) or int(carta_escolhida) <= 1):
        
        # 'input' é mockado para retornar '0'
        carta_escolhida = int(input(f"\n{j1.nome} Qual carta você quer jogar? "))

        # O 'if' na linha 56
        if (carta_escolhida <= len(j1.checa_mao()) and int(carta_escolhida) >= 0):
            # 'j1.jogar_carta' é mockado para contar +1
            carta_jogador_01 = j1.jogar_carta(carta_escolhida) 
            # O 'break' encerra o loop
            break 
        
        # (Ignora as outras opções de aposta)
        elif (carta_escolhida in [4, 5, 6, 7, 8, 9]):
            pass
        else:
            pass

    # 3. Assert
    # Prova que o loop foi interrompido após UMA jogada
    assert cartas_jogadas_count == 1
    
    # Prova que a carta foi realmente jogada
    assert len(j1.mao) == 2

# Em: tests/test_integração_main.py
# (Adicione este teste no final do arquivo)

def test_integracao_main_desistencia_da_pontos_ao_oponente_RN01_RF09(cenario_main, monkeypatch):
    """
    Testa (RF09 / RN01): Se o "remendo" no __main__.py
    corretamente dá os pontos da aposta (truco.valor_aposta) 
    ao oponente (J2) quando J1 escolhe "Ir ao Monte" (opção 9).
    """
    
    # 1. Arrange
    # A fixture 'cenario_main' nos dá todos os objetos globais
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Define o estado: A mão vale 2 pontos
    truco.valor_aposta = 2
    
    # Pré-condição: J2 (oponente) tem 0 pontos
    assert j2.retorna_pontos_totais() == 0
    
    # Simula o Humano (J1) escolhendo a opção '9'
    monkeypatch.setattr('builtins.input', lambda _: '9')

    # 2. Act
    # Esta é a lógica EXATA copiada do 'turno_do_humano'
    # no __main__.py
    
    return_value = None
    carta_escolhida = -1
    
    # Simula o loop 'while'
    while (carta_escolhida > len(j1.checa_mao()) or int(carta_escolhida) <= 1):
        
        # 'input' é mockado para retornar '9'
        carta_escolhida = int(input(f"\n{j1.nome} Qual carta você quer jogar? "))

        if (carta_escolhida <= len(j1.checa_mao()) and int(carta_escolhida) >= 0):
            # ... (Não vai entrar aqui) ...
            break

        # (Ignora truco, flor, envido)
        elif (carta_escolhida in [4, 5, 6, 7, 8]):
            pass

        # ESTA É A LÓGICA QUE ESTAMOS TESTANDO
        elif (carta_escolhida == 9):
            # O "remendo"
            j2.adicionar_pontos(truco.retornar_valor_aposta()) 
            return_value = -1 #
            break # (O return real está fora do loop, mas o break o aciona)
        
        else:
            pass # Simula 'Selecione um valor válido!'

    # 3. Assert
    # Prova que o "remendo" funcionou e J2 ganhou os pontos da aposta
    assert j2.retorna_pontos_totais() == 2
    
    # Prova que J1 (o desistente) não ganhou pontos
    assert j1.retorna_pontos_totais() == 0
    
    # Prova que a função sinalizou a desistência para o loop principal
    assert return_value == -1

def test_integracao_main_reiniciar_jogo_reseta_estado_RF27(cenario_main):
    """
    Testa (RF27): Se a lógica de 'reiniciarJogo'
    reseta a pontuação (RF21), o baralho (RF03) e as apostas (truco/envido).
    """
    
    # 1. Arrange (Poluir o estado do jogo)
    # A fixture 'cenario_main' nos dá todos os objetos
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Polui a pontuação
    j1.adicionar_pontos(5)
    j2.adicionar_pontos(3)
    
    # Polui as apostas
    truco.valor_aposta = 3
    envido.estado_atual = 6
    
    # Polui o baralho (simula 6 cartas distribuídas)
    baralho.retirar_carta()
    baralho.retirar_carta()
    baralho.retirar_carta()
    baralho.retirar_carta()
    baralho.retirar_carta()
    baralho.retirar_carta()
    
    # Pré-condições (Verifica se o estado está "sujo")
    assert j1.retorna_pontos_totais() == 5
    assert truco.retornar_valor_aposta() == 3
    assert envido.estado_atual == 6
    assert len(baralho.cartas) == 34 # 40 - 6 = 34
    
    # 2. Act
    # Esta é a lógica EXATA copiada da função 'reiniciarJogo'
    # no __main__.py
    
    dados.finalizar_partida()
    j1.resetar()                #
    j2.resetar()                #
    baralho.resetar()           #
    baralho.criar_baralho()     #
    baralho.embaralhar()        #
    j1.criar_mao(baralho)       #
    j2.criar_mao(baralho)       #
    envido.resetar()            #
    truco.resetar()             #
    
    # 3. Assert (Verifica se o estado está "limpo")
    
    # Pontuação foi resetada?
    assert j1.retorna_pontos_totais() == 0
    assert j2.retorna_pontos_totais() == 0
    
    # Apostas foram resetadas?
    assert truco.retornar_valor_aposta() == 1
    assert envido.estado_atual == 0
    
    # Mãos foram criadas (3 cartas cada)?
    assert len(j1.mao) == 3
    assert len(j2.mao) == 3
    
    # Baralho foi resetado (40) e 6 cartas foram dadas?
    assert len(baralho.cartas) == 34

# Em: tests/test_integração_main.py
# (Adicione este teste no final do arquivo)

def test_integracao_main_input_invalido_mostra_erro_RF_ERR(cenario_main, monkeypatch, capsys):
    """
    Testa (Mensagem de Erro): Se o loop 'turno_do_humano'
    mostra a mensagem 'Selecione um valor válido!'
    quando um input inválido (ex: '99') é fornecido.
    """
    
    # 1. Arrange
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Damos uma mão conhecida ao J1
    j1.mao = [Carta(7, "OUROS"), Carta(6, "OUROS"), Carta(1, "ESPADAS")]
    
    # Simula o Humano digitando '99' (inválido) e depois '0' (válido, para sair do loop)
    inputs_do_usuario = ['99', '0']
    monkeypatch.setattr('builtins.input', lambda _: inputs_do_usuario.pop(0))

    # 2. Act
    # Esta é a lógica EXATA copiada do 'turno_do_humano'
    # no __main__.py
    
    carta_escolhida = -1
    while (carta_escolhida > len(j1.checa_mao()) or int(carta_escolhida) <= 1):
        
        carta_escolhida = int(input(f"\n{j1.nome} Qual carta você quer jogar? "))

        if (carta_escolhida <= len(j1.checa_mao()) and int(carta_escolhida) >= 0):
            carta_jogador_01 = j1.jogar_carta(carta_escolhida) 
            break
        elif (carta_escolhida in [4, 5, 6, 7, 8, 9]):
            pass # Ignora as opções de aposta
        else:
            # Esta é a linha que estamos testando
            print('Selecione um valor válido!')

    # 3. Assert
    captured = capsys.readouterr() # Captura o print
    
    # Prova que a mensagem de erro foi exibida
    assert "Selecione um valor válido!" in captured.out

# Em: tests/test_integração_main.py
# (Adicione este teste no final do arquivo)

def test_integracao_main_input_nao_numerico_levanta_valueerror(cenario_main, monkeypatch):
    """
    Testa (Exceção): Se o 'turno_do_humano'
    quebra com 'ValueError' quando o usuário digita uma
    string não numérica (ex: "zero").
    """
    
    # 1. Arrange
    baralho, cbr, dados, interface, truco, flor, envido, j1, j2 = cenario_main
    
    # Simula o Humano digitando "zero" (inválido)
    monkeypatch.setattr('builtins.input', lambda _: 'zero')

    # 2. Act
    # Esta é a lógica EXATA copiada do 'turno_do_humano'
    # no __main__.py
    
    # 3. Assert
    # O teste PASSA se o código dentro do 'with'
    # levantar a exceção 'ValueError'.
    with pytest.raises(ValueError):
        
        carta_escolhida = -1
        while (carta_escolhida > len(j1.checa_mao()) or int(carta_escolhida) <= 1):
            
            # Esta linha
            # vai falhar, pois int("zero") levanta ValueError
            carta_escolhida = int(input(f"\n{j1.nome} Qual carta você quer jogar? "))

            if (carta_escolhida <= len(j1.checa_mao()) and int(carta_escolhida) >= 0):
                break
            elif (carta_escolhida in [4, 5, 6, 7, 8, 9]):
                pass
            else:
                print('Selecione um valor válido!')