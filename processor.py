import json
import numpy as np

# Функция обработки входных данных
def process_input_data(data):
    # Установка флагов заделок
    supports_flag = {"Слева": False, "Справа": False}

    # Проверка значения поля "Support" и установка соответствующих флагов
    if "Support" in data[3]:
        if data[3]["Support"] == "from two sides":
            supports_flag = {"Слева": True, "Справа": True}
        elif data[3]["Support"] == "left":
            supports_flag = {"Слева": True, "Справа": False}
        elif data[3]["Support"] == "right":
            supports_flag = {"Слева": False, "Справа": True}
        else:
            print(f"Неизвестное значение 'Support': {data[3]['Support']}. Устанавливаем заделки по умолчанию.")

    # Обработка узлов
    nodes = []
    current_x = 0.0
    kernel_data = data[0]["Kernel"]
    concentrated_load = data[1]["Concentrated load"]

    for node_id, values in concentrated_load.items():
        nodes.append({
            "X": current_x,
            "Сила": values[1]
        })
        if str(node_id) in kernel_data:
            current_x += kernel_data[str(node_id)][0]

    if len(nodes) < len(kernel_data) + 1:
        nodes.append({"X": current_x, "Сила": 0.0})

    # Обработка стержней
    bars = []
    forces = []
    distributed_load = data[2]["Distributed load"]

    for bar_id, values in kernel_data.items():
        bars.append({
            "Площадь": values[1],
            "Модуль упругости": values[2],
            "Продольная нагрузка": distributed_load.get(bar_id, [None, 0.0])[1]
        })
        forces.append(values[3])

    # Длина стержней
    list_length = [values[0] for values in kernel_data.values()]

    return nodes, bars, forces, supports_flag, list_length


def create_matrix_a(number_of_knots: int, list_length: list, list_width: list, list_young_modulus: list,
                    value_left_sealing: bool, value_right_sealing: bool):

    matrix_a = np.zeros((number_of_knots, number_of_knots))

    for index in range(0, number_of_knots - 2):
        value_1 = list_young_modulus[index] * list_width[index] / list_length[index]
        value_2 = list_young_modulus[index + 1] * list_width[index + 1] / list_length[index + 1]
        value = value_1 + value_2
        position = index + 1
        matrix_a[position, position] = value
        matrix_a[position, position + 1] = matrix_a[position + 1, position] = - value_2

    if value_left_sealing:
        matrix_a[0, 0] = 1
        matrix_a[0, 1] = matrix_a[1, 0] = 0
    else:
        value_0_0 = list_young_modulus[0] * list_width[0] / list_length[0]
        matrix_a[0, 0] = value_0_0
        matrix_a[0, 1] = matrix_a[1, 0] = - value_0_0

    if value_right_sealing:
        matrix_a[number_of_knots - 1, number_of_knots - 1] = 1
        matrix_a[number_of_knots - 2, number_of_knots - 1] = 0
        matrix_a[number_of_knots - 1, number_of_knots - 2] = 0
    else:
        value_end_end = list_young_modulus[-1] * list_width[-1] / list_length[-1]
        matrix_a[number_of_knots - 1, number_of_knots - 1] = value_end_end
    return matrix_a

# Создание вектора B
def create_vector_b(input_number_of_knots: int, list_length: list, list_loads: list, list_of_sosr: list,
                    value_left_sealing: bool, value_right_sealing: bool):

    vector_b = np.zeros((input_number_of_knots, 1))

    for index in range(1, input_number_of_knots - 1):
        length_begin = list_length[index - 1]
        value_distributed_begin = list_loads[index - 1]
        length_end = list_length[index]
        value_distributed_end = list_loads[index]

        value_begin = length_begin * value_distributed_begin / 2
        value_end = length_end * value_distributed_end / 2
        value_concentrated = list_of_sosr[index]
        vector_b[index] = value_concentrated + value_begin + value_end

    if value_left_sealing:
        vector_b[0] = 0
    else:
        length_begin = list_length[0]
        value_load_begin = list_loads[0]
        value_power_begin = list_of_sosr[0]
        vector_b[0] = value_power_begin + value_load_begin * length_begin / 2

    if value_right_sealing:
        vector_b[input_number_of_knots - 1] = 0
    else:
        length_end = list_length[-1]
        value_load_end = list_loads[-1]
        value_power_end = list_of_sosr[-1]
        vector_b[input_number_of_knots - 1] = value_power_end + value_load_end * length_end / 2
    return vector_b

# Вычисление смещения
def calc_delta(input_list_of_length: list, input_list_of_square: list, input_list_of_raspr: list,
               input_list_of_modul: list, input_list_of_sosr: list,
               input_zadelka_l: bool, input_zadelka_r: bool):
    number_of_knots = len(input_list_of_sosr)
    matrix_a = create_matrix_a(number_of_knots, input_list_of_length, input_list_of_square, input_list_of_modul,
                               input_zadelka_l, input_zadelka_r)

    vector_b = create_vector_b(number_of_knots, input_list_of_length, input_list_of_raspr, input_list_of_sosr,
                               input_zadelka_l, input_zadelka_r)

    try:
        matrix_a = np.linalg.inv(matrix_a)
    except:
        np.linalg.lstsq(matrix_a, matrix_a)
    delta = np.dot(matrix_a, vector_b)

    return delta

