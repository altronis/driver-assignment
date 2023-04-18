import csv
import sys
from collections import defaultdict
import random
import copy


def clean_string(s):
    return s.strip().lower()


# Lmao, I plagiarized this from the internet
def edit_dist(str1, str2):
    m = len(str1)
    n = len(str2)

    # Create a table to store results of subproblems
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]

    # Fill d[][] in bottom up manner
    for i in range(m + 1):
        for j in range(n + 1):

            # If first string is empty, only option is to
            # insert all characters of second string
            if i == 0:
                dp[i][j] = j  # Min. operations = j

            # If second string is empty, only option is to
            # remove all characters of second string
            elif j == 0:
                dp[i][j] = i  # Min. operations = i

            # If last characters are same, ignore last char
            # and recur for remaining string
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]

            # If last character are different, consider all
            # possibilities and find minimum
            else:
                dp[i][j] = 1 + min(dp[i][j - 1],  # Insert
                                   dp[i - 1][j],  # Remove
                                   dp[i - 1][j - 1])  # Replace

    return dp[m][n]


def most_similar_name(all_names, name):
    TYPO_TOLERANCE = 2

    all_names = list(all_names)
    edit_dists = [edit_dist(test_name, name) for test_name in all_names]
    min_dist = 9999
    matched_name = ''

    for i in range(len(all_names)):
        if edit_dists[i] < min_dist:
            matched_name = all_names[i]
            min_dist = edit_dists[i]

    if min_dist > TYPO_TOLERANCE:
        return ''
    return matched_name


