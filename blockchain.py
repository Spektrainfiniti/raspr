from base import *
from time import time
import hashlib, json


class NetworkInterface(NetworkInterface):
    def __init__(self):
        super().__init__()
    
    def send_transaction_in_blockchain(self, transaction, addr):
        if not self.net:
            return "No network"
        return self.net.send_transaction_in_blockchain(self.addr, addr, transaction)


class Network(Network):
    def __init__(self):
        super().__init__()
    
    def send_transaction_in_blockchain(self, src_addr, dst_addr, transaction):
        if dst_addr in self.__hosts:
            return self.__hosts[dst_addr]
        return "Unknown host"


class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []
 
        # Создание блока генезиса
        self.new_block(previous_hash=1, proof=100)
        
    def new_block(self, proof, previous_hash=None):
        """
        Создание нового блока в блокчейне
 
        :param proof: <int> Доказательства проведенной работы
        :param previous_hash: (Опционально) хеш предыдущего блока
        :return: <dict> Новый блок
        """
 
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
 
        # Перезагрузка текущего списка транзакций
        self.current_transactions = []
 
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender, recipient, amount):
        """
        Направляет новую транзакцию в следующий блок
 
        :param sender: <str> Адрес отправителя
        :param recipient: <str> Адрес получателя
        :param amount: <int> Сумма
        :return: <int> Индекс блока, который будет хранить эту транзакцию
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
 
        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
        """
        Создает хэш SHA-256 блока
 
        :param block: <dict> Блок
        :return: <str>
        """
 
        # Мы должны убедиться в том, что словарь упорядочен, иначе у нас будут непоследовательные хеши
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
 
    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Простая проверка алгоритма:
         - Поиска числа p`, так как hash(pp`) содержит 4 заглавных нуля, где p - предыдущий
         - p является предыдущим доказательством, а p` - новым
 
        :param last_proof: <int>
        :return: <int>
        """
 
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
 
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Подтверждение доказательства: Содержит ли hash(last_proof, proof) 4 заглавных нуля?
 
        :param last_proof: <int> Предыдущее доказательство
        :param proof: <int> Текущее доказательство
        :return: <bool> True, если правильно, False, если нет.
        """
 
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


class Server(Comp): 
    def __init__(self):
        self.__iface : NetworkInterface = NetworkInterface()
        self.__data : Any = None
        self.blockchain : Blockchain = Blockchain()

    def mine(self, node_identifier):
        # Мы запускаем алгоритм подтверждения работы, чтобы получить следующее подтверждение…
        last_block = self.blockchain.last_block
        last_proof = last_block['proof']
        proof = self.blockchain.proof_of_work(last_proof)
    
        # Мы должны получить вознаграждение за найденное подтверждение
        # Отправитель “0” означает, что узел заработал крипто-монету
        self.blockchain.new_transaction(
            sender="0",
            recipient=node_identifier,
            amount=1,
        )
    
        # Создаем новый блок, путем внесения его в цепь
        previous_hash = self.blockchain.hash(last_block)
        block = self.blockchain.new_block(proof, previous_hash)
    
        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
        return response

    def new_transaction(self, values):
        # Убедитесь в том, что необходимые поля были переданы
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return 'Missing values'
    
        # Создание новой транзакции
        index = self.blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
        response = {'message': f'Transaction will be added to Block {index}'}
        return response

    def full_chain(self):
        response = {
            'chain': self.blockchain.chain,
            'length': len(self.blockchain.chain),
        }
        return response


class Miner(Comp):
    def __init__(self):
        self.__iface : NetworkInterface = NetworkInterface()
        self.__data : Any = None

    def send_transaction_in_blockchain(self, transaction, addr):
        return self.iface().send_transaction_in_blockchain(transaction, addr)