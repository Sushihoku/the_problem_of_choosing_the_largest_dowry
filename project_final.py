from math import factorial
from functools import lru_cache
import random, time, secrets



def compute_factorials(n): #Предварительное вычисление факториалов для чисел от 0 до n
        return [factorial(i) for i in range(n + 1)]


@lru_cache
def max_win_probability(skip, total_tickets): #Вычисляет вероятность выигрыша максимального приза при пропуске skip - 1 билетов 
    if skip == 1:
        return 1 / total_tickets  

    probability = 0.0
    for k in range(skip - 1, total_tickets):
        probability += 1 / k
    return probability * (skip - 1) / total_tickets




@lru_cache
def optimal_skip_for_max_probability(total_tickets): #Определяет оптимальное количество пропущенных билетов для максимизации вероятности выигрыша
    for skip in range(1, total_tickets):
        if (skip/total_tickets)> max_win_probability(skip+1,total_tickets):
            return skip
    return 1


@lru_cache
def average_win(skip, total_tickets): #Вычисляет средний выигрыш при пропуске skip - 1 билетов
    factorials = compute_factorials(total_tickets)
    average = 0.0

    if skip == 1: 
        for k in range(1, total_tickets + 1):
            average += k
        return average / total_tickets

    for k in range(skip, total_tickets + 1):
        sum_k = 0.0
        for i in range(skip - 1, k):
            sum_k += factorials[k - 1] * (skip - 1) * factorials[total_tickets - i - 1] / (i * factorials[k - i - 1] * factorials[total_tickets])
        average += k * sum_k

    return average


def optimal_skip_for_max_average(total_tickets): #Определяет оптимальное количество пропущенных билетов для максимизации среднего выигрыша
    total_win = average_win(1,total_tickets)
    for skip in range(1, total_tickets):
        next_win=average_win(skip+1, total_tickets)

        if total_win > next_win:
            return [skip,total_win]
        total_win=next_win
    return [1, average_win(1, total_tickets)]




def print_results_table(max_tickets): #Печатает таблицу с результатами для количества билетов
    print(f"{'n':<8}{'s (вероятность)':<20}{'P(max)':<20}{'s (средний)':<20}{'Средний выигрыш':<20}")
    print("=" * 80)

    for total_tickets in range(1, max_tickets + 1):
        optimal_probability_skip = optimal_skip_for_max_probability(total_tickets)
        probability = max_win_probability(optimal_probability_skip, total_tickets)

        max_average = optimal_skip_for_max_average(total_tickets)

        print(f"{total_tickets:<8}{optimal_probability_skip:<20}{round(probability, 10):<20}{max_average[0]:<20}{round(max_average[1], 10):<20}")



def generate_random_array(n):
    array = list(range(1, n + 1))
    for i in range(n - 1, 0, -1):
        j = secrets.randbelow(i + 1)  # Выбирает случайный индекс от 0 до i
        array[i], array[j] = array[j], array[i]  # Обменивает элементы местами
    return array


def simulation(n, repeat):
    total_wins = 0  # Количество выигрышей максимального приза
    total_average = 0  # Общий средний выигрыш

    # Оптимальные параметры
    optimal_probability_skip = optimal_skip_for_max_probability(n)
    optimal_average_skip = optimal_skip_for_max_average(n)[0]

    print("Оптимальные параметры:")
    print(f"s (для вероятности): {optimal_probability_skip}, P(max): {max_win_probability(optimal_probability_skip, n)}")
    print(f"s (для среднего выигрыша): {optimal_average_skip}, Средний выигрыш: {optimal_skip_for_max_average(n)[1]}")


    array = list(range(1, n + 1))
    for _ in range(repeat):
        #array = generate_random_array(n)
        random.shuffle(array) 

        # Моделирование для среднего выигрыша
        if optimal_average_skip==1:
            total_average+=array[0]
        else:
            last_max_avg = max(array[:optimal_average_skip-1])  # Максимум в пробной серии
            for value in array[optimal_average_skip-1:]:
                if value > last_max_avg:
                    total_average+= value
                    break
        

        # Моделирование для максимального выигрыша
        if optimal_probability_skip==1:
            last_max_prob = 0
        else:
            last_max_prob = max(array[:optimal_probability_skip-1])  # Максимум в пробной серии
        selected_prob = None
        for value in array[optimal_probability_skip-1:]:
            if value > last_max_prob:
                selected_prob = value
                break
        if selected_prob is None:
            selected_prob = array[-1]

        if selected_prob == max(array):
            total_wins += 1

    # Результаты
    win_probability = total_wins / repeat
    average_reward = total_average / repeat

    #print("Результаты моделирования:")
    print(f"Вероятность выигрыша максимального приза: {win_probability}")
    print(f"Средний выигрыш: {average_reward}")


n = int(input("Введите максимальное количество билетов (n): "))    
start_time = time.time()
print_results_table(n)
#print(f"\nn={n}")
simulation(n,10**7)
end_time = time.time()
#print(f"Время выполнения программы: {end_time - start_time:.2f} секунд\n")