def parse_form(form_file):
    drivers = {}
    non_drivers = {}
    all_names = set()
    num_solos = 0

    with open(form_file, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(reader):
            if i == 0:
                continue  # Skip the first row

            name = clean_string(row[1])
            if name in all_names:
                continue  # Skip duplicate name

            is_driver = 'yes' in clean_string(row[3])
            need_ride = 'yes' in clean_string(row[5])

            if not is_driver and not need_ride:
                num_solos += 1
                continue

            all_names.add(name)
            diet_restrictions = row[-2].strip()
            comments = row[-1].strip()

            try:
                seats = int(clean_string(row[4]))
            except:
                seats = 0

            member = {
                'discord': clean_string(row[2]),
                'is_driver': is_driver,
                'seats': seats,
                'need_ride': need_ride,
                'diet_restrictions': diet_restrictions,
                'comments': comments
            }

            if is_driver:
                drivers[name] = member
            elif need_ride:
                non_drivers[name] = member

        return all_names, drivers, non_drivers, num_solos


def parse_restrictions(res_file, all_names):
    together = defaultdict(list)
    separate = defaultdict(list)

    with open(res_file) as f:
        lines = f.readlines()

    for i in range(len(lines) // 2):
        is_together = 'y' in clean_string(lines[i * 2])
        p1, p2 = lines[i * 2 + 1].split(',')
        p1 = clean_string(p1)
        p2 = clean_string(p2)

        p1 = most_similar_name(all_names, p1)
        p2 = most_similar_name(all_names, p2)

        if p1 not in all_names or p2 not in all_names:
            continue

        if is_together:
            together[p1].append(p2)
            together[p2].append(p1)
        else:
            separate[p1].append(p2)
            separate[p2].append(p1)

    return together, separate


def parse_officers(officer_file):
    officers = set()

    with open(officer_file) as f:
        for line in f:
            officers.add(clean_string(line.strip()))

    return officers


def parse_big_instruments(big_file):
    info = {}

    with open(big_file) as f:
        for line in f:
            name, instr = line.strip().split(',')
            name = clean_string(name)
            instr = clean_string(instr)
            info[name] = instr

    return info


def get_cliques_without_drivers(cars, together):
    names = set(cars.keys())
    for driver in cars.keys():
        if driver in together:
            for friend in together[driver]:
                names.add(friend)

    cliques = []

    for name, friends in together.items():
        if name in names:
            continue

        names.add(name)
        if not friends:
            continue

        for friend in friends:
            names.add(friend)

        cliques.append([name] + friends)
    return cliques


def put_in_car(cars, capacities, people, separate):
    # First, we need to check constraints
    enemies = set()
    for person in people:
        for enemy in separate[person]:
            enemies.add(enemy)

    eff_seats = copy.deepcopy(capacities)

    for driver, passengers in cars.items():
        people_in_car = [driver] + passengers
        if enemies.intersection(set(people_in_car)):
            del eff_seats[driver]

    max_seats = max(eff_seats.values())
    drivers_with_max_seats = [driver for driver in eff_seats if eff_seats[driver] == max_seats]
    driver = random.choice(drivers_with_max_seats)

    cars[driver] += people
    capacities[driver] -= len(people)


def groupify(form_file, res_file, officer_file, big_file):
    # Step 1. Parse the csv file
    all_names, drivers, non_drivers, num_solos = parse_form(form_file)
    non_driver_names = set(non_drivers.keys())

    # Step 2. Parse the restrictions file
    together, separate = parse_restrictions(res_file, all_names)

    # Step 3. Form groups
    cars = {}
    capacities = {}
    total_capacity = 0

    for driver, info in drivers.items():
        cars[driver] = []
        capacities[driver] = info['seats']
        total_capacity += info['seats']

    # First, put the people that the drivers need to be with in their car.
    for driver_name in cars:
        companions = together[driver_name]
        cars[driver_name] += companions
        capacities[driver_name] -= len(companions)

        for companion in companions:
            non_driver_names.remove(companion)

    # Then, take care of the groups that want to be together, that excludes drivers.
    cliques = get_cliques_without_drivers(cars, together)
    for clique in cliques:
        put_in_car(cars, capacities, clique, separate)

        for person in clique:
            non_driver_names.remove(person)

    # Now just put everyone in cars, randomly
    for person in non_driver_names:
        put_in_car(cars, capacities, [person], separate)

    # Get officers and big instruments info
    officers = parse_officers(officer_file)
    instr_info = parse_big_instruments(big_file)

    officers_going = set()
    big_instrs_going = {}

    for officer in officers:
        name = most_similar_name(all_names, officer)
        if name:
            officers_going.add(name)

    for big_instr_name in instr_info:
        name = most_similar_name(all_names, big_instr_name)
        if name:
            big_instrs_going[name] = instr_info[big_instr_name]

    # Print in pretty format
    for driver, passengers in cars.items():
        seats = drivers[driver]['seats']
        discord = drivers[driver]['discord']

        if driver in officers_going:
            print('*', end='')
        if driver in big_instrs_going:
            print(f'[{big_instrs_going[driver][:3].upper()}]', end='')
        print(f'{driver} ({seats}) ({discord})')

        for passenger in passengers:
            discord = non_drivers[passenger]['discord']
            print('\t', end='')

            if passenger in officers_going:
                print('*', end='')
            if passenger in big_instrs_going:
                print(f'[{big_instrs_going[passenger][:3].upper()}]', end='')
            print(f'{passenger} ({discord})')

        print()

    # Statistics
    num_drivers = len(drivers)
    num_non_drivers = len(non_drivers)

    print(f'Total number of people who are going: {num_drivers + num_non_drivers + num_solos}')
    print(f'Number of people who are driving others or getting driven: {num_drivers + num_non_drivers}')
    print(f'Number of people who are going by themselves: {num_solos}')
    print(f'Number of drivers: {num_drivers}')
    print(f'Number of empty seats: {total_capacity - num_non_drivers}')


if __name__ == '__main__':
    form_file = 'form.csv'
    res_file = 'restrictions.txt'
    officer_file = 'officers.txt'
    big_file = 'big_instruments.txt'
    groupify(form_file, res_file, officer_file, big_file)
