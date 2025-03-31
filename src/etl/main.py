from src.etl.extraction import DataExtractor
from src.etl.transformation import DataTransformer
from load import DatabaseLoader
from utils.encryption.encryption import ConfigEncryptor

import yaml


def main():
    config_file = "../../utils/config/db_config.yaml"

    with open(config_file) as file:
        config = yaml.safe_load(file)

    #Extract data
    with DataExtractor(config["database"]["paths"]["raw_data"]) as extractor:
        raw_data = extractor.extract_data()

    #Transform data
    with DataTransformer(raw_data) as transformer:
        transformed_data = transformer.transform_data()

        #save data to csv for loading
        transformed_data.to_csv(config["database"]["paths"]["transformed_csv"]
                            , index=False)

    #Load data into database
    with DatabaseLoader(config_file) as db_loader:
        db_loader.load_transformed_data(transformed_data)

    #Encrypt db credentials in config
    ConfigEncryptor.encrypt_config()

    #Decrypt db credentials from config
    decrypted_config = ConfigEncryptor.decrypt_config()
    #print(yaml.dump(decrypted_config))

if __name__ == "__main__":
    main()