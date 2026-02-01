import requests
import json
import time
from config import GIGACHAT_CREDENTIALS, GIGACHAT_SCOPE, SYSTEM_PROMPT

class GigaChatAPI:
    def __init__(self):
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.access_token = None
        self.token_expires = 0
        
    def _get_auth_headers(self):
        """Заголовки для аутентификации"""
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(int(time.time())),  # Уникальный ID на основе времени
            'Authorization': f'Basic {GIGACHAT_CREDENTIALS}'
        }
    
    def _get_api_headers(self):
        """Заголовки для API запросов"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
    
    def _auth(self):
        """Аутентификация в GigaChat API"""
        print("Прохожу аутентификацию в GigaChat...")
        
        data = {'scope': GIGACHAT_SCOPE}
        
        try:
            response = requests.post(
                self.auth_url,
                headers=self._get_auth_headers(),
                data=data,
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                # Токен обычно живет 30 минут, ставим 25 для запаса
                self.token_expires = time.time() + 1500
                print("Аутентификация успешна!")
                return True
            else:
                print(f"Ошибка аутентификации: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Исключение при аутентификации: {e}")
            return False
    
    def _check_token(self):
        """Проверка и обновление токена при необходимости"""
        if not self.access_token or time.time() > self.token_expires:
            return self._auth()
        return True
    
    def get_response(self, user_message: str) -> str:
        """Получение ответа от GigaChat"""
        if not self._check_token():
            return "Не могу авторизоваться в GigaChat... Опять эти техники балбесы! 🔧"
        
        # Обрезаем слишком длинные сообщения
        if len(user_message) > 1000:
            user_message = user_message[:1000] + "..."
        
        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.85,
            "max_tokens": 400,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self._get_api_headers(),
                json=payload,
                verify=False,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"Ошибка API: {response.status_code}")
                return "Сервер GigaChat опять глючит... Как и твои вопросы! 🐛"
            
        except requests.exceptions.Timeout:
            return "Долго думаю... Наверное, слишком сложный для тебя вопрос задал! ⏳"
        except Exception as e:
            print(f"Ошибка: {e}")
            return "У меня в голове что-то замкнуло... Наверное, из-за твоего глупого вопроса! ⚡"
