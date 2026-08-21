import os
import sys
import re
import argparse
from datetime import datetime
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

SYSTEM_PROMPT = """
Ты — эксперт по кибербезопасности и анализу вредоносного кода в JavaScript/Userscripts (Tampermonkey).
Твоя задача — провести жесткий аудит безопасности предоставленного кода юзерскрипта.

Проверь код по следующим критическим точкам:
1. Сетевая безопасность: Есть ли скрытые запросы (fetch, XMLHttpRequest, GM_xmlhttpRequest)? Куда они ведут?
2. Кража данных: Ищет ли код cookie, localStorage, sessionStorage, пароли, токены Telegram/соцсетей или данные карт?
3. Обфускация: Используются ли техники скрытия кода (eval, unescape, atob, hex-строки, странные переменные)?
4. Сторонние уязвимости: Подключаются ли сомнительные внешние библиотеки через @require или динамические теги <script>?
5. Скрытая активность: Есть ли признаки майнинга, кликджекинга или скрытых iframe?

Выведи отчет на русском языке в формате Markdown. Обязательно используй заголовки, списки и жирный шрифт для scannability.
Структура отчета:
- Вердикт: (БЕЗОПАСЕН / ПОДОЗРИТЕЛЕН / ОПАСЕН)
- Обнаруженные угрозы/риски: (перечисли по пунктам, если есть)
- Краткий технический разбор: (что делает код на самом деле)
"""

def download_and_save_script(url):
    if "greasyfork.org" in url and not url.endswith(".user.js"):
        url = re.sub(r'(/code)(.*?)$', r'.user.js', url)
    elif "github.com" in url and "/blob/" in url:
        url = url.replace("github.com", "://githubusercontent.com").replace("/blob/", "/")

    print(f"🥭 Скачивание скрипта по ссылке: {url}...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        user_code = response.text

        os.makedirs("scripts", exist_ok=True)

        filename = "downloaded_script.js"
        url_match = re.search(r'([^/]+\.user\.js|[^/]+\.js)$', url)
        if url_match:
            filename = url_match.group(1)
        else:
            name_match = re.search(r'//\s*@name\s+(.+)', user_code)
            if name_match:
                clean_name = re.sub(r'[\\/*?:"<>| ]', '_', name_match.group(1).strip())
                filename = f"{clean_name}.user.js"
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"script_{timestamp}.js"

        download_path = os.path.join("scripts", filename)

        with open(download_path, "w", encoding="utf-8") as f:
            f.write(user_code)
        print(f"❤️ Исходный код успешно сохранен: {download_path}")

        return user_code
    except Exception as e:
        print(f"❌ Ошибка при скачивании скрипта: {e}")
        return None

def analyze_script(user_code):
    if not HF_TOKEN:
        print("❌ Ошибка: Переменная HF_TOKEN не найдена в файле .env.")
        return

    print("😋 Отправка запроса в облако Hugging Face. Пожалуйста, подождите...")

    try:
        client = InferenceClient(api_key=HF_TOKEN)

        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Вот код для анализа:\n\n```javascript\n{user_code}\n```"}
            ],
            max_tokens=1500,
            temperature=0.1
        )

        report_text = ""
        try:
            if hasattr(response, 'choices') and response.choices:
                first_choice = response.choices[0]
                if hasattr(first_choice, 'message'):
                    report_text = first_choice.message.content
                elif isinstance(first_choice, dict) and 'message' in first_choice:
                    report_text = first_choice['message'].get('content', '')
            elif isinstance(response, dict) and 'choices' in response:
                report_text = response['choices'][0]['message']['content']
            else:
                report_text = getattr(response, 'text', str(response))
        except Exception as parse_error:
            print(f"[!] Внутренняя ошибка парсинга ответа: {parse_error}")
            print(f"[!] Сырой ответ сервера для отладки: {response}")
            return

        if not report_text:
            print("❌ Ошибка: Не удалось извлечь текст ответа от ИИ.")
            return

        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = f"reports/report_{timestamp}.md"

        print(f"🥭 Запись отчета в {output_path} и answer.md...")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        with open("answer.md", "w", encoding="utf-8") as f:
            f.write(report_text)

        print(f"❤️ Успешно! Анализ юзерскрипта полностью завершен.")

    except Exception as e:
        print(f"❌ Произошла ошибка при запросе к ИИ: {e}")

def main():
    parser = argparse.ArgumentParser(description="UserScript Analyzer CLI 😋🥭❤️")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", type=str, help="Имя JS-файла внутри папки 'scripts/'")
    group.add_argument("--url", type=str, help="Прямая URL-ссылка на юзерскрипт")

    args = parser.parse_args()
    user_code = ""

    if args.url:
        user_code = download_and_save_script(args.url)
        if not user_code:
            return

    elif args.file:
        file_path = os.path.join("scripts", args.file)
        if not os.path.exists(file_path):
            print(f"❌ Ошибка: Файл '{args.file}' не найден в папке 'scripts/'.")
            return
        print(f"🥭 Чтение файла {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            user_code = f.read()

    else:
        file_path = os.path.join("scripts", "input_script.js")
        if not os.path.exists(file_path):
            os.makedirs("scripts", exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("// Вставьте ваш JS-код сюда для быстрой проверки")
            print(f"⚠️ Создан пустой файл шаблона по пути: {file_path}")
            return

        print(f"🥭 Флаги не переданы. Чтение дефолтного файла: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            user_code = f.read()

    if not user_code.strip() or user_code.startswith("// Вставьте ваш JS-код"):
        print("❌ Ошибка: Исходный код юзерскрипта пуст или не изменен.")
        return

    analyze_script(user_code)

if __name__ == "__main__":
    main()
