import streamlit as st
import hashlib
import time
from typing import List


# --- Core Blockchain Classes ---
class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float, description: str = ""):
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
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        transactions_str = "".join(str(tx) for tx in self.transactions)
        value = f"{self.index}{self.timestamp}{transactions_str}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(value.encode()).hexdigest()

    def mine_block(self, difficulty: int):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self, difficulty: int = 3, reward: float = 50):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        self.reward = reward

    def create_genesis_block(self):
        return Block(0, [Transaction("System", "Genesis", 0)], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction):
        if transaction.sender and transaction.recipient and transaction.amount > 0:
            self.pending_transactions.append(transaction)
            return True
        return False

    def mine_pending_transactions(self, miner_address: str):
        if len(self.pending_transactions) == 0:
            return False
        new_block = Block(len(self.chain), self.pending_transactions[:], self.get_latest_block().hash)
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

# --- Persistent State ---
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

# --- Streamlit App ---
st.title("BEATS Blockchain: Chia-Inspired Model")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Adicionar Transação",
        "Minerar Bloco",
        "Visualizar Blockchain",
        "Estatísticas",
        "Validar Blockchain",
    ],
)

blockchain = st.session_state.blockchain

# --- Menu: Adicionar Transação ---
if menu == "Adicionar Transação":
    st.header("Adicionar Transação")
    sender = st.text_input("Remetente:")
    recipient = st.text_input("Destinatário:")
    amount = st.number_input("Valor:", min_value=0.01, step=0.01)
    description = st.text_area("Descrição:")
    if st.button("Adicionar Transação"):
        transaction = Transaction(sender, recipient, amount, description)
        if blockchain.add_transaction(transaction):
            st.success("Transação adicionada com sucesso!")
        else:
            st.error("Erro ao adicionar transação. Verifique os dados.")

# --- Menu: Minerar Bloco ---
elif menu == "Minerar Bloco":
    st.header("Minerar Bloco")
    miner_address = st.text_input("Endereço do Minerador:")
    if st.button("Minerar"):
        if blockchain.mine_pending_transactions(miner_address):
            st.success("Bloco minerado com sucesso!")
        else:
            st.warning("Nenhuma transação pendente para minerar.")

# --- Menu: Visualizar Blockchain ---
elif menu == "Visualizar Blockchain":
    st.header("Blockchain")
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

# --- Menu: Estatísticas ---
elif menu == "Estatísticas":
    st.header("Estatísticas do Blockchain")
    total_blocks = len(blockchain.chain)
    total_transactions = sum(len(block.transactions) for block in blockchain.chain)
    total_reward = sum(
        tx.amount for block in blockchain.chain for tx in block.transactions if tx.sender == "System"
    )
    last_miner = blockchain.chain[-1].transactions[-1].recipient if len(blockchain.chain) > 1 else "Nenhum"

    st.write(f"**Blocos Minerados:** {total_blocks}")
    st.write(f"**Transações Realizadas:** {total_transactions}")
    st.write(f"**Recompensa Total aos Mineradores:** {total_reward} BEAT")
    st.write(f"**Último Minerador:** {last_miner}")

# --- Menu: Validar Blockchain ---
elif menu == "Validar Blockchain":
    st.header("Validar Blockchain")
    if blockchain.is_chain_valid():
        st.success("O blockchain é válido!")
    else:
        st.error("O blockchain é inválido!")
