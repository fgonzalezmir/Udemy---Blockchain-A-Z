# Module 1 - Create a Blockchain

# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/

# Importing the libraries -----------------------------------------------------
import datetime

# Para hacer los hash de los bloques.
import hashlib  

# usaremos la funcion dumps para codificarlo cuando tengamos el hash del bloque 
import json
                
# Importamos Flask para crear la aplicación web. 
# Importamos jsonify para poder interaccionar con Postman.
from flask import Flask, jsonify

# Part 1 - Building a Blockchain ---------------------------------------------

class Blockchain:

    def __init__(self):
        self.chain = []  #Para la cadena de bloques.
        
        # Creamos el Genesis Block
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self, proof, previous_hash):
        '''
        Función que crea un bloque.
        
        Parametros:
            proof: proof of work (Nonce)
            previous_hash: Hash del boque previo.
        
        Devuelve:
            Un bloque.
        '''
        
        #Definimos la estructura del bloque.
        # De momento no añadimos datos al bloque. En el modulo2 si que lo haremos.
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        
        #Añadimos el bloque a la cadena.
        self.chain.append(block)
        
        return block

    def get_previous_block(self):
        '''
        Función que devuelve el bloque anterior de la cadena.
        '''
        #Devolvemos el ultimo bloque de la actual cadena.
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        '''
        Función que nos calcula el proof of work (Nonce)
        
        Parametros:
            previous_proof: proof of work anterior. Se usa para calcular el
            nuevo proof. Asi conseguimos distanciar al máximo el nuevo del 
            anterior proof.
        
        Devuelve:
            El nuevo valor del proof of work.
        '''
        new_proof = 1 # Inicializamos el nuevo proof a 1.
        check_proof = False
        
        while check_proof is False:
            
            #Se busca una operación asimetrica. P.e new_proof + previous_proof 
            #es igual a previous_proof + new_proof y eso no funcionaria.
            #Para minar el bloque solo usaremos el proof antiguo y el nuevo. Es 
            #el reto que empleamos para nuestro blockchain.
            #El encode() nos pasa de string a cadena binaria.
            #hexdigest() nos lo pasa a cadena hexadecimal.
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        '''
        Función que nos calcula el hash del bloque.
        
        Paramtetros:
            block: Es el bloque alq ue queremos hacer el hash
        
        Devuelve:
            Nos devuelva el bloque hasheado en formato hexadecimal.
        '''
        
        #Lo primero que tenemos que hacer es pasar el diccionario del bloque a
        #string -->json.dumps y con las claves siempre en el mismo orden.
        #obtenemos una cadena binaria debido al encode()
        encoded_block = json.dumps(block, sort_keys = True).encode()
        
        #Nos devuelve el bloque hasheado como cadena hexadecimal.
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        '''
        Función que valida que la cadena sea correcta. Valida dos cosas:
            1. Que el previous_hash sea correcto en todos los bloques.
            2. Que el proof of work de cada uno sea correcto.
        
        Parametros:
            chain: La cadena de bloques a validar.
        
        Devuelve:
            Devuelve True si la cadena es correcta y False si no lo es.
        '''
        
        #Inicializamos las variables del loop.
        previous_block = chain[0] # Bloque Génesis.
        block_index = 1 # Indice del bloque posterior al genesis.
        
        #Iteramos por todos los bloques de la cadena.
        while block_index < len(chain):
            block = chain[block_index]
            
            #Validamos el previous_hash
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            #Validamos el proof of work
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index += 1
        return True

# Part 2 - Mining our Blockchain ----------------------------------------------

# Creating a Web App
# Para crearla emprearemos Flask.
app = Flask(__name__)

# Creating a Blockchain
# Creamos una instancia de nuestra clase Blockchain.
blockchain = Blockchain()

# Mining a new block
# El decorador route() indica a Flask la ruta donde la función tiene que
# hacer trigger.
# Por defecto Flask te pone la aplicación en http://127.0.0.1:5000/
# Como no tenemmos que enviar nada y solo recibimos el resultado ponemos como
# metodos solo GET.
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    '''
    Metodo que nos mina un nuevo bloque para la cadena
    
    Devuelve:
        Nos devuelve un JSON con la respuesta de la creación del bloque.
        La respuesta HTTP 200: The request has succeeded.
    '''
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    '''
    Metodo que nos devuelve toda la cadena
    
    Devuelve:
        La cadena de bloques
        La respuesta HTTP 200: The request has succeeded.
    '''
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    '''
    Metodo que valida la cadena.
    
    Devuelve:
        Un mensaje indicando si es correcto o no
        La respuesta HTTP 200: The request has succeeded.
    '''
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Running the app
# Decimos a Flask que ejecute la aplicación en el host:0.0.0.0 y el puerto 5000
# Esto se hace para hacer la aplicación visible desde otras IPs distintas a las
# del propio host. Esto hace al host 'public available'.
app.run(host = '0.0.0.0', port = 5000)
