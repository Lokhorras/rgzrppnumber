from flask import Flask, request, jsonify, render_template
from flasgger import Swagger, swag_from
from flask_cors import CORS

app = Flask(__name__)

# Включаем CORS для всех доменов
CORS(app, resources={r"/*": {"origins": "*"}})

# Отключаем ASCII для правильного отображения русских символов
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Конфигурация Swagger
app.config['SWAGGER'] = {
    'title': 'Phone Contacts API',
    'description': 'API для управления телефонными контактами',
    'uiversion': 3,
    'specs_route': '/docs/'
}
swagger = Swagger(app)

# Хранение данных в словаре
contacts_db = {}
contact_counter = 1

@app.route('/')
def index():
    """Главная страница с веб-интерфейсом"""
    return render_template('index.html')

@app.route('/contacts', methods=['POST', 'OPTIONS'])
@swag_from({
    'tags': ['Contacts'],
    'summary': 'Создание нового контакта',
    'description': 'Создает новый телефонный контакт',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Иван Иванов'},
                    'phone': {'type': 'string', 'example': '+7 (999) 123-45-67'},
                    'email': {'type': 'string', 'example': 'ivan@example.com'}
                },
                'required': ['name', 'phone']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Контакт успешно создан',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'phone': {'type': 'string'},
                    'email': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Неверные данные'
        }
    }
})
def create_contact():
    """Создание нового телефонного контакта"""
    global contact_counter
    
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        return response
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' not in data or 'phone' not in data:
        return jsonify({'error': 'Name and phone are required'}), 400
    
    contact_id = contact_counter
    contact_counter += 1
    
    contacts_db[contact_id] = {
        'id': contact_id,
        'name': data['name'],
        'phone': data['phone'],
        'email': data.get('email', '')
    }
    
    response = jsonify(contacts_db[contact_id])
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 201

@app.route('/contacts/<int:contact_id>', methods=['GET'])
@swag_from({
    'tags': ['Contacts'],
    'summary': 'Получение контакта по ID',
    'description': 'Получает информацию о контакте по его идентификатору',
    'parameters': [
        {
            'name': 'contact_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID контакта'
        }
    ],
    'responses': {
        200: {
            'description': 'Информация о контакте',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'phone': {'type': 'string'},
                    'email': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Контакт не найден'
        }
    }
})
def get_contact(contact_id):
    """Получение контакта по идентификатору"""
    contact = contacts_db.get(contact_id)
    
    if not contact:
        response = jsonify({'error': f'Contact with ID {contact_id} not found'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 404
    
    response = jsonify(contact)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 200

@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Contacts'],
    'summary': 'Удаление контакта',
    'description': 'Удаляет контакт по его идентификатору',
    'parameters': [
        {
            'name': 'contact_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID контакта для удаления'
        }
    ],
    'responses': {
        200: {
            'description': 'Контакт успешно удален',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'deleted_contact': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'phone': {'type': 'string'},
                            'email': {'type': 'string'}
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Контакт не найден'
        }
    }
})
def delete_contact(contact_id):
    """Удаление контакта"""
    if contact_id not in contacts_db:
        response = jsonify({'error': f'Contact with ID {contact_id} not found'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 404
    
    deleted_contact = contacts_db.pop(contact_id)
    
    response = jsonify({
        'message': f'Contact {contact_id} deleted successfully',
        'deleted_contact': deleted_contact
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 200

@app.route('/contacts', methods=['GET'])
@swag_from({
    'tags': ['Contacts'],
    'summary': 'Получение всех контактов',
    'description': 'Получает список всех телефонных контактов',
    'responses': {
        200: {
            'description': 'Список всех контактов',
            'schema': {
                'type': 'object',
                'properties': {
                    'contacts': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'name': {'type': 'string'},
                                'phone': {'type': 'string'},
                                'email': {'type': 'string'}
                            }
                        }
                    },
                    'count': {'type': 'integer'}
                }
            }
        }
    }
})
def get_all_contacts():
    """Получение всех контактов"""
    response = jsonify({
        'contacts': list(contacts_db.values()),
        'count': len(contacts_db)
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 200

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья приложения"""
    response = jsonify({
        'status': 'healthy',
        'contacts_count': len(contacts_db),
        'service': 'Phone Contacts API v1.0'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response, 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)