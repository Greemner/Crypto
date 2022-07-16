def permutation(text, key):
    import textwrap
    text = text.replace(' ', '')
    result = ""
    parts_of_text = textwrap.wrap(text, len(key))
    for part in parts_of_text:
        while len(part) < len(key):
            part += " "
        for i in range(len(part)):
            res_index = int(key[i]) - 1
            result += part[res_index]
    result = ''.join(result.split())

    return result.lower()


def ceasar(text, key):
    import re
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    result = ""
    key = int(key)
    text = re.sub(r'[^\w\s]', '', text.lower()).split()

    for word in text:
        new_word = ""
        for i in word:
            new_word += alphabet[(alphabet.index(i) + key) % len(alphabet)]
        result += new_word + " "
    result = result.strip()
    result = ''.join(result.split())

    return result


def new_encode_vijn(text, key):
    from itertools import cycle
    import re
    text = text.lower()
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    f = lambda arg: alphabet[(alphabet.index(arg[0]) + alphabet.index(arg[1])) % len(alphabet)]
    result = ""

    text = re.sub(r'[^\w\s]', '', text).split()

    len_words = [len(word) for word in text]
    one_word_text = "".join(text)
    encrypt_one_word_text = ''.join(map(f, zip(one_word_text, cycle(key))))

    for i in range(len(len_words)):
        result += encrypt_one_word_text[:len_words[i]] + " "
        encrypt_one_word_text = encrypt_one_word_text[len_words[i]:]

    result = result.strip()
    result = ''.join(result.split())

    return result


def pleifer(plaintext, pseudo):
    import itertools

    def chunker(seq, size):
        it = iter(seq)
        while True:
            chunk = tuple(itertools.islice(it, size))
            if not chunk:
                return
            yield chunk

    def prepare_input(dirty):
        symbols = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        dirty = "".join([c.upper() for c in dirty if c in symbols])
        clean = ""

        if len(dirty) < 2:
            return dirty

        for i in range(len(dirty) - 1):
            clean += dirty[i]

            if dirty[i] == dirty[i + 1]:
                clean += "Ь"

        clean += dirty[-1]

        if len(clean) & 1:
            clean += "Ь"

        return clean

    def generate_table():
        alphabet = "АХБМЦВЧГНШДОЕЩ,ЖУП.ЗЪРИЙСЬКЭТЛЮЯ_ЫФ-"
        table = []
        for char in alphabet:
            if char not in table:
                table.append(char)
        return table

    def encode(plaintext):
        table = generate_table()
        plaintext = prepare_input(plaintext)
        ciphertext = ""

        for char1, char2 in chunker(plaintext, 2):
            row1, col1 = divmod(table.index(char1), 6)
            row2, col2 = divmod(table.index(char2), 6)

            if row1 == row2:
                ciphertext += table[row1 * 6 + (col1 + 1) % 6]
                ciphertext += table[row2 * 6 + (col2 + 1) % 6]
            elif col1 == col2:
                ciphertext += table[((row1 + 1) % 6) * 6 + col1]
                ciphertext += table[((row2 + 1) % 6) * 6 + col2]
            else:  # rectangle
                ciphertext += table[row1 * 6 + col2]
                ciphertext += table[row2 * 6 + col1]

        return ciphertext.lower()

    return encode(plaintext)


def gamma(input_text, keys):
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    f = lambda arg: alphabet[(alphabet.index(arg[0]) + alphabet.index(arg[1])) % mod + 1]
    result = ""

    import re
    from itertools import cycle

    text = re.sub(r'[^\w\s]', '', input_text).split()
    key = keys[0]
    mod = keys[1]

    len_words = [len(word) for word in text]
    one_word_text = "".join(text)
    encrypt_one_word_text = ''.join(map(f, zip(one_word_text, cycle(key))))

    for i in range(len(len_words)):
        result += encrypt_one_word_text[:len_words[i]] + " "
        encrypt_one_word_text = encrypt_one_word_text[len_words[i]:]

    result = result.strip()

    return result


def polybius_square(input_text, key):
    polyb_dict = {"а": "11", "б": "12", "в": "13",
                  "г": "14", "д": "15", "е": "16", "ё": "21",
                  "ж": "22", "з": "23", "и": "24", "й": "25",
                  "к": "26", "л": "31", "м": "32", "н": "33",
                  "о": "34", "п": "35", "р": "36", "с": "41",
                  "т": "42", "у": "43", "ф": "44", "х": "45",
                  "ц": "46", "ч": "51", "ш": "52", "щ": "53",
                  "ъ": "54", "ы": "55", "ь": "56", "э": "61",
                  "ю": "62", "я": "63"}

    result = ""
    list_text = list(input_text)
    for i in input_text:
        if i in polyb_dict:
            result += polyb_dict.get(i)
    return result