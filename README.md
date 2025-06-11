


          
# 🏦 Sistema Bancário Python 3000 🚀

## 💰 Seu dinheiro, nossa responsabilidade! 💰


## 🌟 O que é isso?

Bem-vindo ao **Sistema Bancário Python 3000** - a solução bancária que você sempre sonhou! Este sistema foi desenvolvido com Python puro e SQLite para oferecer uma experiência bancária completa, segura e eficiente. Quem precisa de bancos reais quando você tem código?

## 🔥 Funcionalidades Incríveis

### 💵 Operações Básicas

- **Depósito** - Faça chuva de dinheiro na sua conta! (Desde que seja seu, claro)
- **Saque** - Retire seu dinheiro quando precisar, mas lembre-se das regras!
- **Extrato** - Veja para onde foi todo aquele dinheiro que você jurava ter guardado

### 👤 Gestão de Usuários

- **Cadastro de Usuários** - Registre-se com nome, CPF, data de nascimento e endereço
- **Criação Automática de Conta** - Ao cadastrar um usuário, uma conta bancária é criada automaticamente! 🎁
- **Consulta de Usuários** - Encontre usuários mais rápido que achar meias combinando

### 🏛️ Gestão de Contas

- **Criação de Contas** - Abra quantas contas quiser (seu gerente ficaria orgulhoso)
- **Consulta de Contas** - Veja detalhes da sua conta sem precisar enfrentar filas

### 📊 Relatórios

- **Relatórios Personalizados** - Dados organizados por CPF ou número de conta
- **Histórico de Transações** - Cada centavo rastreado com data e hora

### 🛡️ Validações Aprimoradas

- **Preenchimento Seguro** - Validações em tempo real para todos os campos
- **Segunda Chance** - Errou algo? O sistema permite que você tente novamente!

## 🚀 Como Usar

1. Execute o arquivo `sistema_bancario.py`
2. Navegue pelo menu interativo:

```
================ MENU ================
[d] Depositar
[s] Sacar
[e] Extrato
[u] Novo Usuário
[c] Nova Conta
[q] Consultar
[r] Relatório
[x] Sair
```

## 🧠 Detalhes Técnicos (Para os Curiosos)

### 🔄 Funções Principais

#### 💸 Função `deposito()`
- **O que faz**: Adiciona dinheiro à sua conta
- **Como funciona**: Recebe argumentos apenas por posição (positional only)
- **Parâmetros**: Saldo atual, valor a depositar, extrato
- **Bônus**: Registra tudo no banco de dados com data e hora

#### 💰 Função `saque()`
- **O que faz**: Retira dinheiro da sua conta (se você tiver)
- **Como funciona**: Recebe argumentos apenas por nome (keyword only)
- **Parâmetros**: Saldo, valor, extrato, limite, número de saques, limite de saques
- **Regras**: Máximo de 3 saques diários, limite de R$500 por saque

#### 📝 Função `exibir_extrato()`
- **O que faz**: Mostra todas as suas movimentações
- **Como funciona**: Recebe argumentos por posição e nome
- **Exibição**: Transações organizadas por data e hora

#### 👤 Função `criar_usuario()`
- **O que faz**: Cadastra novos clientes no sistema
- **Validações**: CPF único, nome com sobrenome, formato de endereço
- **Armazenamento**: Dados salvos no banco SQLite

#### 🏦 Função `criar_conta()`
- **O que faz**: Cria contas bancárias vinculadas a usuários
- **Detalhes**: Agência fixa (0001), número sequencial
- **Vínculo**: Uma conta pertence a um usuário, mas um usuário pode ter várias contas

#### 🔍 Função `consultar()`
- **O que faz**: Busca informações de usuários e contas
- **Opções**: Consulta por CPF ou por número da conta/agência
- **Exibição**: Dados do usuário, conta e movimentações

#### 📊 Função `gerar_relatorio()`
- **O que faz**: Apresenta dados gerais do sistema
- **Organização**: Por CPF ou por número da conta
- **Conteúdo**: Usuários, contas e resumo de transações

## 💾 Banco de Dados

Todas as informações são armazenadas em um banco SQLite com as seguintes tabelas:

- **Usuários**: CPF, nome, data de nascimento, endereço
- **Contas**: Número, agência, CPF do usuário, saldo
- **Transações**: ID, número da conta, tipo, valor, data/hora

## 🛠️ Requisitos

- Python 3.x
- SQLite (já incluído na biblioteca padrão do Python)

## 🔮 Próximas Atualizações

- Interface gráfica (porque CLIs são tão século XX)
- Transferências entre contas (compartilhe a riqueza!)
- Investimentos (faça seu dinheiro trabalhar enquanto você dorme)

---

## 🎯 Desenvolvido com ❤️ e muito ☕

*"Seu dinheiro está seguro conosco... provavelmente."* 😉
        