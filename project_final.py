from math import factorial, comb
from functools import lru_cache
import random
import time
import secrets
import itertools


# Предварительное вычисление факториалов для чисел от 0 до n
def compute_factorials1(n):
    return [factorial(i) for i in range(n + 1)]


def compute_factorials(n):
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i
    return fact


@lru_cache
# Вычисляет вероятность выигрыша максимального приза при пропуске skip - 1 билетов
def max_win_probability(skip, total_tickets):
    if skip == 1:
        return 1 / total_tickets

    probability = 0.0
    for k in range(skip - 1, total_tickets):
        probability += 1 / k
    return probability * (skip - 1) / total_tickets


@lru_cache
# Определяет оптимальное количество пропущенных билетов для максимизации вероятности выигрыша
def optimal_skip_for_max_probability(total_tickets):
    for skip in range(1, total_tickets):
        if (skip/total_tickets) > max_win_probability(skip+1, total_tickets):
            return skip
    return 1


@lru_cache
# Вычисляет средний выигрыш при пропуске skip - 1 билетов
def average_win(skip, total_tickets):
    factorials = compute_factorials(total_tickets)
    average = 0.0

    if skip == 1:
        for k in range(1, total_tickets + 1):
            average += k
        return average / total_tickets

    for k in range(skip, total_tickets + 1):
        sum_k = 0.0
        for i in range(skip - 1, k):
            sum_k += factorials[k - 1] * (skip - 1) * factorials[total_tickets - i - 1] / (
                i * factorials[k - i - 1] * factorials[total_tickets])
        average += k * sum_k

    return average

# Определяет оптимальное количество пропущенных билетов для максимизации среднего выигрыша


def optimal_skip_for_max_average(total_tickets):
    total_win = average_win(1, total_tickets)
    for skip in range(1, total_tickets):
        next_win = average_win(skip+1, total_tickets)

        if total_win > next_win:
            return [skip, total_win]
        total_win = next_win
    return [1, average_win(1, total_tickets)]


@lru_cache
# вычисляет средний выигрыш при пропуске skip-1 билет по алгоритму со средним
def average_win_med_gpt(skip, total_tickets):
    average = 0.0
    if skip == 1:
        for k in range(1, total_tickets + 1):
            average += k
        return average / total_tickets

    factorials = compute_factorials(total_tickets)
    for avr_n in itertools.combinations(range(1, total_tickets+1), skip-1):
        avr_n = list(avr_n)
        avg_inskip = 0
        mid = sum(avr_n)/(skip-1)
        low = 0
        for k in range(1, total_tickets+1):
            if k not in avr_n:
                if k >= mid:
                    avg_inskip += k
                else:
                    low += 1

        if low != total_tickets-skip+1:
            chanse_drop = 0
            for i in range(low+1):
                total_drop = factorials[total_tickets -
                                        skip-i] / factorials[low-i]
                chanse_drop += total_drop / \
                    factorials[total_tickets-skip+1] * factorials[low]

            avg_inskip *= chanse_drop
            average += avg_inskip

    average *= factorials[skip-1]*factorials[total_tickets -
                                             skip+1]/factorials[total_tickets]
    return average


@lru_cache
def average_win_med_gpt1(skip, total_tickets):
    k = skip - 1
    # всего сочетаний
    total_comb = comb(total_tickets, k)
    total_sum = 0.0

    for S in itertools.combinations(range(1, total_tickets+1), k):
        μ = sum(S)/k if k > 0 else 0.0
        # билеты, которые остались
        remaining = [x for x in range(1, total_tickets+1) if x not in S]
        # допустимые (>= μ)
        H = [x for x in remaining if x >= μ]

        if H:
            # среднее по H
            total_sum += sum(H)/len(H)
        # иначе прибавляем 0

    return total_sum / total_comb


@lru_cache
def optimal_skip_for_max_average_new(total_tickets):
    if total_tickets == 1:
        return [1, average_win_med_gpt(1, 1)]

    start = total_tickets // 2
    best_win = average_win_med_gpt(start, total_tickets)

    # Проверяем соседние значения (если они допустимы)
    win_left = average_win_med_gpt(
        start - 1, total_tickets) if start > 1 else float('-inf')
    win_right = average_win_med_gpt(
        start + 1, total_tickets) if start < total_tickets-1 else float('-inf')

    # Определяем направление поиска
    if win_right > best_win:
        direction = 1
        skip = start + 1
        best_win = win_right
    elif win_left > best_win:
        direction = -1
        skip = start - 1
        best_win = win_left
    else:
        return [start, best_win]  # локальный максимум

    # Односторонний поиск в выбранном направлении
    while 1 <= skip + direction <= total_tickets-1:
        next_skip = skip + direction
        next_win = average_win_med_gpt(next_skip, total_tickets)

        if next_win > best_win:
            skip = next_skip
            best_win = next_win
        else:
            break

    return [skip, best_win]

