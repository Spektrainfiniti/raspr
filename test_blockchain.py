from blockchain import *

def test_1():
    server = Server()
    miner = Miner()
    net = Network()

    net.add_host(server, "192.168.0.1")
    net.add_host(miner, "192.168.0.2")


    transaction = {
        "sender" : "",
        "recipient" : "",
        "amount" : 5
    }
    miner.send_transaction_in_blockchain(transaction, "192.168.0.1")
