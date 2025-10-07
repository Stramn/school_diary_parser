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
from pathlib import Path

# Загружаем логин и пароль из .env
load_dotenv()
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

# === [2] Настройка Chrome с маскировкой ===
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

def get_grades_from_page(driver):
    results = []
    grades_table = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "db_day"))
    )
    rows = grades_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        mark_cells = row.find_elements(By.CLASS_NAME, "mark")
        if not mark_cells:
            continue
        mark = row.find_element(By.CLASS_NAME, "mark")
        mark_num = mark.text.strip()
        if mark_num:
            subj = row.find_element(By.CLASS_NAME, "lesson")
            subj_txt = subj.text.strip()
            results.append({"subject": subj_txt, "mark": mark_num})
    print(results) # проверка работоспособности

def append_csv(res): # TODO: дописать работу с CSV
    pass

#print(get_grades_from_page(driver))

time.sleep(random.uniform(10, 20))

driver.quit()
