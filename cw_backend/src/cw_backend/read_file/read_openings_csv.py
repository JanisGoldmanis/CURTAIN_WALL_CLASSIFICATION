import csv


def transform_raw_to_point(data):
    data = data.replace('{', '')
    data = data.replace('}', '')
    data = [round(float(x.rstrip()), 1) for x in data.split(',')]
    point = Geometry.Point(data[0], data[1], data[2])
    return point


def read_point_cloud_csv(file_path):
    # Method will go over each row of csv file.
    # First it looks at guid, if such element has already been created.
    # Second if, necessary it creates new element object and then adds profile to necessary element.
    point_cloud = []

    with open(file_path, encoding='UTF-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')

        # Skip first row (csv header)
        next(reader)

        for row in reader:
            name = row[0]
            raw_coordinate = row[1]
            point = transform_raw_to_point(raw_coordinate)
            point.name = name

            point_cloud.append(point)


    return point_cloud
