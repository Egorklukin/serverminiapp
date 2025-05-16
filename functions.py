import requests
from giga_token import giga_token, ver_crt
import json

def get_chat_completion(auth_token, user_message, conversation_history=None):
    """
    Отправляет POST-запрос к API чата для получения ответа от модели GigaChat в рамках диалога.

    Параметры:
    - auth_token (str): Токен для авторизации в API.
    - user_message (str): Сообщение от пользователя, для которого нужно получить ответ.
    - conversation_history (list): История диалога в виде списка сообщений (опционально).

    Возвращает:
    - response (requests.Response): Ответ от API.
    - conversation_history (list): Обновленная история диалога.
    """
    # URL API, к которому мы обращаемся
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # Если история диалога не предоставлена, инициализируем пустым списком
    if conversation_history is None:
        conversation_history = []

    # Добавляем сообщение пользователя в историю диалога
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Подготовка данных запроса в формате JSON
    payload = {
    "model": "GigaChat:latest",
    "messages": [
        {
            "role": "user",
            "content": "что было бы если Александр II не отменил бы крепостное право"
        }
    ],
    "function_call": {
        "name": "search_history"
    },
    "functions": [
        {
            "name": "search_history",
            "description": "Прогноз альтернативного хода истории и поиск информации в Интернете",
            "parameters": {
                "type": "object",
                "properties": {
                    "quotes": {
                        "type": "string",
                        "description": "Цитаты, подходящие к данным событиям"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Рассуждения о вариантах развития событий"
                    },
                    "people": {
                        "type": "string",
                        "description": "Лица, участвовавшие в данных событиях"
                    },
                    "name": {
                        "type": "string",
                        "description": "Названия событий"
                    }
                },
                "required": ["quotes", "reasoning", "people", "name"]
            },
            "examples": [
                {
                    "request": "что было бы если Александр II не отменил бы крепостное право",
                    "params": {
                        "name": "Отмена крепостного права Александром II",
                        "people": "Александр II, крестьяне",
                        "reasoning": "Неотмена крепостного права сделала бы Россию более бедной, нестабильной и ускорила бы её крах. Однако даже в этом сценарии давление снизу рано или поздно привело бы к реформе – но уже через кровь и хаос, а не сверху.",
                        "quotes": "Крепостное право было бомбой замедленного действия. Его сохранение ускорило бы крах монархии, возможно, уже к концу XIX века (гипотетическое мнение, основанное на трудах А. Герцена)"
                    }
                }
            ],
            "returns": {
                "type": "object",
                "properties": {
                    "quotes": {
                        "type": "string",
                        "description": "Цитаты, подходящие к данным событиям"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Рассуждения о вариантах развития событий"
                    },
                    "people": {
                        "type": "string",
                        "description": "Лица, участвовавшие в данных событиях"
                    },
                    "name": {
                        "type": "string",
                        "description": "Названия событий"
                    }
                }
            }
        }
    ]
}

    # Преобразуем данные в строку формата JSON
    payload_json = json.dumps(payload)

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    # Выполнение POST-запроса и возвращение ответа
    try:
        response = requests.post(url, headers=headers, data=payload_json, verify=ver_crt)
        response_data = response.json()
        print(response_data)

        # Добавляем ответ модели в историю диалога
        conversation_history.append({
            "role": "assistant",
            "content": response_data['choices'][0]['message']['content']
        })

        return response, conversation_history
    except requests.RequestException as e:
        # Обработка исключения в случае ошибки запроса
        print(f"Произошла ошибка: {str(e)}")
        return None, conversation_history


conversation_history = []
# Пользователь отправляет следующее сообщение, продолжая диалог
response, conversation_history = get_chat_completion(giga_token, "что было бы если Александр II не отменил бы крепостное право", conversation_history)
if response:
    print(response.json()['choices'][0]['message']['content'])