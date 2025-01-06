import streamlit as st
import hashlib
import time
import uuid


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

    def mine_pending_transactions(self, miner_address):
        if len(self.pending_transactions) == 0:
            return False
        new_block = Block(len(self.chain), time.time(), self.pending_transactions[:], self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = [Transaction("System", miner_address, self.reward)]
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

# Gerar o identificador do minerador
miner_id = str(uuid.uuid4())
st.sidebar.title("Minerador")
st.sidebar.write(f"Seu código único de minerador (para uso): `{miner_id}`")


# Interface do Streamlit
st.title("BEATS Blockchain")

menu = st.sidebar.selectbox("Menu", ["Adicionar Transação", "Minerar Bloco", "Visualizar Blockchain", "Validar Blockchain"])

# Aba: Adicionar Transação
if menu == "Adicionar Transação":
    st.header("Adicionar Transação")
    sender = st.text_input("Remetente:")
    recipient = st.text_input("Destinatário:")
    amount = st.number_input("Valor:", min_value=0.0, step=0.01)
    description = st.text_area("Descrição:")
    if st.button("Adicionar Transação"):
        if sender and recipient and amount > 0:
            transaction = Transaction(sender, recipient, amount, description)
            added = blockchain.add_transaction(transaction)
            if added:
                st.success("Transação adicionada com sucesso!")
            else:
                st.error("Erro ao adicionar transação.")
        else:
            st.error("Por favor, preencha todos os campos corretamente.")

# Aba: Minerar Bloco
elif menu == "Minerar Bloco":
    st.header("Minerar Bloco")
    st.write(f"Seu código de minerador: `{miner_id}`")
    miner_address = st.text_input("Insira o endereço do minerador:")
    if st.button("Minerar"):
        if miner_address:
            success = blockchain.mine_pending_transactions(miner_address)
            if success:
                st.success("Bloco minerado com sucesso! As transações pendentes foram incluídas no blockchain.")
            else:
                st.warning("Nenhuma transação pendente para minerar.")
        else:
            st.error("Por favor, insira o endereço do minerador.")

# Aba: Visualizar Blockchain
elif menu == "Visualizar Blockchain":
    st.header("Blockchain")
    
    # Exibe as transações pendentes
    if len(blockchain.pending_transactions) > 0:
        st.subheader("Transações Pendentes")
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
        if len(block.transactions) > 0:
            for tx in block.transactions:
                st.write(f"- {tx}")
        else:
            st.write("Nenhuma transação neste bloco.")
        st.write("---")

# Aba: Validar Blockchain
elif menu == "Validar Blockchain":
    st.header("Validar Blockchain")
    is_valid = blockchain.is_chain_valid()
    if is_valid:
        st.success("O blockchain é válido!")
    else:
        st.error("O blockchain não é válido!")
