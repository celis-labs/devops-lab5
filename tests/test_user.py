from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'nonexistent@mail.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'Sidor Sidorov',
        'email': 's.s.sidorov@mail.com'
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    # Проверяем, что в ответе вернулся ID (целое число)
    assert isinstance(response.json(), int)

    # Дополнительная проверка: получаем созданного пользователя
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 200
    created_user = get_response.json()
    assert created_user['id'] == response.json()
    assert created_user['name'] == new_user['name']
    assert created_user['email'] == new_user['email']

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    user_with_existing_email = {
        'name': 'Someone Else',
        'email': users[0]['email']  # Используем email существующего пользователя
    }
    response = client.post("/api/v1/user", json=user_with_existing_email)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создаём пользователя для удаления
    new_user = {
        'name': 'User For Deletion',
        'email': 'to.delete@mail.com'
    }
    create_response = client.post("/api/v1/user", json=new_user)
    assert create_response.status_code == 201

    # Удаляем созданного пользователя
    delete_response = client.delete("/api/v1/user", params={'email': new_user['email']})
    assert delete_response.status_code == 204
    assert delete_response.content == b''  # Проверяем, что тело ответа пустое

    # Проверяем, что пользователь действительно удалён
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 404