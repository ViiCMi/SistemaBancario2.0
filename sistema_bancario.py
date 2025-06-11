import sqlite3
from datetime import datetime
import re

# Configuração do banco de dados
def inicializar_banco():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    # Criar tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        cpf TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        data_nascimento TEXT NOT NULL,
        endereco TEXT NOT NULL
    )
    ''')
    
    # Criar tabela de contas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contas (
        numero INTEGER PRIMARY KEY,
        agencia TEXT NOT NULL,
        cpf_usuario TEXT NOT NULL,
        saldo REAL NOT NULL,
        FOREIGN KEY (cpf_usuario) REFERENCES usuarios(cpf)
    )
    ''')
    
    # Criar tabela de transações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_conta INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        valor REAL NOT NULL,
        data_hora TEXT NOT NULL,
        FOREIGN KEY (numero_conta) REFERENCES contas(numero)
    )
    ''')
    
    conn.commit()
    return conn, cursor

# Função para depósito (positional only)
def deposito(saldo, valor, extrato, /, *, conn, cursor, numero_conta):
    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Atualizar saldo na conta
        cursor.execute("UPDATE contas SET saldo = ? WHERE numero = ?", (saldo, numero_conta))
        
        # Registrar transação
        cursor.execute(
            "INSERT INTO transacoes (numero_conta, tipo, valor, data_hora) VALUES (?, ?, ?, ?)",
            (numero_conta, "Depósito", valor, data_hora)
        )
        
        conn.commit()
        print("Depósito realizado com sucesso!")
    else:
        print("Operação falhou! O valor informado é inválido.")
    
    return saldo, extrato

# Função para saque (keyword only)
def saque(*, saldo, valor, extrato, limite, numero_saques, limite_saques, conn, cursor, numero_conta):
    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= limite_saques

    if excedeu_saldo:
        print("Operação falhou! Você não tem saldo suficiente.")
    
    elif excedeu_limite:
        print("Operação falhou! O valor do saque excede o limite.")
    
    elif excedeu_saques:
        print("Operação falhou! Número máximo de saques excedido.")
    
    elif valor > 0:
        saldo -= valor
        extrato += f"Saque: R$ {valor:.2f}\n"
        numero_saques += 1
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Atualizar saldo na conta
        cursor.execute("UPDATE contas SET saldo = ? WHERE numero = ?", (saldo, numero_conta))
        
        # Registrar transação
        cursor.execute(
            "INSERT INTO transacoes (numero_conta, tipo, valor, data_hora) VALUES (?, ?, ?, ?)",
            (numero_conta, "Saque", valor, data_hora)
        )
        
        conn.commit()
        print("Saque realizado com sucesso!")
    
    else:
        print("Operação falhou! O valor informado é inválido.")
    
    return saldo, extrato, numero_saques

# Função para extrato (positional only e keyword only)
def exibir_extrato(saldo, /, *, extrato, conn, cursor, numero_conta):
    print("\n================ EXTRATO ================")
    
    # Buscar transações do banco de dados
    cursor.execute(
        "SELECT tipo, valor, data_hora FROM transacoes WHERE numero_conta = ? ORDER BY data_hora",
        (numero_conta,)
    )
    transacoes = cursor.fetchall()
    
    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for tipo, valor, data_hora in transacoes:
            print(f"{data_hora} - {tipo}: R$ {valor:.2f}")
    
    print(f"\nSaldo: R$ {saldo:.2f}")
    print("=========================================")
    
    return extrato

# Função para criar usuário
def criar_usuario(conn, cursor):
    while True:
        cpf = input("Informe o CPF (somente números): ")
        # Remover caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        
        if not cpf:
            print("CPF não pode ser vazio. Tente novamente.")
            continue
            
        if len(cpf) != 11:
            print("CPF deve conter 11 dígitos. Tente novamente.")
            continue
        
        # Verificar se o CPF já existe
        cursor.execute("SELECT cpf FROM usuarios WHERE cpf = ?", (cpf,))
        if cursor.fetchone():
            print("\nErro! Já existe um usuário com esse CPF.")
            opcao = input("Deseja tentar novamente? (s/n): ")
            if opcao.lower() != 's':
                return
            continue
        break
    
    # Validar formato do nome
    while True:
        nome = input("Informe o nome completo: ")
        if ' ' in nome and len(nome.split()) >= 2:
            break
        print("Por favor, informe nome e sobrenome.")
    
    # Validar formato da data de nascimento
    while True:
        data_nascimento = input("Informe a data de nascimento (DD/MM/AAAA): ")
        if re.match(r'^\d{2}/\d{2}/\d{4}$', data_nascimento):
            break
        print("Formato de data inválido. Use: DD/MM/AAAA")
    
    # Validar formato do endereço
    while True:
        endereco = input("Informe o endereço (logradouro, numero - bairro - cidade/UF): ")
        if re.match(r'.+,.+-.+-.+/.+', endereco):
            break
        print("Formato de endereço inválido. Use: logradouro, numero - bairro - cidade/UF")
    
    cursor.execute(
        "INSERT INTO usuarios (cpf, nome, data_nascimento, endereco) VALUES (?, ?, ?, ?)",
        (cpf, nome, data_nascimento, endereco)
    )
    conn.commit()
    
    print("\nUsuário criado com sucesso!")
    
    # Criar automaticamente uma conta bancária para o usuário
    # Obter o próximo número de conta
    cursor.execute("SELECT MAX(numero) FROM contas")
    resultado = cursor.fetchone()[0]
    numero_conta = 1 if resultado is None else resultado + 1
    
    agencia = "0001"
    saldo = 0.0
    
    cursor.execute(
        "INSERT INTO contas (numero, agencia, cpf_usuario, saldo) VALUES (?, ?, ?, ?)",
        (numero_conta, agencia, cpf, saldo)
    )
    conn.commit()
    
    print(f"\nConta criada automaticamente para o usuário!")
    print(f"Agência: {agencia}")
    print(f"Número da conta: {numero_conta}")

# Função para criar conta corrente
def criar_conta(conn, cursor):
    while True:
        cpf = input("Informe o CPF do usuário (somente números): ")
        cpf = re.sub(r'\D', '', cpf)
        
        if not cpf:
            print("CPF não pode ser vazio. Tente novamente.")
            continue
            
        if len(cpf) != 11:
            print("CPF deve conter 11 dígitos. Tente novamente.")
            continue
        
        # Verificar se o usuário existe
        cursor.execute("SELECT cpf FROM usuarios WHERE cpf = ?", (cpf,))
        if not cursor.fetchone():
            print("\nErro! Usuário não encontrado.")
            opcao = input("Deseja tentar novamente? (s/n): ")
            if opcao.lower() != 's':
                return
            continue
        break
    
    # Obter o próximo número de conta
    cursor.execute("SELECT MAX(numero) FROM contas")
    resultado = cursor.fetchone()[0]
    numero_conta = 1 if resultado is None else resultado + 1
    
    agencia = "0001"
    saldo = 0.0
    
    cursor.execute(
        "INSERT INTO contas (numero, agencia, cpf_usuario, saldo) VALUES (?, ?, ?, ?)",
        (numero_conta, agencia, cpf, saldo)
    )
    conn.commit()
    
    print(f"\nConta criada com sucesso!")
    print(f"Agência: {agencia}")
    print(f"Número da conta: {numero_conta}")

# Função para consulta
def consultar(conn, cursor):
    print("\n================ CONSULTA ================\n")
    print("[1] Consultar por CPF")
    print("[2] Consultar por Conta/Agência")
    opcao = input("=> ")
    
    if opcao == "1":
        cpf = input("Informe o CPF (somente números): ")
        cpf = re.sub(r'\D', '', cpf)
        
        # Buscar usuário
        cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf,))
        usuario = cursor.fetchone()
        
        if not usuario:
            print("\nUsuário não encontrado.")
            return
        
        # Exibir dados do usuário
        print("\n--- DADOS DO USUÁRIO ---")
        print(f"CPF: {usuario[0]}")
        print(f"Nome: {usuario[1]}")
        print(f"Data de Nascimento: {usuario[2]}")
        print(f"Endereço: {usuario[3]}")
        
        # Buscar contas do usuário
        cursor.execute("SELECT * FROM contas WHERE cpf_usuario = ?", (cpf,))
        contas = cursor.fetchall()
        
        if not contas:
            print("\nUsuário não possui contas.")
            return
        
        # Exibir contas e movimentações
        for conta in contas:
            print(f"\n--- CONTA {conta[0]} ---")
            print(f"Agência: {conta[1]}")
            print(f"Saldo: R$ {conta[3]:.2f}")
            
            # Buscar movimentações
            cursor.execute(
                "SELECT tipo, valor, data_hora FROM transacoes WHERE numero_conta = ? ORDER BY data_hora",
                (conta[0],)
            )
            transacoes = cursor.fetchall()
            
            if transacoes:
                print("\nMovimentações:")
                for tipo, valor, data_hora in transacoes:
                    print(f"{data_hora} - {tipo}: R$ {valor:.2f}")
            else:
                print("\nNenhuma movimentação registrada.")
    
    elif opcao == "2":
        agencia = input("Informe a agência: ")
        numero_conta = input("Informe o número da conta: ")
        
        # Buscar conta
        cursor.execute("SELECT * FROM contas WHERE agencia = ? AND numero = ?", (agencia, numero_conta))
        conta = cursor.fetchone()
        
        if not conta:
            print("\nConta não encontrada.")
            return
        
        # Buscar usuário
        cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (conta[2],))
        usuario = cursor.fetchone()
        
        # Exibir dados da conta e usuário
        print("\n--- DADOS DA CONTA ---")
        print(f"Agência: {conta[1]}")
        print(f"Número: {conta[0]}")
        print(f"Saldo: R$ {conta[3]:.2f}")
        
        print("\n--- DADOS DO TITULAR ---")
        print(f"CPF: {usuario[0]}")
        print(f"Nome: {usuario[1]}")
        print(f"Data de Nascimento: {usuario[2]}")
        print(f"Endereço: {usuario[3]}")
        
        # Buscar movimentações
        cursor.execute(
            "SELECT tipo, valor, data_hora FROM transacoes WHERE numero_conta = ? ORDER BY data_hora",
            (conta[0],)
        )
        transacoes = cursor.fetchall()
        
        if transacoes:
            print("\nMovimentações:")
            for tipo, valor, data_hora in transacoes:
                print(f"{data_hora} - {tipo}: R$ {valor:.2f}")
        else:
            print("\nNenhuma movimentação registrada.")
    
    else:
        print("Opção inválida!")

# Função para relatório
def gerar_relatorio(conn, cursor):
    print("\n================ RELATÓRIO ================\n")
    print("[1] Organizar por CPF")
    print("[2] Organizar por Número da Conta")
    opcao = input("=> ")
    
    if opcao == "1":
        # Buscar usuários ordenados por CPF
        cursor.execute("SELECT * FROM usuarios ORDER BY cpf")
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("\nNenhum usuário cadastrado.")
            return
        
        print("\n--- RELATÓRIO DE USUÁRIOS E CONTAS (ORDENADO POR CPF) ---")
        for usuario in usuarios:
            print(f"\nCPF: {usuario[0]}")
            print(f"Nome: {usuario[1]}")
            print(f"Data de Nascimento: {usuario[2]}")
            print(f"Endereço: {usuario[3]}")
            
            # Buscar contas do usuário
            cursor.execute("SELECT * FROM contas WHERE cpf_usuario = ?", (usuario[0],))
            contas = cursor.fetchall()
            
            if contas:
                print("\nContas:")
                for conta in contas:
                    print(f"  Agência: {conta[1]} | Conta: {conta[0]} | Saldo: R$ {conta[3]:.2f}")
                    
                    # Contar transações
                    cursor.execute(
                        "SELECT COUNT(*) FROM transacoes WHERE numero_conta = ?",
                        (conta[0],)
                    )
                    num_transacoes = cursor.fetchone()[0]
                    print(f"  Total de movimentações: {num_transacoes}")
            else:
                print("\nNenhuma conta cadastrada.")
    
    elif opcao == "2":
        # Buscar contas ordenadas por número
        cursor.execute("""
            SELECT c.numero, c.agencia, c.saldo, u.cpf, u.nome 
            FROM contas c 
            JOIN usuarios u ON c.cpf_usuario = u.cpf 
            ORDER BY c.numero
        """)
        contas = cursor.fetchall()
        
        if not contas:
            print("\nNenhuma conta cadastrada.")
            return
        
        print("\n--- RELATÓRIO DE CONTAS (ORDENADO POR NÚMERO) ---")
        for conta in contas:
            print(f"\nConta: {conta[0]}")
            print(f"Agência: {conta[1]}")
            print(f"Saldo: R$ {conta[2]:.2f}")
            print(f"CPF do Titular: {conta[3]}")
            print(f"Nome do Titular: {conta[4]}")
            
            # Contar transações
            cursor.execute(
                "SELECT COUNT(*) FROM transacoes WHERE numero_conta = ?",
                (conta[0],)
            )
            num_transacoes = cursor.fetchone()[0]
            print(f"Total de movimentações: {num_transacoes}")
    
    else:
        print("Opção inválida!")

# Função principal modificada
def main():
    conn, cursor = inicializar_banco()
    
    LIMITE_SAQUES = 3
    limite = 500
    
    menu = """
    ================ MENU ================
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [u] Novo Usuário
    [c] Nova Conta
    [q] Consultar
    [r] Relatório
    [x] Sair
    => """
    
    extrato = ""
    numero_saques = 0
    
    while True:
        opcao = input(menu)
        
        if opcao == "d":
            # Sempre perguntar qual conta ou CPF
            print("\nInforme os dados para depósito:")
            print("[1] Buscar por Conta/Agência")
            print("[2] Buscar por CPF")
            opcao_busca = input("=> ")
            
            if opcao_busca == "1":
                agencia = input("Agência: ")
                numero_conta = input("Número da conta: ")
                
                cursor.execute(
                    "SELECT numero, saldo FROM contas WHERE agencia = ? AND numero = ?",
                    (agencia, numero_conta)
                )
                resultado = cursor.fetchone()
                
                if not resultado:
                    print("Conta não encontrada!")
                    continue
                
                conta_selecionada = resultado[0]
                saldo = resultado[1]
            
            elif opcao_busca == "2":
                cpf = input("CPF do titular (somente números): ")
                cpf = re.sub(r'\D', '', cpf)
                
                # Verificar se o usuário existe
                cursor.execute("SELECT cpf FROM usuarios WHERE cpf = ?", (cpf,))
                if not cursor.fetchone():
                    print("Usuário não encontrado!")
                    continue
                
                # Buscar contas do usuário
                cursor.execute("SELECT numero, agencia, saldo FROM contas WHERE cpf_usuario = ?", (cpf,))
                contas = cursor.fetchall()
                
                if not contas:
                    print("Usuário não possui contas!")
                    continue
                
                if len(contas) == 1:
                    conta_selecionada = contas[0][0]
                    saldo = contas[0][2]
                    print(f"Conta selecionada: Agência {contas[0][1]}, Número {contas[0][0]}")
                else:
                    print("\nContas disponíveis:")
                    for i, conta in enumerate(contas):
                        print(f"[{i+1}] Agência: {conta[1]}, Conta: {conta[0]}, Saldo: R$ {conta[2]:.2f}")
                    
                    while True:
                        try:
                            escolha = int(input("Escolha uma conta (número): "))
                            if 1 <= escolha <= len(contas):
                                conta_selecionada = contas[escolha-1][0]
                                saldo = contas[escolha-1][2]
                                break
                            else:
                                print("Opção inválida!")
                        except ValueError:
                            print("Por favor, digite um número válido.")
            else:
                print("Opção inválida!")
                continue
            
            valor = float(input("Informe o valor do depósito: "))
            saldo, extrato = deposito(saldo, valor, extrato, conn=conn, cursor=cursor, numero_conta=conta_selecionada)
        
        elif opcao == "s":
            # Sempre perguntar qual conta ou CPF
            print("\nInforme os dados para saque:")
            print("[1] Buscar por Conta/Agência")
            print("[2] Buscar por CPF")
            opcao_busca = input("=> ")
            
            if opcao_busca == "1":
                agencia = input("Agência: ")
                numero_conta = input("Número da conta: ")
                
                cursor.execute(
                    "SELECT numero, saldo FROM contas WHERE agencia = ? AND numero = ?",
                    (agencia, numero_conta)
                )
                resultado = cursor.fetchone()
                
                if not resultado:
                    print("Conta não encontrada!")
                    continue
                
                conta_selecionada = resultado[0]
                saldo = resultado[1]
            
            elif opcao_busca == "2":
                cpf = input("CPF do titular (somente números): ")
                cpf = re.sub(r'\D', '', cpf)
                
                # Verificar se o usuário existe
                cursor.execute("SELECT cpf FROM usuarios WHERE cpf = ?", (cpf,))
                if not cursor.fetchone():
                    print("Usuário não encontrado!")
                    continue
                
                # Buscar contas do usuário
                cursor.execute("SELECT numero, agencia, saldo FROM contas WHERE cpf_usuario = ?", (cpf,))
                contas = cursor.fetchall()
                
                if not contas:
                    print("Usuário não possui contas!")
                    continue
                
                if len(contas) == 1:
                    conta_selecionada = contas[0][0]
                    saldo = contas[0][2]
                    print(f"Conta selecionada: Agência {contas[0][1]}, Número {contas[0][0]}")
                else:
                    print("\nContas disponíveis:")
                    for i, conta in enumerate(contas):
                        print(f"[{i+1}] Agência: {conta[1]}, Conta: {conta[0]}, Saldo: R$ {conta[2]:.2f}")
                    
                    while True:
                        try:
                            escolha = int(input("Escolha uma conta (número): "))
                            if 1 <= escolha <= len(contas):
                                conta_selecionada = contas[escolha-1][0]
                                saldo = contas[escolha-1][2]
                                break
                            else:
                                print("Opção inválida!")
                        except ValueError:
                            print("Por favor, digite um número válido.")
            else:
                print("Opção inválida!")
                continue
            
            # Verificar número de saques para esta conta
            cursor.execute(
                "SELECT COUNT(*) FROM transacoes WHERE numero_conta = ? AND tipo = 'Saque' AND data_hora LIKE ?",
                (conta_selecionada, datetime.now().strftime("%Y-%m-%d") + "%")
            )
            numero_saques = cursor.fetchone()[0]
            
            valor = float(input("Informe o valor do saque: "))
            
            saldo, extrato, numero_saques = saque(
                saldo=saldo,
                valor=valor,
                extrato=extrato,
                limite=limite,
                numero_saques=numero_saques,
                limite_saques=LIMITE_SAQUES,
                conn=conn,
                cursor=cursor,
                numero_conta=conta_selecionada
            )
        
        elif opcao == "e":
            # Sempre perguntar qual conta ou CPF
            print("\nInforme os dados para consulta de extrato:")
            print("[1] Buscar por Conta/Agência")
            print("[2] Buscar por CPF")
            opcao_busca = input("=> ")
            
            if opcao_busca == "1":
                agencia = input("Agência: ")
                numero_conta = input("Número da conta: ")
                
                cursor.execute(
                    "SELECT numero, saldo FROM contas WHERE agencia = ? AND numero = ?",
                    (agencia, numero_conta)
                )
                resultado = cursor.fetchone()
                
                if not resultado:
                    print("Conta não encontrada!")
                    continue
                
                conta_selecionada = resultado[0]
                saldo = resultado[1]
            
            elif opcao_busca == "2":
                cpf = input("CPF do titular (somente números): ")
                cpf = re.sub(r'\D', '', cpf)
                
                # Verificar se o usuário existe
                cursor.execute("SELECT cpf FROM usuarios WHERE cpf = ?", (cpf,))
                if not cursor.fetchone():
                    print("Usuário não encontrado!")
                    continue
                
                # Buscar contas do usuário
                cursor.execute("SELECT numero, agencia, saldo FROM contas WHERE cpf_usuario = ?", (cpf,))
                contas = cursor.fetchall()
                
                if not contas:
                    print("Usuário não possui contas!")
                    continue
                
                if len(contas) == 1:
                    conta_selecionada = contas[0][0]
                    saldo = contas[0][2]
                    print(f"Conta selecionada: Agência {contas[0][1]}, Número {contas[0][0]}")
                else:
                    print("\nContas disponíveis:")
                    for i, conta in enumerate(contas):
                        print(f"[{i+1}] Agência: {conta[1]}, Conta: {conta[0]}, Saldo: R$ {conta[2]:.2f}")
                    
                    while True:
                        try:
                            escolha = int(input("Escolha uma conta (número): "))
                            if 1 <= escolha <= len(contas):
                                conta_selecionada = contas[escolha-1][0]
                                saldo = contas[escolha-1][2]
                                break
                            else:
                                print("Opção inválida!")
                        except ValueError:
                            print("Por favor, digite um número válido.")
            else:
                print("Opção inválida!")
                continue
            
            exibir_extrato(saldo, extrato=extrato, conn=conn, cursor=cursor, numero_conta=conta_selecionada)
        
        elif opcao == "u":
            criar_usuario(conn, cursor)
        
        elif opcao == "c":
            criar_conta(conn, cursor)
        
        elif opcao == "q":
            consultar(conn, cursor)
        
        elif opcao == "r":
            gerar_relatorio(conn, cursor)
        
        elif opcao == "x":
            break
        
        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")
    
    conn.close()

if __name__ == "__main__":
    main()