# Определяет оптимальное количество пропущенных билетов для максимизации среднего выигрыша


def optimal_skip_for_max_average_new_old(total_tickets):
    total_win = average_win_med_gpt(1, total_tickets)
    for skip in range(1, total_tickets):
        next_win = average_win_med_gpt(skip+1, total_tickets)

        if total_win > next_win:
            return [skip, total_win]
        total_win = next_win
    return [1, average_win_med_gpt(1, total_tickets)]


# Печатает таблицу с результатами для количества билетов

def print_results_table(max_tickets):
    print(f"{'n':<8}{'s (вероятность)':<20}{'P(max)':<20}"
          f"{'s (средний)':<20}{'Средний выигрыш':<20}"
          f"{'s (через среднее)':<20}{'Средний выигрыш (через среднее)':<35}")
    print("=" * 135)

    for total_tickets in range(1, max_tickets + 1):
        optimal_probability_skip = optimal_skip_for_max_probability(
            total_tickets)
        probability = max_win_probability(
            optimal_probability_skip, total_tickets)

        max_average = optimal_skip_for_max_average(total_tickets)
        max_average_new = optimal_skip_for_max_average_new(total_tickets)

        print(f"{total_tickets:<8}{optimal_probability_skip:<20}"
              f"{round(probability, 10):<20}{max_average[0]:<20}"
              f"{round(max_average[1], 10):<20}{max_average_new[0]:<20}"
              f"{round(max_average_new[1], 10):<35}")


def generate_random_array(n):
    array = list(range(1, n + 1))
    for i in range(n - 1, 0, -1):
        j = secrets.randbelow(i + 1)  # Выбирает случайный индекс от 0 до i
        array[i], array[j] = array[j], array[i]  # Обменивает элементы местами
    return array


def simulation(n, repeat):
    total_wins = 0  # Количество выигрышей максимального приза
    total_average = 0  # Общий средний выигрыш
    total_average_new = 0  # Общий средний выигрыш через среднее

    # Оптимальные параметры
    optimal_probability_skip = optimal_skip_for_max_probability(n)
    optimal_average_skip = optimal_skip_for_max_average(n)[0]
    optimal_average_skip_avr = optimal_skip_for_max_average_new(n)[0]

    print("Оптимальные параметры:")
    print(f"s (для вероятности): {optimal_probability_skip}, P(max): {
          max_win_probability(optimal_probability_skip, n)}")
    print(f"s (для среднего выигрыша): {optimal_average_skip}, Средний выигрыш: {
          optimal_skip_for_max_average(n)[1]}")
    print(f"s (для среднего выигрыша через среднее): {optimal_average_skip_avr}, Средний выигрыш: {
          optimal_skip_for_max_average_new(n)[1]}")

    array = list(range(1, n + 1))
    for _ in range(repeat):
        # array = generate_random_array(n)
        random.shuffle(array)

        # Моделирование для среднего выигрыша
        if optimal_average_skip == 1:
            total_average += array[0]
        else:
            # Максимум в пробной серии
            last_max_avg = max(array[:optimal_average_skip-1])
            for value in array[optimal_average_skip-1:]:
                if value > last_max_avg:
                    total_average += value
                    break

        # Моделирование для среднего выигрыша через среднее
        if optimal_average_skip_avr == 1:
            total_average_new += array[0]
        else:
            # Среднее арифметическое в пробной серии
            last_avg = sum(array[:optimal_average_skip_avr-1]) / \
                len(array[:optimal_average_skip_avr-1])
            for value in array[optimal_average_skip_avr-1:]:
                if value > last_avg:
                    total_average_new += value
                    break

        # Моделирование для максимального выигрыша
        if optimal_probability_skip == 1:
            last_max_prob = 0
        else:
            # Максимум в пробной серии
            last_max_prob = max(array[:optimal_probability_skip-1])
        selected_prob = None
        for value in array[optimal_probability_skip-1:]:
            if value > last_max_prob:
                selected_prob = value
                break
        if selected_prob is None:
            selected_prob = array[-1]

        if selected_prob == n:
            total_wins += 1

    # Результаты
    win_probability = total_wins / repeat
    average_reward = total_average / repeat
    average_reward_new = total_average_new / repeat

    # print("Результаты моделирования:")
    print(f"Вероятность выигрыша максимального приза: {win_probability}")
    print(f"Средний выигрыш: {average_reward}")
    print(f"Средний выигрыш через среднее: {average_reward_new}")


n = int(input("Введите максимальное количество билетов (n): "))
start_time = time.time()
print_results_table(n)
# print(f"\nn={n}")
# simulation(n, 10**7)
end_time = time.time()
print(f"Время выполнения программы: {end_time - start_time:.2f} секунд\n")
