from http.client import responses
import flask
from langchain.chat_models import init_chat_model
from flask import Flask, request, jsonify

#Flask web APP
app = Flask(__name__)

model = init_chat_model(
    model = 'gemma3:1b',
    model_provider = 'ollama'
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    response = model.invoke(data['messages'])
    return jsonify(
        {"message": {"role": "assistant",
        "content": response.content}}
    )

#response = model.invoke("Can i learn python in one year?")
#print(response.text)

if __name__ == '__main__':
    app.run(debug=True, port=5002)