import os, sys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import random
import json
from pathlib import Path
import calculate

# Настройка Chrome с маскировкой
options = webdriver.ChromeOptions()

# Имитация обычного браузера
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-logging"])

profile_dir = Path.cwd() / "chrome_profile"
profile_dir.mkdir(parents=True, exist_ok=True)
options.add_argument(f"--user-data-dir={str(profile_dir)}")


def log_in(driver):
    # Загружаем логин и пароль из .env
    load_dotenv(os.path.join(os.getcwd(), "default.env.txt"))
    LOGIN = os.getenv("LOGIN")
    PASSWORD = os.getenv("PASSWORD")
    time.sleep(random.uniform(2.5, 4.5))
    # Вводим логин и пароль
    try:
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_username"))
        )
    except TimeoutException:
        print("\033[31mНе удалось найти поле логина/пароля\033[0m")
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
    "Ист.Бел.вкон.всем.ист.": [],
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
    "Черчение": [],
    "Информ.": []
    }

def get_visible_week(driver):
    try: # получаем активную неделю по стилю и классу
        week_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".db_week:not([style])"))
        )
    except TimeoutException:
        week_element = driver.find_element(By.CLASS_NAME, "db_week")
    return week_element


def get_grades_from_page(driver, results):
    week_element = get_visible_week(driver)
    try:
        date_text = week_element.find_element(By.CLASS_NAME, "db_period").text.strip()
    except NoSuchElementException:
        date_text = "\033[31mНеизвестная дата\033[0m"

    found = False
    days = WebDriverWait(week_element, 10).until(
    lambda w: w.find_elements(By.CLASS_NAME, "db_day") or False
    )
    print(f"\033[35mОбрабатываемая неделя: {date_text}\033[0m")
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
                        found = True
                        if '/' in mark_num:
                            for m in mark_num.split('/'):
                                m = int(m) 
                                results[subj_txt].append(m)
                                print(f"Найдена оценка: {subj_txt} - {m}")
                        else:
                            mark_num = int(mark_num)
                            results[subj_txt].append(mark_num)
                            print(f"Найдена оценка: {subj_txt} - {mark_num}")
                    else:
                        print(f"\033[33mНеизвестный предмет: {subj_txt}\033[0m (оценка {mark_num})")
    
    if found:
        return results
    else:
        print("\033[33mОценок не найдено\033[0m")
        return None


def go_to_prev_page(driver):
    week_element = get_visible_week(driver)
    try:
        prev_button = week_element.find_element(By.CLASS_NAME, "prev")
    except NoSuchElementException:
        print("\033[34mЧетверть собрана\033[0m")
        return False

    old_week = get_visible_week(driver)
    old_week_text = old_week.find_element(By.CLASS_NAME, "db_period").text

    prev_button.click()

    try:
        WebDriverWait(driver, 10).until(
            lambda d: get_visible_week(d).find_element(By.CLASS_NAME, "db_period").text != old_week_text
        )
    except TimeoutException:
        print("\033[31mНеделя не была сменена\033[0m")
        return False

    new_week = get_visible_week(driver)
    new_week_text = new_week.find_element(By.CLASS_NAME, "db_period").text
    print(f"\033[36mПереключились на неделю: {new_week_text}\033[0m")
    return True

def switch_to_previous_quarter(driver):
    try:
        # получаем панель с четвертями
        quarters = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tabs2"))
        )
    except TimeoutException:
        print("\033[31mНе найден HUD смены четверти\033[0m")
        return False

    try:
        # Находим активный элемент и ссылку в нем
        active_link = quarters.find_element(By.CSS_SELECTOR, "li.active > a")
        active_quarter_text = active_link.text.strip()
        active_id = active_link.get_attribute("quarter_id")
        
        print(f"Текущая четверть: {active_quarter_text} (ID: {active_id})")
        
        # Проверяем, нужно ли переключать
        if "2" in active_quarter_text or "4" in active_quarter_text:
            target_id = str(int(active_id) - 1)
            
            # Добавляем try/except для этого поиска
            try:
                target_button = quarters.find_element(
                    By.CSS_SELECTOR, f"a[quarter_id='{target_id}']"
                )
                target_button.click()
                
                # Уменьшаем время ожидания
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, f"li.active a[quarter_id='{target_id}']")
                    )
                )
                
                print(f"\033[32mУспешно переключено на четверть ID {target_id}\033[0m")
                return True
                    
            except (NoSuchElementException, TimeoutException):
                print(f"\033[31mЧетверть ID {target_id} не найдена или не переключилась\033[0m")
                return False
                    
            except ValueError:
                print("\033[31mОшибка: quarter_id не является числом\033[0m")
                return False
        else:
            print("\033[33mНе нужно переключать (не 2-я и не 4-я четверть)\033[0m")
            return False
            
    except NoSuchElementException as e:
        print(f"\033[31mОшибка поиска элемента: {e}\033[0m")
        return False
    except Exception as e:
        print(f"\033[31mНеизвестная ошибка: {e}\033[0m")
        return False

def write_json(res):
    if getattr(sys, 'frozen', False):  # если запущено как .exe
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(BASE_DIR, "marks.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    return res


if __name__ == "__main__":
    # инициализация хрома
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

    time.sleep(2) # время для прогрузки страницы и редиректа на страницу ученика

    # при попытке зайти на страницу логина, если юзер зареган - сайт перенаправляет на личную страницу ученика
    if driver.current_url == "https://schools.by/login":
        log_in(driver)
        time.sleep(2)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "db_week"))
    )
    schedule_container = driver.find_element(By.CLASS_NAME, "db_week")
    driver.execute_script("arguments[0].scrollIntoView(true);", schedule_container)
    time.sleep(0.5)

    for i in range(12):
        get_grades_from_page(driver, results)
        time.sleep(random.uniform(0.5, 1.2))
        if not go_to_prev_page(driver):
            break
        if switch_to_previous_quarter(driver): # TODO: написать отдельную обработку четвертных и получетвертных оценок
            pass
    print("-" * 50)
    write_json(results)
    time.sleep(random.uniform(5, 10))
    driver.quit()
    calculate.main()
    print("\033[32mПрограмма выполнена\033[0m")
    # Окно не закроется пока пользователь не нажмет Enter
    input("\033[35mНажмите Enter для выхода...\033[0m")