# decrypt.py

from cryptography.fernet import Fernet
import os

def decrypt_file(file_path, key, decrypted_folder):
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()

    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    
    decrypted_file_path = file_path[:-10]  # Removing '.encrypted' from the file name
    decrypted_file_path = os.path.join(decrypted_folder, os.path.basename(decrypted_file_path))

    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)

def decrypt_files_in_folder(folder_path, key, decrypted_folder):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.encrypted'):
                file_path = os.path.join(root, file)
                decrypt_file(file_path, key, decrypted_folder)
                

if __name__ == "__main__":
    key = b'-PZ9W2oYPv4LjMLTGMgaIzMH0tr8gH2tGruoMy7du28='  # Provide the same key used for encryption
    encrypted_folder_path = 'backup'
    decrypted_folder_path = 'decrypt'  # Specify the desired location for decrypted files
    decrypt_files_in_folder(encrypted_folder_path, key, decrypted_folder_path)
    print("Files decrypted successfully.")

