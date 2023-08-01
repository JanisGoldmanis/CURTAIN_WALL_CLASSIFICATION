def get_point_cloud_array(opening_report):
    # Get point cloud from Opening Report
    point_cloud = ReadOpeningCSVData.read_point_cloud_csv(opening_report)
    print(f'From point cloud read {len(point_cloud)} items')

    sorted_point_cloud = sorted(point_cloud, key=lambda point: Geometry.distance_to_zero(point))

    print(f'From point cloud sorted {len(sorted_point_cloud)} items')
    point_cloud_array = []

    i = 0

    while len(sorted_point_cloud) > 1:
        i += 1000
        current_list = []
        # print(len(sorted_point_cloud))
        while True:
            if len(sorted_point_cloud) == 0:
                break
            if Geometry.distance_to_zero(sorted_point_cloud[0]) < i:
                current_list.append(sorted_point_cloud.pop(0))
            else:
                break
        point_cloud_array.append(current_list)
    point_cloud_array.append([])
    point_cloud_array.append([])

    print('Working...')

    return point_cloud_array