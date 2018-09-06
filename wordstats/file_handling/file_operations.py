import codecs


# useful methods for handling files

def load_from_path(path):
    try:
        with codecs.open(path, encoding="utf8") as file:
            content = file.read()

    except FileNotFoundError:
        print(path + " not found, creating empty file.")
        codecs.open(path, encoding="utf8", mode="w")
        content = load_from_path(path)

    return content


def save_to_file(path, content):
    with codecs.open(path, encoding="utf8", mode="w") as words_file:
        words_file.write(content)


def append_to_file(path, content):
    with codecs.open(path, encoding="utf8", mode="a") as words_file:
        words_file.writelines(content + "\n")
