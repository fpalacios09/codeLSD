import hashlib
import json
import os
from time import time

class UpdateBlock:
    def __init__(self, index, timestamp, version, script_name, script_hash, previous_hash, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.version = version
        self.script_name = script_name
        self.script_hash = script_hash
        self.previous_hash = previous_hash
        self.hash = hash if hash else self.calculate_hash()

    def calculate_hash(self):
        block_content = f"{self.index}{self.timestamp}{self.version}{self.script_name}{self.script_hash}{self.previous_hash}"
        return hashlib.sha256(block_content.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "version": self.version,
            "script_name": self.script_name,
            "script_hash": self.script_hash,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            version=data["version"],
            script_name=data["script_name"],
            script_hash=data["script_hash"],
            previous_hash=data["previous_hash"],
            hash=data["hash"]
        )

class UpdateBlockchain:
    def __init__(self):
        self.chain = []

    def create_genesis_block(self):
        return UpdateBlock(0, time(), "0.0", "init.py", "0", "0")

    def load_chain(self, filename="update_chain.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                self.chain = [UpdateBlock.from_dict(b) for b in data]
        else:
            self.chain = [self.create_genesis_block()]

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, version, script_name, script_hash):
        last_block = self.get_last_block()
        new_block = UpdateBlock(
            index=len(self.chain),
            timestamp=time(),
            version=version,
            script_name=script_name,
            script_hash=script_hash,
            previous_hash=last_block.hash
        )
        self.chain.append(new_block)

    def save_chain(self, filename="update_chain.json"):
        with open(filename, "w") as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=4)

    def save_last_block(self, filename="last_update.json"):
        last_block = self.get_last_block()
        with open(filename, "w") as f:
            json.dump(last_block.to_dict(), f, indent=4)

    def save_genesis_block(self, filename="block_gen.json"):
        genesis_block = self.chain[0]
        with open(filename, "w") as f:
            json.dump(genesis_block.to_dict(), f, indent=4)

def calcular_hash_archivo(path):
    with open(path, "rb") as f:
        contenido = f.read()
    return hashlib.sha256(contenido).hexdigest()

# 🛠️ Parámetros del nuevo script
script_path = "/home/pi-lsd/Desktop/code/blockchain001/updates/track_v1_0.py"  # Ruta absoluta o relativa
version = "1.0"

# 🧱 Construcción de la blockchain
bc = UpdateBlockchain()
bc.load_chain()  # Carga desde JSON o crea génesis
script_hash = calcular_hash_archivo(script_path)
bc.add_block(version, script_path, script_hash)
bc.save_chain()  # Guarda el JSON completo con la cadena actualizada

# 📝 Guarda solo el último bloque
bc.save_last_block()  

# 📄 Guarda el bloque génesis aparte
bc.save_genesis_block()
