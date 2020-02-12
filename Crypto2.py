from cryptography.hazmat.backends               import default_backend
from cryptography.hazmat.primitives.asymmetric  import rsa
from cryptography.hazmat.primitives             import serialization
from cryptography.hazmat.primitives             import hashes
from cryptography.hazmat.primitives.asymmetric  import padding

class crypto:
  privateKey = rsa
  publicKey = rsa


  #Generating Public and Private Keys
  def genKeys(self):
    global privateKey, publicKey
    privateKey = rsa.generate_private_key(
      public_exponent = 65537,
      key_size = 2352,
      backend = default_backend()
    )
    publicKey = privateKey.public_key()


  #Serialization and Storing of keys
  def storeKeys(self):
    global privateKey, publicKey
    pemFile = privateKey.private_bytes(
      encoding = serialization.Encoding.PEM,
      format = serialization.PrivateFormat.PKCS8,
      encryption_algorithm = serialization.BestAvailableEncryption(b'mypassword')
    )
    with open("privateKey.pem", "wb") as file:
      file.write(pemFile)

    pemFile = publicKey.public_bytes(
      encoding = serialization.Encoding.PEM,
      format = serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open("publicKey.pem", "wb") as file:
      file.write(pemFile)


  #Loading the keys
  def loadPrivateKey(self):
    with open("privateKey.pem", "rb") as file:
      privateKey = serialization.load_pem_private_key(
        file.read(),
        password = b'mypassword',
        backend = default_backend()
      )
    return privateKey.private_bytes(
      encoding = serialization.Encoding.PEM,
      format = serialization.PrivateFormat.PKCS8,
      encryption_algorithm = serialization.BestAvailableEncryption(b'mypassword')
    )


  def loadPublicKey(self):
    with open("publicKey.pem", "rb") as file:
      publicKey = serialization.load_pem_public_key(
        file.read(),
        backend = default_backend()
      )
    return publicKey.public_bytes(
      encoding = serialization.Encoding.PEM,
      format = serialization.PublicFormat.SubjectPublicKeyInfo
    )


  def loadPublicKeyFromBytes(self, bytes):
    publicKey = serialization.load_pem_public_key(
      bytes,
      backend = default_backend()
    )
    return publicKey


  def loadPrivateKeyFromBytes(self, bytes):
    pKey = serialization.load_pem_private_key(
        bytes,
        password = b'mypassword',
        backend = default_backend()
      )
    return pKey


  #Encyption and Decryption methods
  def encryptData(self, data):
    global publicKey
    message = bytes(data)
    cipherText = publicKey.encrypt(
      message,
      padding.OAEP(
        mgf = padding.MGF1(algorithm=hashes.SHA256()),
        algorithm = hashes.SHA256(),
        label=None
      )
    )
    return cipherText


  def encryptData(self, data, key):
    message = bytes(data.encode("UTF-8"))
    cipherText = key.encrypt(
      message,
      padding.OAEP(
        mgf = padding.MGF1(algorithm=hashes.SHA256()),
        algorithm = hashes.SHA256(),
        label=None
      )
    )
    return cipherText


  def decryptData(self, data):
    global privateKey
    plainText = privateKey.decrypt(
      data,
      padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
      )
    )
    return plainText


  def signMessage(self, message):
    signature = privateKey.sign(
      message,
      padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
      ),
      hashes.SHA256()
    )
    return signature
