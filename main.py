from flask import Flask, render_template
from markov_text_generator import Translator, MarkovTextGenerator

generator = MarkovTextGenerator()
translator = Translator()
words = translator.convert_to_words('shrek.txt');
generator.add_words(words)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    message = generator.new_message()
    return '<p>' + message + '</p><button hx-post="/generate" hx-swap="outerHTML">New Message</button>'

app.run()