# Обновленные функции Nx, Ux и Sgx с учетом delta
def nx_equation(input_list_of_length: list, input_list_of_square: list, input_list_of_raspr: list,
                input_list_of_modul: list, input_list_of_sosr: list,
                input_zadelka_l: bool, input_zadelka_r: bool,
                input_rod_number: int = None, input_value_x: float = None):

    delta = calc_delta(input_list_of_length, input_list_of_square, input_list_of_raspr,
                       input_list_of_modul, input_list_of_sosr, input_zadelka_l, input_zadelka_r)
    size_vector_delta = len(delta)
    answer_list = []
    for rod in range(size_vector_delta - 1):

        value_1 = input_list_of_modul[rod] * input_list_of_square[rod] / input_list_of_length[rod]
        value_2 = delta[rod + 1] - delta[rod]
        value_3 = input_list_of_raspr[rod] * input_list_of_length[rod] / 2

        if input_value_x is not None:
            value_4 = 1 - 2 * input_value_x / input_list_of_length[rod]
            value_n = value_1 * value_2 + value_3 * value_4
            value_n = round(value_n[0], 3)

            answer_list.append(value_n)

        else:
            value_4_1 = 1
            value_n_begin = value_1 * value_2 + value_3 * value_4_1
            value_n_begin = round(value_n_begin[0], 3)

            value_4_2 = -1
            value_n_end = value_1 * value_2 + value_3 * value_4_2
            value_n_end = round(value_n_end[0], 3)

            answer_list.append([value_n_begin, value_n_end])

    if input_value_x is not None and input_rod_number is not None:
        return answer_list[input_rod_number - 1]
    else:
        return answer_list

def ux_equation(input_list_of_length: list, input_list_of_square: list, input_list_of_raspr: list,
                input_list_of_modul: list, input_list_of_sosr: list,
                input_zadelka_l: bool, input_zadelka_r: bool,
                input_rod_number: int = None, input_value_x: float = None):

    delta = calc_delta(input_list_of_length, input_list_of_square, input_list_of_raspr,
                       input_list_of_modul, input_list_of_sosr, input_zadelka_l, input_zadelka_r)
    size_vector_delta = len(delta)

    answer_list = []
    for rod in range(size_vector_delta - 1):
        value_2 = delta[rod + 1] - delta[rod]
        value_3 = (input_list_of_raspr[rod] * (input_list_of_length[rod] ** 2)) / (
                2 * input_list_of_modul[rod] * input_list_of_square[rod])

        if input_value_x is not None:
            value_1 = input_value_x / input_list_of_length[rod]
            value_4 = 1 - input_value_x / input_list_of_length[rod]

            value_n = delta[rod] + value_1 * value_2 + value_3 * value_1 * value_4
            value_n = round(value_n[0], 3)

            answer_list.append(value_n)

        else:
            value_1_begin = 0
            value_4_begin = 1

            value_n_begin = delta[rod] + value_1_begin * value_2 + value_3 * value_1_begin * value_4_begin
            value_n_begin = round(value_n_begin[0], 3)

            value_1_end = 1
            value_4_end = 0

            value_n_end = delta[rod] + value_1_end * value_2 + value_3 * value_1_end * value_4_end
            value_n_end = round(value_n_end[0], 3)

            answer_list.append([value_n_begin, value_n_end])

    if input_value_x is not None:
        return answer_list[input_rod_number - 1]
    else:
        return answer_list

def sgx_equation(input_list_of_length: list, input_list_of_square: list, input_list_of_raspr: list,
                 input_list_of_modul: list, input_list_of_sosr: list,
                 input_zadelka_l: bool, input_zadelka_r: bool,
                 input_rod_number: int = None, input_value_x: float = None):

    if input_value_x is not None:
        nx_value = nx_equation(input_list_of_length, input_list_of_square, input_list_of_raspr,
                               input_list_of_modul, input_list_of_sosr, input_zadelka_l, input_zadelka_r,
                               input_rod_number, input_value_x)
        area_value = input_list_of_square[input_rod_number - 1]
        answer_value = nx_value / area_value

        return answer_value

    else:
        nx_list = nx_equation(input_list_of_length, input_list_of_square, input_list_of_raspr, input_list_of_modul,
                              input_list_of_sosr, input_zadelka_l, input_zadelka_r)

        answer_list = []
        for nx_index in range(len(nx_list)):
            nx_list_indexed = nx_list[nx_index]
            width = input_list_of_square[nx_index]
            result_list = [round(value / width, 3) for value in nx_list_indexed]

            answer_list.append(result_list)

        return answer_list

# Функция отображения результатов
import json
import numpy as np

# Весь предыдущий код обработки данных и функций расчета остается без изменений

