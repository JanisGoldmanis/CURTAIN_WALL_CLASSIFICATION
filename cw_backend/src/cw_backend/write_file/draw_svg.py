from ..classes.element_representation import element as element_module

import drawsvg as draw


def add_profile_to_drawing(drawing, profile, level, element_height, x_offset, perimeter_profile=True, border=10, scale=20,
                           profile_shortening=100):
    start = profile.start
    end = profile.end

    if profile.direction == 'V':
        horizontal_shortening = 0
        vertical_shortening = int(profile_shortening / scale)
    elif profile.direction == 'H':
        horizontal_shortening = int(profile_shortening / scale)
        vertical_shortening = 0
    else:
        horizontal_shortening = 0
        vertical_shortening = 0

    x1 = int(start.x / scale) + border + horizontal_shortening + x_offset
    y1 = element_height - int(start.y / scale) + border + level * (element_height + 2 * border) - vertical_shortening

    x2 = int(end.x / scale) + border - horizontal_shortening + x_offset
    y2 = element_height - int(end.y / scale) + border + level * (element_height + 2 * border) + vertical_shortening

    if perimeter_profile:
        stroke = 'black'
    else:
        stroke = 'red'

    drawing.append(draw.Lines(x1, y1, x2, y2,
                              close=False,
                              fill='none',
                              stroke=stroke))


def add_opening_to_drawing(drawing, opening, level, element_height, x_offset, border=10, scale=20, opening_shortening=50):
    shortening = int(opening_shortening / scale)

    origin = opening.origin

    vertical_offset = (element_height + 2 * border) * (level + 1)

    local_x = int(origin.x / scale)
    local_y = int(origin.y / scale)

    local_height = int(opening.height / scale)
    local_width = int(opening.width / scale)

    height = local_height - 2 * shortening
    width = local_width - 2 * shortening

    x1 = local_x + border + shortening + x_offset
    y1 = - local_y - border + shortening + vertical_offset - local_height

    drawing.append(draw.Rectangle(x1, y1, width, height, fill='blue', fill_opacity=0.3))


def add_level_title(drawing, level, element_height, element_width, border, scale, text_size):
    x = element_width / 2 + border
    y = border / 2 + (element_height + 2 * border) * level
    drawing.append(draw.Text(f'Level {level}', text_size, x, y, fill='Black', center=True))


def add_opening_to_openings(opening, openings):
    # Recursion function for method split_openings_in_opening_lists
    level = opening.level
    openings[level].append(opening)
    for child in opening.children:
        add_opening_to_openings(child, openings)


def split_openings_in_opening_lists(element, all_openings):
    # Change data structure from tree to list of lists
    for i in range(len(element.element_planes)):
        plane = element.element_planes[i]
        opening = plane.opening
        plane_openings = all_openings[i]
        add_opening_to_openings(opening, plane_openings)


def draw_element(element, svg_folder):
    """
    Generate SVG file for debugging purposes
    :param element:
    :return:
    """
    border = 10  # Border between images in svg file
    scale = 20

    element_dimensions = element_module.get_element_dimensions(element)

    max_level = element_module.get_element_max_level(element)  # Depth level for opening recursion splitting

    # element_representation data
    height = element_dimensions["HEIGHT"]
    width = element_dimensions["WIDTH"]
    element_height = int(height / scale)
    element_width = int(width / scale)

    # Drawing data
    d_height = element_height + 2 * border
    d_width = element_width + 2 * border

    # Create canvas, only objects within canvas borders will be shown
    d = draw.Drawing(d_width, d_height * (max_level + 1), origin=(0, 0))

    # To make organization easier, openings and their children are changed to different data structure
    openings = []
    for _ in range(len(element.element_planes)):
        plane_array = []
        for _ in range(max_level+1):
            plane_array.append([])
        # plane_openings = [[] for _ in range(max_level)]
        openings.append(plane_array)

    split_openings_in_opening_lists(element, openings)
    x_offsets = [0]
    for i in range(len(element.element_planes)-1):
        x_offsets.append(int(element.element_planes[i].width / scale))

    # Create label above each level image
    for level in range(max_level + 1):
        add_level_title(d, level, element_height, element_width, border, scale, text_size=8)

    for i in range(len(element.element_planes)):
        plane_openings = openings[i]
        x_offset = x_offsets[i]

        # Generate image for each recursion level
        for level in range(max_level+1):
            openings_in_level = plane_openings[level]

            # Used to control so that each profile is being drawn only once
            profiles_added = set()

            for opening in openings_in_level:

                # Add inside red profiles
                for profile in opening.profiles_inside:
                    if profile.guid in profiles_added:
                        print(f'When drawing svg file {profile.guid} is as inside profile in multiple openings. It '
                              f'should not happen')
                    profiles_added.add(profile.guid)
                    perimeter_profile = False
                    add_profile_to_drawing(d, profile, level, element_height, x_offset, perimeter_profile, border, scale)

                # Add perimeter black profiles
                perimeter_profiles = [x for x in [opening.top, opening.right, opening.bottom, opening.left]
                                      if x is not None]
                for profile in perimeter_profiles:
                    perimeter_profile = True
                    if profile.guid not in profiles_added:
                        profiles_added.add(profile.guid)
                        add_profile_to_drawing(d, profile, level, element_height, x_offset, perimeter_profile, border, scale)

                # Add opaque opening rectangle
                add_opening_to_drawing(d, opening, level, element_height, x_offset, border, scale, 75)

    d.set_pixel_scale(2)  # Set number of pixels per geometry unit

    d.save_svg(f'{svg_folder}/{element.delivery_number}.svg')
