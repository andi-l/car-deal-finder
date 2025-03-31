from cryptography.fernet import Fernet
import os
import yaml

class ConfigEncryptor:
    @staticmethod
    def generate_key(key_path="../../utils/encryption/encryption.key"):
        """
            Generate a new encryption key and save it to a file.
        """
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
        return key

    @staticmethod
    def load_key(key_path="../../utils/encryption/encryption.key"):
        """
            Load the encryption key from a file.
        """
        #if no key found generate new
        if not os.path.exists(key_path):
            return ConfigEncryptor.generate_key(key_path)

        with open(key_path, "rb") as key_file:
            return key_file.read()

    @staticmethod
    def encrypt_config(config_path="../../utils/config/db_config.yaml"):
        """
            Encrypt db credentials in the config file.
        """
        #load original config
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        # Load encryption key
        key = ConfigEncryptor.load_key()
        fernet = Fernet(key)

        # Encrypt db name and password
        if "database" in config:
            # Check if credentials are already encrypted
            if "name" in config["database"] and "password" in config["database"]:
                db_name = config["database"]["name"]
                db_password = config["database"]["password"]

                #encrypt credentials
                encrypted_name = fernet.encrypt(db_name.encode()).decode()
                encrypted_password = fernet.encrypt(db_password.encode()).decode()

                #replace plain with encrypted credentials
                config["database"]["encrypted_name"] = encrypted_name
                config["database"]["encrypted_password"] = encrypted_password

                #remove plaintext original
                del config["database"]["password"]
                del config["database"]["name"]

        # Save encrypted config
        with open(config_path, "w") as file:
            yaml.safe_dump(config, file)

        print(f"Encrypted config saved to {config_path}")

    @staticmethod
    def decrypt_config(encrypted_config_path="../../utils/config/db_config.yaml"
                       ) -> object:
        """
            Decrypt sensitive credentials in the config file.
        """
        # Load the encrypted config
        with open(encrypted_config_path, "r") as file:
            config = yaml.safe_load(file)

        # Load encryption key
        key = ConfigEncryptor.load_key()
        fernet = Fernet(key)

        # Decrypt database credentials
        if "database" in config:
            if "encrypted_name" in config["database"] and "encrypted_password" in config["database"]:
                # Decrypt credentials
                decrypted_name = fernet.decrypt(
                    config["database"]["encrypted_name"].encode()
                ).decode()
                decrypted_password = fernet.decrypt(
                    config["database"]["encrypted_password"].encode()
                ).decode()

                # Replace encrypted credentials with decrypted ones
                config["database"]["name"] = decrypted_name
                config["database"]["password"] = decrypted_password

                # Remove encrypted fields
                del config["database"]["encrypted_name"]
                del config["database"]["encrypted_password"]

        return config