# Функция расчета и сохранения результатов
def calculate_and_save_results(data):
    # Чтение данных из входного файла
    nodes, bars, forces, supports_flag, list_length = process_input_data(data)

    list_width = [i["Площадь"] for i in bars]
    list_young_modulus = [modulus["Модуль упругости"] for modulus in bars]
    value_left_sealing = supports_flag["Слева"]
    value_right_sealing = supports_flag["Справа"]
    list_loads = [loads["Продольная нагрузка"] for loads in bars]
    list_of_sosr = [sosr["Сила"] for sosr in nodes]

    interval = 0.1  # Интервал расчета
    counter = 0  # Начальный счетчик
    results = []

    # Основные расчеты с учетом интервалов
    while counter <= sum(list_length):
        for rod in range(1, len(list_length) + 1):
            x_start = float(nodes[rod - 1]["X"])
            x_end = float(nodes[rod]["X"])

            if x_start <= counter < x_end or abs(counter - x_end) < 1e-9:
                nx = nx_equation(list_length, list_width, list_loads, list_young_modulus, list_of_sosr,
                                 value_left_sealing, value_right_sealing, rod, abs(counter - x_start))
                ux = ux_equation(list_length, list_width, list_loads, list_young_modulus, list_of_sosr,
                                 value_left_sealing, value_right_sealing, rod, abs(counter - x_start))
                sgx = sgx_equation(list_length, list_width, list_loads, list_young_modulus, list_of_sosr,
                                   value_left_sealing, value_right_sealing, rod, abs(counter - x_start))
                results.append({"X": round(counter, 4), "Nx": round(nx, 4), "Ux": round(ux, 4), "Sgx": round(sgx, 4)})
        counter += interval

    # Добавление узлов для каждого стержня
    for rod in range(1, len(list_length) + 1):
        x_start = float(nodes[rod - 1]["X"])
        x_end = float(nodes[rod]["X"])

        # Узел конца текущего стержня
        nx = nx_equation(list_length, list_width, list_loads, list_young_modulus, list_of_sosr,
                         value_left_sealing, value_right_sealing, rod, abs(x_start - x_end))
        ux = ux_equation(list_length, list_width, list_loads, list_young_modulus, list_of_sosr,
                         value_left_sealing, value_right_sealing, rod, abs(x_start - x_end))
        sgx = sgx_equation(list_length, list_width, list_loads, list_young_modulus, list_of_sosr,
                           value_left_sealing, value_right_sealing, rod, abs(x_start - x_end))
        results.append({"X": round(x_end, 4), "Nx": round(nx, 4), "Ux": round(ux, 4), "Sgx": round(sgx, 4)})

        # Узел начала следующего стержня, если он не последний
        if rod < len(list_length):
            nx = nx_equation(list_length, list_width, list_loads, list_young_modulus, list_of_sosr,
                             value_left_sealing, value_right_sealing, rod + 1, 0)
            ux = ux_equation(list_length, list_width, list_loads, list_young_modulus, list_of_sosr,
                             value_left_sealing, value_right_sealing, rod + 1, 0)
            sgx = sgx_equation(list_length, list_width, list_loads, list_young_modulus, list_of_sosr,
                               value_left_sealing, value_right_sealing, rod + 1, 0)
            results.append({"X": round(x_end, 4), "Nx": round(nx, 4), "Ux": round(ux, 4), "Sgx": round(sgx, 4)})

    # Удаление дубликатов
    unique_results = []
    seen_results = set()

    for res in results:
        key = (res["X"], res["Nx"], res["Ux"], res["Sgx"])
        if key not in seen_results:
            unique_results.append(res)
            seen_results.add(key)

    # Сортировка результатов по X
    unique_results = sorted(unique_results, key=lambda res: res["X"])

    # Сохранение результатов
    output_path = r"C:\Users\agolo\OneDrive\Рабочий стол\САПР\processor\results.json"
    with open(output_path, "w") as outfile:
        json.dump(unique_results, outfile, indent=4)

    print(f"Результаты успешно сохранены в {output_path}")

if __name__ == "__main__":
    # Чтение данных из файла
    try:
        with open(r"C:\Users\agolo\OneDrive\Рабочий стол\САПР\processor\data.json") as file:
            input_data = json.load(file)

        # Передача input_data в calculate_and_save_results
        calculate_and_save_results(input_data)

    except Exception as e:
        print(f"Ошибка при запуске processor.py: {e}")

        nodes, bars, forces, supports_flag, list_length = process_input_data(input_data)

        list_width = [i["Площадь"] for i in bars]
        list_young_modulus = [modulus["Модуль упругости"] for modulus in bars]
        value_left_sealing = supports_flag["Слева"]
        value_right_sealing = supports_flag["Справа"]
        list_loads = [loads["Продольная нагрузка"] for loads in bars]
        list_of_sosr = [sosr["Сила"] for sosr in nodes]

        # Запуск расчета и сохранения
        calculate_and_save_results()

    except Exception as e:
        print(f"Ошибка при запуске processor.py: {e}")

