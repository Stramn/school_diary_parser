import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Загружаем логин и пароль из .env
load_dotenv()
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

# Настройка Chrome через webdriver-manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Открываем сайт
driver.get("https://schools.by/login")

# Даём время странице загрузиться
time.sleep(2)

# Вводим логин и пароль
username_input = driver.find_element(By.ID, "id_username")
password_input = driver.find_element(By.ID, "id_password")

username_input.send_keys(LOGIN)
password_input.send_keys(PASSWORD)

login_submit = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//div[@class="button_wrap"]/input[@type="submit" and @value="Войти" and not(@style="display: None")]'))
)
login_submit.click()

refuse_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "refuse-cookies"))
)

refuse_button.click()

def append_db(subj, mark): # TODO: дописать работу с БД
    pass

def get_grades():
    grades_table = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "db_day"))
    )
    rows = grades_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        mark = row.find_element(By.CLASS_NAME, "mark")
        mark_num = mark.text.strip()
        if mark_num:
            subj = row.find_element(By.CLASS_NAME, "lesson")
            subj_txt = mark.text.strip()
            append_db(subj_txt, mark_num)


driver.quit()
