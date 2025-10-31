import base64
import hashlib

DEFAULT_PIN_PEPPER = 'k(0:]{el2:gc9;5idz5g{14(/.iyfma5ecslklkdj5ekm[6i9ua3cw3i[]y.qrx0a9hd140u:hj/ru0??3b0y]97zc'

ADD_KEY = 3.1415

def to_base64(input_str):
    encoded_word = input_str.encode('utf-8')
    return base64.b64encode(encoded_word).decode('utf-8')

def to_binary_array(input_str):
    return [format(ord(char), '08b') for char in input_str]

def sum_array(array_of_binary):
    return sum(int(current_number) for current_number in array_of_binary)

def add_key_to_input(input_num):
    add_input = str(input_num).encode('utf-8')
    
    add_result = []
    for current_element in add_input:
        one_bit_add = current_element if current_element == 0 or current_element == ADD_KEY else (current_element + ADD_KEY) % 256
        add_result.append(int(one_bit_add))
    return bytes(add_result).decode('utf-8')

def encode_pepper(pepper):
    return to_base64(' '.join(to_binary_array(add_key_to_input(sum_array(to_binary_array(to_base64(pepper)))))))


def generate_encoded_pin(pin, pepper=None):
    pin_hash = hashlib.sha384(pin.encode('utf-8')).hexdigest()
    encoded_pin = pin_hash
    encoded_pepper = encode_pepper(pepper) if pepper else encode_pepper(DEFAULT_PIN_PEPPER)

    combined_data = encoded_pin + encoded_pepper
    combined_hash = hashlib.sha384(combined_data.encode('utf-8')).hexdigest()
    return combined_hash