import csv

DESIRED_MPG=30

def parse_cars_file(file_name):
    with open(file_name, 'r') as file:
        cars = [line.strip().split() for line in file]
    return cars


def parse_epa_csv():
    data = []
    with open('C:/Users/bethe/Downloads/vehicles.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


def find_matching_data(cars, data):
    matches = []
    for car in cars:
        make, model = car[0].split('_', 1)
        year = car[1]
        car_matches = []
        for row in data:
            if row['make'] == make and row['model'] == model and row['year'] == year:
                comb08 = int(row['comb08'])
                if comb08 > DESIRED_MPG:
                    car_matches.append([make, model, year, comb08])
        if car_matches:
            car_matches.sort(key=lambda x: x[3])  # sort by comb08
            matches.append(car_matches[0])  # append the match with lowest comb08
    return matches

def write_to_file(matches):
    with open(f'above90above{DESIRED_MPG}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(matches)


def main():
    cars = parse_cars_file('cars_above_90.txt')
    data = parse_epa_csv()
    matches = find_matching_data(cars, data)
    write_to_file(matches)


if __name__ == "__main__":
    main()
