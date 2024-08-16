# encrypt.py
# pip install cryptography

from cryptography.fernet import Fernet
import os

def generate_key():
    return Fernet.generate_key()

def encrypt_file(file_path, key):
    with open(file_path, 'rb') as f:
        data = f.read()
    
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data)
    
    with open(file_path + '.encrypted', 'wb') as f:
        f.write(encrypted_data)


def encrypt_files_in_folder(folder_path, key):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key)
            if file.endswith('.pdf'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key) 
            if file.endswith('.exe'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key) 
            if file.endswith('.docx'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key) 
            if file.endswith('.jpg'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key) 
            if file.endswith('.png'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key)
            if file.endswith('.mp3'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key)
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key)  
            if file.endswith('.hidden'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key)    
            if file.endswith('.pptx'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key) 
            if file.endswith('.zip'):
                file_path = os.path.join(root, file)
                encrypt_file(file_path, key)                                             

if __name__ == "__main__":
    key = b'-PZ9W2oYPv4LjMLTGMgaIzMH0tr8gH2tGruoMy7du28='  # Provide the same key for encryption and decryption
    folder_path = 'backup'
    encrypt_files_in_folder(folder_path, key)
    print("Files encrypted successfully.")
