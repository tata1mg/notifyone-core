import base64

from torpedo import CONFIG

from Crypto.Cipher import AES


class Crypto:

    PROVIDERS_DATA_ENCRYPTION = CONFIG.config.get("PROVIDERS", {}).get("ENCRYPTION")

    @classmethod
    def encrypt(cls, message):
        obj = AES.new(cls.PROVIDERS_DATA_ENCRYPTION["KEY"], AES.MODE_CFB, cls.PROVIDERS_DATA_ENCRYPTION["AES_IV"])
        ciphertext = obj.encrypt(message)
        return str(base64.b64encode(ciphertext), 'utf-8')

    @classmethod
    def decrypt(cls, encrypted_message):
        obj = AES.new(cls.PROVIDERS_DATA_ENCRYPTION["KEY"], AES.MODE_CFB, cls.PROVIDERS_DATA_ENCRYPTION["AES_IV"])
        return obj.decrypt(base64.b64decode(encrypted_message)).decode('utf-8')
