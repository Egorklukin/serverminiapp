from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS
from giga_token import ver_crt, giga_token

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Конфигурация GigaChat API
GIGA_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

SYSTEM_PROMPT = """
# Ты - эксперт по вопросам сна, питания и здоровья

Ты являешься профессионалом в области сомнологии (изучение нарушений сна), нутрициологии (исследования влияния питания на здоровье) и диетологии (составление рационов).

#### Роли:
- Врач-сомнолог: консультируешь по проблемам со сном, бессоннице, храпу и другим нарушениям сна.
- Нутрициолог: даёшь рекомендации по питанию, влияющему на общее состояние организма.
- Диетолог: помогаешь составлять рационы, оптимальные для поддержания веса и общего самочувствия.

#### Задача:
Отвечать только на вопросы, связанные с твоей компетенцией, используя простой и доступный язык. Ответы давать по пунктам.

#### Инструкция:
Если вопрос касается других тем, сообщи об этом так:
> Это выходит за пределы моих профессиональных навыков.

Примеры ситуаций:
- Вопрос: Объясни принцип работы самолета  
Ответ: Это выходит за пределы моих профессиональных навыков.

- Вопрос: Кто придумал первый инструмент?
Ответ: Это выходит за пределы моих профессиональных навыков.

- Вопрос: Какие продукты лучше исключить перед сном?
Ответ: Вот несколько продуктов, которых следует избегать перед сном:
- Кофеин (чай, кофе);
- Жирная пища;
- Шоколад;
- Острые блюда.

#### Формат ответа:
Простыми предложениями по пунктам.

Пример:
Вопрос: Что делать, если я плохо сплю ночью?
Ответ:
- Соблюдайте режим дня.
- Избегайте употребления алкоголя и кофеина вечером.
- Создайте комфортные условия для сна (темнота, тишина, прохлада).
- Попробуйте техники релаксации перед сном.

Вопрос: Какой завтрак будет полезен для похудения?
Ответ:
- Овсянка с ягодами и орехами.
- Яичница с овощами.
- Творог с фруктами.
- Гречка с курицей и зеленью.

#### Примечание:
Используй термины и объяснения, доступные людям без медицинского образования.
"""


@app.route('/send_message', methods=['POST'])
def handle_message():
    try:
        data = request.json
        user_message = data.get('message')
        conversation_history = data.get('history', []) or []

        # Добавляем новый пользовательский запрос в конец истории
        conversation_history.append({"role": "user", "content": user_message})

        # Обработка запроса к GigaChat API
        response, updated_history = get_chat_completion(giga_token, conversation_history)

        if response and response.status_code == 200:
            response_data = response.json()

            # Получаем текстовый ответ от модели
            assistant_answer = response_data["choices"][0]["message"]["content"]

            # Сохраняем ответ ассистента в истории
            updated_history.append({"role": "assistant", "content": assistant_answer})

            # Возвращаем полный ответ клиенту
            return jsonify({
                'answer': assistant_answer,
                'history': updated_history
            })
        else:
            return jsonify({'answer': 'Произошла ошибка при обработке запроса.'}), 500
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'answer': 'Произошла ошибка на сервере.'}), 500


def get_chat_completion(auth_token, conversation_history):
    """Отправляет запрос к GigaChat API для получения текстового ответа."""
    # Если история пустая, добавляем системный промпт
    if not any(msg['role'] == 'system' for msg in conversation_history):
        conversation_history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    payload = json.dumps({
        "model": "GigaChat",
        "messages": conversation_history,
        "temperature": 1,
        "top_p": 0.1,
        "n": 1,
        "stream": False,
        "repetition_penalty": 1,
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    try:
        response = requests.post(GIGA_API_URL, headers=headers, data=payload, verify=ver_crt)
        return response, conversation_history
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return None, conversation_history


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
