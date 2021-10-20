import random
import json


class MarkovTextGenerator:

    word_dict = {}

    def __init__(self, phrase_length=1):
        self.phrase_length = phrase_length

    def load_word_set(self, word_set_path, fallback_phrase_length=1):
        try:
            with open(word_set_path, 'r') as file:
                self.phrase_length, self.word_dict = json.load(file)
                self.phrase_length = int(self.phrase_length)

        except (FileNotFoundError, EOFError):
            print('Error reading', word_set_path)
            self.phrase_length = fallback_phrase_length
            self.word_dict = {}

    def save_word_set(self, word_set_path):

        with open(word_set_path, 'w') as file:
            data = (self.phrase_length, self.word_dict)
            json.dump(data, file)

    def add_words(self, words):

        for i in range(len(words) - self.phrase_length):

            found = False

            try:
                for prediction_state in self.word_dict[words[i]]:
                    if prediction_state == words[i + 1]:
                        found = True
                        self.word_dict[words[i]][prediction_state] += 1

                if not found:
                    self.word_dict[words[i]][words[i + 1]] = 1

            except KeyError:
                self.word_dict[words[i]] = {words[i + 1]: 1}

    def compress_word_set(self, word_set_path):
        """Each state needs an array of next states, and an array of probabilities."""

        compressed_word_set = []

        words = list(self.word_dict.keys()) #sorted(self.word_dict, key=self.word_dict.get, reverse=True)

        for word in self.word_dict.keys():

            next_states = self.word_dict[word].keys()

            total = 0
            for state in next_states:
                total += self.word_dict[word][state]

            next_states_probabilities = [self.word_dict[word][state] / total for state in next_states]

            next_states = [words.index(word) for word in next_states]

            compressed_word_set.append((words.index(word), next_states, next_states_probabilities))

        with open(word_set_path, 'w') as file:
            data = (self.phrase_length, words, self.word_dict)
            json.dump(data, file)

    def new_message(self, word_count=50, first_word=''):

        if first_word == '':
            try:
                current_word = random.choice(list(self.word_dict['START']))
            except KeyError:
                current_word = random.choice(list(self.word_dict.keys()))
        else:
            current_word = first_word

        message = current_word.capitalize()

        for i in range(word_count):

            words = []

            if len(self.word_dict[current_word]) == 0:
                current_word = random.choice(list(self.word_dict))

            for prediction_state in self.word_dict[current_word]:
                for _ in range(self.word_dict[current_word][prediction_state]):
                    words.append(prediction_state)

            current_word = random.choice(words)

            if current_word == 'END':
                return message

            message = ' '.join((message, current_word))

        message = ''.join(message.split('\n'))

        return message


class Translator:

    """Converts text sources into words for the message generator"""

    accepted_chars = 'abcdefghijklmnopqrstuvwxyz'

    def convert_to_words(self, filename):

        words = []

        with open(filename) as file:
            for line in file:
                words_in_line = line.split(' ')
                for i, word in enumerate(words_in_line):
                    words_in_line[i] = self.sanitise(word)

                words_in_line.insert(0, 'START')
                words_in_line.append('END')

                for word in words_in_line:
                    if word != '':
                        words.append(word)

        return words

    def sanitise(self, word):

        word = word.encode('ascii', 'ignore')
        word = word.decode('ascii')
        word = word.lower()

        if 'https://' in word:
            return ''

        word = list(word)
        for i in range(len(word) - 1, -1, -1):
            if not word[i] in self.accepted_chars:
                word.pop(i)

        word = ''.join(word)

        return word


'''
def main():

    generator = MarkovTextGenerator()
    translator = Translator()

    words = translator.convert_to_words(''path/to/file.json')

    generator.add_words(words)

    while True:
        print(generator.new_message())
        input()


if __name__ == '__main__':
    main()
'''