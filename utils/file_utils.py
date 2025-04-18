import os

def save_text(text, file_path):
    """ Save generated text to a file """
    with open(file_path, "w") as f:
        f.write(text)

def read_text(file_path):
    """ Read text from a file """
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    return None
