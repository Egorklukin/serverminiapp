from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS

from giga_token import ver_crt, giga_token

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Конфигурация GigaChat API
GIGA_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


@app.route('/send_message', methods=['POST'])
def handle_message():
    try:
        data = request.json
        user_message = data.get('message')
        conversation_history = data.get('history', [])

        # Обработка обычного текстового запроса
        response, updated_history = get_chat_completion(
            giga_token,
            user_message,
            conversation_history
        )

        if response and response.status_code == 200:
            response_data = response.json()
            return jsonify({
                'answer': response_data['choices'][0]['message']['content']
            })
        else:
            return jsonify({
                'answer': 'Произошла ошибка при обработке запроса.'
            }), 500
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'answer': 'Произошла ошибка на сервере.'
        }), 500


def get_chat_completion(auth_token, user_message, conversation_history=None):
    """Отправляет запрос к GigaChat API для получения текстового ответа"""
    if conversation_history is None:
        conversation_history = [{
            "role": "system",
            "content": "ты формируешь варианты альтернативного развития события истории России"
        },]

    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    payload = json.dumps({
        "model": "GigaChat",
        "messages": conversation_history,
        "temperature": 1,
        "top_p": 0.1,
        "n": 1,
        "stream": False,
        "repetition_penalty": 1,
        "update_interval": 0,
        "function_call": "auto",
        "functions": [
            {
                "name": "text2image"
            },
            {
                "name": "weather_forecast",
                "description": "Возвращает температуру на заданный период",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Местоположение, например, название города"
                        },
                        "format": {
                            "type": "string",
                            "enum": [
                                "celsius",
                                "fahrenheit"
                            ],
                            "description": "Единицы измерения температуры"
                        },
                        "num_days": {
                            "type": "integer",
                            "description": "Период, для которого нужно вернуть"
                        }
                    },
                    "required": [
                        "location",
                        "format"
                    ]
                }
            }
        ]
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    try:
        response = requests.post(GIGA_API_URL, headers=headers, data=payload, verify=ver_crt)
        response_data = response.json()

        conversation_history.append({
            "role": "assistant",
            "content": response_data['choices'][0]['message']['content']
        })
        print(response.json()['choices'][0]['message']['content'])
        return response, conversation_history
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return None, conversation_history

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)