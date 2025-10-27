import json
import os, sys

# Файл с оценками
if getattr(sys, 'frozen', False):  # если запущено как .exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MARKS_FILE = os.path.join(BASE_DIR, "marks.json")

# Список предметов, за которые оценка считается за полугодие
half_year_subjects = ["ДП/МП", "Обществов.", "География", "Черчение"]

def calculate_average(grades):
    # Считает среднее значение списка оценок
    if not grades:
        return 0
    return sum(grades) / len(grades)

def main():
    with open(MARKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)  # словарь {предмет: [оценки]}

    avgs = []


    for subject, grades in data.items():
        if not grades:
            print(f"{subject}: нет оценок")
            continue

        average = calculate_average(grades)
        grades_count = len(grades)

        if grades_count < 4 and subject not in half_year_subjects:
            # выводим среднюю с двумя знаками после запятой
            print(f"{subject}: {average:.2f} — неаттестация")
        elif grades_count < 6 and subject in half_year_subjects:
            print(f"{subject}: {average:.2f} — неаттестация")
        else:
            print(f"{subject}: {average:.2f}")
        if subject not in ["ДП/МП", "Физ.к.и.зд."]:
            avgs.append(average)

    print("Средняя оценка:", round(calculate_average(avgs), 2))

if __name__ == "__main__":
    main()
