import cv2
import numpy as np
from Crypto.Cipher import AES
import base64
import os

# AES Encryption Function
def encrypt_message(message, password):
    password = password.ljust(16, ' ')[:16]  # Ensure 16-byte key
    cipher = AES.new(password.encode(), AES.MODE_ECB)
    padded_msg = message.ljust((len(message) + 15) // 16 * 16)  # Pad to multiple of 16
    encrypted_msg = cipher.encrypt(padded_msg.encode())
    return base64.b64encode(encrypted_msg).decode()  # Convert to base64 for easy storage

# AES Decryption Function
def decrypt_message(encrypted_msg, password):
    password = password.ljust(16, ' ')[:16]  # Ensure 16-byte key
    cipher = AES.new(password.encode(), AES.MODE_ECB)
    decrypted_msg = cipher.decrypt(base64.b64decode(encrypted_msg))
    return decrypted_msg.decode().strip()  # Remove padding

# Encode message into LSB of image
def encode_message(image_path, secret_message, password):
    img = cv2.imread(image_path)
    encrypted_msg = encrypt_message(secret_message, password) + "####"  # End marker
    binary_msg = ''.join(format(ord(i), '08b') for i in encrypted_msg)

    height, width, _ =  img.shape  # Corrected

    idx = 0

    for row in range(height):
        for col in range(width):
            for color in range(3):  # Iterate over R, G, B
                if idx < len(binary_msg):
                    img[row, col, color] = (img[row, col, color] & 0xFE) | int(binary_msg[idx])
                    idx += 1
                else:
                    break

    cv2.imwrite("stego_image.png", img)
    print("Message successfully hidden in 'stego_image.png'")

# Decode message from LSB of image
def decode_message(image_path, password):
    img = cv2.imread(image_path)
    binary_msg = ""
    
    height, width, _ = img.shape
    for row in range(height):
        for col in range(width):
            for color in range(3):
                binary_msg += str(img[row, col, color] & 1)

    byte_msg = [binary_msg[i:i+8] for i in range(0, len(binary_msg), 8)]
    decoded_msg = ''.join(chr(int(b, 2)) for b in byte_msg)
    
    if "####" in decoded_msg:
        encrypted_msg = decoded_msg.split("####")[0]
        try:
            decrypted_msg = decrypt_message(encrypted_msg, password)
            print("Decrypted message:", decrypted_msg)
        except:
            print("Incorrect password or corrupted data")
    else:
        print("No hidden message found")

# Usage
image_file = "c2.jpg"  # Replace with your image path
message = input("Enter secret message: ")
password = input("Enter passcode: ")

encode_message(image_file, message, password)

# Decryption
decode_pass = input("Enter passcode to decrypt: ")
decode_message("stego_image.png", decode_pass)
