import streamlit as st
import hashlib
import time


# Classes para o Blockchain
class Transaction:
    def __init__(self, sender, recipient, amount, description=""):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.description = description
        self.timestamp = time.time()
        self.transaction_id = self.calculate_hash()

    def calculate_hash(self):
        tx_data = f"{self.sender}{self.recipient}{self.amount}{self.description}{self.timestamp}"
        return hashlib.sha256(tx_data.encode()).hexdigest()

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.amount} BEAT | {self.description}"


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        transactions_str = "".join(str(tx) for tx in self.transactions)
        value = f"{self.index}{self.timestamp}{transactions_str}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(value.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class BeatCoinBlockchain:
    def __init__(self, difficulty=3, reward=50):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.reward = reward
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(0, time.time(), [Transaction("System", "Genesis", 0)], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        if transaction.sender and transaction.recipient and transaction.amount > 0:
            self.pending_transactions.append(transaction)
            return True
        return False

    def mine_pending_transactions(self, miner_name):
        if len(self.pending_transactions) == 0:
            return False
        # Cria um novo bloco com as transações pendentes
        new_block = Block(len(self.chain), time.time(), self.pending_transactions[:], self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        # Adiciona a recompensa ao minerador como nova transação pendente
        self.pending_transactions = [Transaction("System", miner_name, self.reward)]
        return True

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True


# Inicializa o blockchain
blockchain = BeatCoinBlockchain()

# Lista de mineradores registrados
registered_miners = {}


# Funções de registro e login
def register_miner(username, password):
    if username in registered_miners:
        return False, "Usuário já existe."
    registered_miners[username] = hashlib.sha256(password.encode()).hexdigest()
    return True, "Usuário registrado com sucesso."


def login_miner(username, password):
    if username not in registered_miners:
        return False, "Usuário não encontrado."
    if registered_miners[username] != hashlib.sha256(password.encode()).hexdigest():
        return False, "Senha incorreta."
    return True, "Login realizado com sucesso."


# Interface do Streamlit
st.title("BEATS Blockchain")

# Aba para registro e login
menu = st.sidebar.selectbox(
    "Menu",
    [
        "Registrar Minerador",
        "Login Minerador",
        "Mineração Inicial",
        "Adicionar Transação",
        "Minerar Bloco",
        "Visualizar Blockchain",
        "Histórico de Transações",
        "Estatísticas do Blockchain",
        "Validar Blockchain",
        "Reiniciar Blockchain",
    ],
)

current_user = st.session_state.get("current_user", None)

# Aba: Registrar Minerador
if menu == "Registrar Minerador":
    st.header("Registrar Minerador")
    username = st.text_input("Nome de Usuário:")
    password = st.text_input("Senha:", type="password")
    if st.button("Registrar"):
        success, message = register_miner(username, password)
        if success:
            st.success(message)
        else:
            st.error(message)

# Aba: Login Minerador
elif menu == "Login Minerador":
    st.header("Login Minerador")
    username = st.text_input("Nome de Usuário:")
    password = st.text_input("Senha:", type="password")
    if st.button("Login"):
        success, message = login_miner(username, password)
        if success:
            st.session_state["current_user"] = username
            st.success(message)
        else:
            st.error(message)

# Aba: Mineração Inicial
elif menu == "Mineração Inicial":
    if not current_user:
        st.error("Por favor, faça login para acessar esta funcionalidade.")
    else:
        st.header("Mineração Inicial")
        if st.button("Iniciar Mineração Inicial"):
            # Transação inicial para dar BEATs ao minerador
            initial_transaction = Transaction("System", current_user, 100, "Mineração Inicial")
            blockchain.add_transaction(initial_transaction)
            success = blockchain.mine_pending_transactions(current_user)
            if success:
                st.success("Mineração inicial concluída! Você recebeu 100 BEAT.")
            else:
                st.warning("Erro durante a mineração inicial.")

# Aba: Adicionar Transação
elif menu == "Adicionar Transação":
    if not current_user:
        st.error("Por favor, faça login para acessar esta funcionalidade.")
    else:
        st.header("Adicionar Transação")
        recipient = st.text_input("Destinatário:")
        amount = st.number_input("Valor:", min_value=0.0, step=0.01)
        description = st.text_area("Descrição:")
        if st.button("Adicionar Transação"):
            transaction = Transaction(current_user, recipient, amount, description)
            added = blockchain.add_transaction(transaction)
            if added:
                st.success("Transação adicionada com sucesso!")
            else:
                st.error("Erro ao adicionar transação.")

# Aba: Minerar Bloco
elif menu == "Minerar Bloco":
    if not current_user:
        st.error("Por favor, faça login para acessar esta funcionalidade.")
    else:
        st.header("Minerar Bloco")
        if st.button("Minerar"):
            success = blockchain.mine_pending_transactions(current_user)
            if success:
                st.success("Bloco minerado com sucesso! As transações pendentes foram incluídas no blockchain.")
            else:
                st.warning("Nenhuma transação pendente para minerar.")

# Aba: Visualizar Blockchain
elif menu == "Visualizar Blockchain":
    st.header("Blockchain")
    
    # Exibe as transações pendentes
    st.subheader("Transações Pendentes")
    if len(blockchain.pending_transactions) > 0:
        for tx in blockchain.pending_transactions:
            st.write(f"- {tx}")
    else:
        st.write("Nenhuma transação pendente no momento.")
    
    # Exibe os blocos do blockchain
    st.subheader("Blocos Minerados")
    for block in blockchain.chain:
        st.subheader(f"Bloco {block.index}")
        st.write(f"Timestamp: {block.timestamp}")
        st.write(f"Hash: {block.hash}")
        st.write(f"Hash Anterior: {block.previous_hash}")
        st.write("Transações:")
        for tx in block.transactions:
            st.write(f"- {tx}")
        st.write("---")

# Outras abas como "Histórico de Transações", "Estatísticas", "Validar Blockchain", e "Reiniciar Blockchain" permanecem inalteradas.
