import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
from pathlib import Path

# === Настройка Chrome с маскировкой ===
options = webdriver.ChromeOptions()

# Имитация обычного браузера
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-logging"])


profile_dir = Path.cwd() / "chrome_profile"
profile_dir.mkdir(parents=True, exist_ok=True)
options.add_argument(f"--user-data-dir={str(profile_dir)}")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Скрытие признаков Selenium в JavaScript
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4]});
        Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru']});
    """
})

driver.get("https://schools.by/login")

def log_in(driver):
    # Загружаем логин и пароль из .env
    load_dotenv()
    LOGIN = os.getenv("LOGIN")
    PASSWORD = os.getenv("PASSWORD")
    time.sleep(random.uniform(2.5, 4.5))
    # Вводим логин и пароль
    username_input = driver.find_element(By.ID, "id_username")
    password_input = driver.find_element(By.ID, "id_password")
    username_input.send_keys(LOGIN)
    time.sleep(random.uniform(0.5, 1.5))
    password_input.send_keys(PASSWORD)
    login_submit = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="button_wrap"]/input[@type="submit" and @value="Войти" and not(@style="display: None")]'))
    )
    time.sleep(random.uniform(0.5, 1.5))
    login_submit.click()
    refuse_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "refuse-cookies"))
    )
    time.sleep(random.uniform(0.5, 1.2))
    refuse_button.click()


results = {
    "Матем.": [],
    "ДП/МП": [],
    "Ист.Бел.вкон.всем.ист": [],
    "Физика": [],
    "Англ.яз.": [],
    "Физ.к.и.зд.": [],
    "Бел.яз.": [],
    "Бел.лит.": [],
    "Химия": [],
    "Биология": [],
    "Рус.яз.": [],
    "Рус.лит.": [],
    "Обществов.": [],
    "География": [],
    "Черчение": []
    }

def get_grades_from_page(driver, results):
    # Находим все дни (все таблицы с расписанием)
    days = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "db_day"))
    )
    
    found = False
    
    for day in days:
        # Для каждого дня находим все строки таблицы
        rows = day.find_elements(By.TAG_NAME, "tr")
        
        for row in rows:
            # Пропускаем строки заголовков
            if row.find_elements(By.TAG_NAME, "th"):
                continue
                
            # Ищем ячейку с оценкой
            mark_cell = row.find_element(By.CLASS_NAME, "mark")
            
            # Ищем оценку внутри mark_box
            mark_box = mark_cell.find_element(By.CLASS_NAME, "mark_box")
            strong_tags = mark_box.find_elements(By.TAG_NAME, "strong")
            
            if strong_tags:
                mark_num = strong_tags[0].text.strip()
                
                # Если нашли оценку, ищем предмет
                if mark_num:
                    lesson_cell = row.find_element(By.CLASS_NAME, "lesson")
                    # Извлекаем текст предмета (убираем номер урока)
                    lesson_text = lesson_cell.text.strip()
                    # Убираем цифру и точку в начале
                    subj_txt = lesson_text.split('.', 1)[1].strip() if '.' in lesson_text else lesson_text
                    # Нормализуем название предмета
                    subj_txt = subj_txt.replace(" ", "")
                    
                    if subj_txt in results:
                        results[subj_txt].append(mark_num)
                        found = True
                        print(f"Найдена оценка: {subj_txt} - {mark_num}")
                    else:
                        print(f"\033[33mНеизвестный предмет: {subj_txt}\033[0m (оценка {mark_num})")
    
    if found:
        return results
    else:
        print("\033[31mОценок не найдено\033[0m")
        return None


def write_json(res):
    filename = "marks.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

time.sleep(2)

if driver.current_url == "https://schools.by/login":
    log_in(driver)

print(get_grades_from_page(driver, results)) # тест

time.sleep(random.uniform(10, 20))

driver.quit()
