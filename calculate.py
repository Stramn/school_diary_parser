import json
import os, sys

# Файл с оценками
if getattr(sys, 'frozen', False):  # если запущено как .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MARKS_FILE = os.path.join(BASE_DIR, "marks.json")

# Список предметов, за которые оценка считается за полугодие
half_year_subjects = ["ДП/МП", "Обществов.", "География", "Черчение", "Информ."]

def calculate_average(grades):
    # Считает среднее значение списка оценок
    if not grades:
        return 0
    return sum(grades) / len(grades)

def main():
    with open(MARKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)  # словарь {предмет: [оценки]}

    avgs = []

    print("\033[36mСредние отметки по предметам:\033[0m")
    for subject, grades in data.items():
        if not grades:
            print(f"\033[33m{subject}: нет оценок\033[0m")
            continue

        average = calculate_average(grades)
        grades_count = len(grades)
        if grades_count < 4 and subject not in half_year_subjects:
            # выводим среднюю с двумя знаками после запятой
            print(f"\033[32m{subject}: {average:.2f}\033[0m — \033[33mнеаттестация\033[0m")
        elif grades_count < 6 and subject in half_year_subjects:
            print(f"\033[32m{subject}: {average:.2f}\033[0m — \033[33mнеаттестация\033[0m")
        else:
            print(f"\033[32m{subject}: {average:.2f}\033[0m")
        if subject not in ["ДП/МП", "Физ.к.и.зд."]:
            avgs.append(average)

    print("\033[36mСредняя оценка:\033[0m", round(calculate_average(avgs), 2))

if __name__ == "__main__":
    main()
