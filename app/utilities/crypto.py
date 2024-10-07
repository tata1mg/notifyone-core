import base64

from torpedo import CONFIG

from Crypto.Cipher import AES


class Crypto:

    @staticmethod
    def encrypt(message):
        obj = AES.new(CONFIG.config.get('ENCRYPTION_KEY'), AES.MODE_CFB, CONFIG.config.get('AES_IV'))
        ciphertext = obj.encrypt(message)
        return str(base64.b64encode(ciphertext), 'utf-8')

    @staticmethod
    def decrypt(encrypted_message):
        obj = AES.new(CONFIG.config.get('ENCRYPTION_KEY'), AES.MODE_CFB, CONFIG.config.get('AES_IV'))
        return obj.decrypt(base64.b64decode(encrypted_message)).decode('utf-8')
