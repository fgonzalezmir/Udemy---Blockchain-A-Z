# Module 2 - Create a Cryptocurrency

# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

# Importing the libraries -----------------------------------------------------
import datetime
import hashlib
import json

# Importamos en este caso también request de Flask, porque tenemos que conectar
# los nodos unos con otros vía GET.
from flask import Flask, jsonify, request

# La usaremos para comprobar las cadenas de los diferentes nodos para hacer el
# el consenso.
import requests 

# Lo importamos para crear la url de cada nodo.                        
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain ----------------------------------------------

class Blockchain:
    
    def __init__(self):
        self.chain = []
        
        # Almacenamos las transacciones. Estas transacciones cuando se mine un 
        # bloque se añadirán al bloque. Es importasnte crear este array de 
        # transacciones antes de crear el bloque génesis. Si no daría error.
        self.transactions = []
        
        self.create_block(proof = 1, previous_hash = '0')
        
        # Almacena los nodos de la red.
        self.nodes = set()
    
    def create_block(self, proof, previous_hash):
        '''
        Function create_block que crea un blque
        
        Imputs:
            proof: Nonce
            previous_hash: Hash del bloque previo
        
        Oyput:
            Un bloque.
        '''
        
        # Añadimos al bloque las transcciones.
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        
        # Eliminamos todas las transacciones ya que hab sido insertadas en el
        # bloque.
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        '''
        Function get_previous_block que nos devuelve el indice del bloque 
        anterior
        
        Output:
            (block) Bloque anterior. Es un diccionario.
        '''
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        '''
        function add_transaction que añade una transacción.
        
        Inputs:
                sender: El que envía la transacción.
                receiver: Quién la recive
                amount: Importe de la transacción
        
        Output:
            (integer) El indice del bloque actual al que se le añade la 
            transacción.
        '''
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        '''
        Function add_node que añade un nodo a la red de nuestro blockchain.
        
        Input:
            adddress: URL del nuevo nodo.
        '''
        # parseamos la dirección:
        # address = 'http://127.0.0.1:5000/'
        # parsed_url = ParseResult(scheme='http', netloc='127.0.0.1:5000',
        #                          path='/', params='', query='', fragment='')
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        '''
        Function replace_chain que reemplaza cualquier cadena que sea menor 
        que la cadena más larga por la cadena más larga que sea válida.
        
        Tiene el argumento self porque esta operación se va a realizar en cada
        uno de los nodos.
        
        Output:
            
            [True, False] en función de si se ha reemplazado o no.
            
        '''
        # Obtenemos todos los nodos.
        network = self.nodes
        
        # Inicializamos la variable que tendrá la cadema más larga
        longest_chain = None
        
        # Variable que emplearemos para calcular la cadena más larga. 
        max_length = len(self.chain)
        
        # Recorremos todos los nodos de la red.
        for node in network:
            # Hacemos una llamada a las APIs rest de todos los nodos para que 
            # nos envién la cadena y su longitud.
            # Para ello empleamos la funcion del import requests. 
            response = requests.get(f'http://{node}/get_chain')
            
            # Si la respuesta es correcta (http 200)
            if response.status_code == 200:
                
                #Obtenemos la longitud de la cadena y la cadena.
                length = response.json()['length']
                chain = response.json()['chain']
                
                # Si la longitud de la cadena del otro nodo es mayor que la del
                # nodo y la remota es una cadena valida, la copiamos sobre la
                # del nodo.
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        
        # Si la dena no es Null            
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

# Part 2 - Mining our Blockchain ----------------------------------------------

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5000
# str(uuid4())  ='31cad115-e129-4ecc-aea3-8be5cde238d8'
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # Añadimos una transacción. Hacemos que cuando unn minero minq un bloque
    # gane algo de dinero.
    blockchain.add_transaction(sender = node_address, receiver = 'Hadelin', amount = 1)
    
    block = blockchain.create_block(proof, previous_hash)
    
    #En esta caso añadimos tambien a la respuesta las transacciones.
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    
    # HTTP 201 Created 
    return jsonify(response), 201

# Part 3 - Decentralizing our Blockchain --------------------------------------

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Hadcoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5000)
