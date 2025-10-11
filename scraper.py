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
import csv
from pathlib import Path

# === Настройка Chrome с маскировкой ===
options = webdriver.ChromeOptions()

# Имитация обычного браузера
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

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
    grades_table = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "db_day"))
    )
    rows = grades_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        mark_cells = row.find_elements(By.CLASS_NAME, "mark")
        if not mark_cells:
            continue
        # оценка заключена в <strong>, ищем его
        strong_tags = mark_cells[0].find_elements(By.TAG_NAME, "strong")

        if strong_tags:
            mark_num = strong_tags[0].text.strip()
        else:
            mark_num = mark_cells[0].text.strip()

        # если и strong, и text пустые — пропускаем
        if not mark_num:
            continue
        subj = row.find_element(By.CLASS_NAME, "lesson")
        # первые два символа в назве предмета - номер => отсекаем
        subj_txt = subj.text[2:].replace(" ", "").strip()
        if subj_txt in results:
            results[subj_txt].append(mark_num)
        else:
            # что за клоунада с эмодзи в терминале?
            # print(f"⚠️ Неизвестный предмет: {subj_txt} (оценка {mark_num})") 
            print(f"\033[33mНеизвестный предмет: {subj_txt}\033[0m (оценка {mark_num})")
            # так то лучше
        return(results)


def append_csv(res):
    filename = "marks.csv"
    delimiter = ";"

    # Шаг 1. Загружаем старые данные, если файл есть
    existing = {}
    if os.path.exists(filename):
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                subject = row["subject"]
                marks = [m.strip() for m in row["marks"].split(",") if m.strip()]
                existing[subject] = marks

    # Шаг 2. Объединяем старые и новые оценки
    for subject, new_marks in res.items():
        old_marks = existing.get(subject, [])
        combined = old_marks + [m for m in new_marks if m not in old_marks]
        existing[subject] = combined

    # Шаг 3. Перезаписываем файл (создастся, если не существует)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["subject", "marks"], delimiter=delimiter)
        writer.writeheader()
        for subject, marks in existing.items():
            writer.writerow({"subject": subject, "marks": ",".join(marks)})

    print(f"✅ CSV обновлён ({filename})")


time.sleep(random.uniform(10, 20))

driver.quit()
