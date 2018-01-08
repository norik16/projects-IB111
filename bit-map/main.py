from PIL import Image
import random
from collections import deque
import math
import copy


def random_point(size_x, size_y, padding):
    extra = 2
    return random.randint(padding + extra, size_x - padding - extra), \
           random.randint(padding + extra, size_y - padding - extra)


def make_crater(land_map, center, radius):
    """
        Creates crater as an steepnes increase in map['a']

    :param land_map:
    :param center:
    :param radius:
    :return:
    """
    x0, y0 = center
    steepness = 1.1

    land_map['a'][x0][y0] += -steepness * 2

    for k in range(1, radius):
        land_map['a'][x0 + k][y0 + k] += -steepness
        land_map['a'][x0 - k][y0 + k] += -steepness
        land_map['a'][x0 - k][y0 - k] += -steepness
        land_map['a'][x0 + k][y0 - k] += -steepness

    land_map['a'][x0 - radius][y0] += steepness
    land_map['a'][x0 + radius][y0] += steepness

    for k in range(1, radius):
        land_map['a'][x0 - radius][y0 - k] += steepness
        land_map['a'][x0 + radius][y0 - k] += steepness
        land_map['a'][x0 - radius][y0 + k] += steepness
        land_map['a'][x0 + radius][y0 + k] += steepness

    return land_map


def calculate_v_map(land_map, size_x, size_y):
    """
        Calculate steepness of given point

    :param land_map:
    :param size_x:
    :param size_y:
    :return:
    """
    for y in range(size_y):
        for x in range(1, size_x):
            land_map['v'][x][y] = land_map['v'][x - 1][y] + \
                                  land_map['a'][x - 1][y]

    return land_map


def calculate_s_map(land_map, size_x, size_y):
    """
        Calculate height at given point from steepness

    :param land_map:
    :param size_x:
    :param size_y:
    :return:
    """
    for y in range(size_y):
        for x in range(1, size_x):
            land_map['s'][x][y] = land_map['s'][x - 1][y] + \
                                  land_map['v'][x - 1][y]

    return land_map


def rain_craters(land_map, size_x, size_y, amount):
    """
        Generate given number of craters

    :param land_map:
    :param size_x:
    :param size_y:
    :param amount:
    :return:
    """
    for k in range(amount):
        radius = min(random.randint(2, min(size_x, size_y) // 5),
                     random.randint(2, min(size_x, size_y) // 13))
        center = random_point(size_x, size_y, radius)
        land_map = make_crater(land_map, center, radius)

    return land_map


def create_map(size_x, size_y):
    sub_map = [[0 for x in range(size_x)] for y in range(size_y)]
    # print(sub_map)

    return {'s': copy.deepcopy(sub_map), 'v': copy.deepcopy(sub_map),
            'a': copy.deepcopy(sub_map)}


def get_color(height):
    """

    :param height:
    :return:
    """

    color = (0, 0, 0)
    delimeters = [120, 145]
    if height in [160, 175, 190, 205, 220]:
        color = (0, 0, 0)

    elif height > delimeters[1]:
        ch = ((height - delimeters[1]) / (255 - delimeters[1]))
        color = (270 * ch,
                 210 + 80 * ch,
                 -220 + 510 * ch)

    elif height < delimeters[1] and height > delimeters[0]:
        color = (
        200 + 40 * ((height - delimeters[0]) / (delimeters[1] - delimeters[0])),
        80 + 40 * ((height - delimeters[0]) / (delimeters[1] - delimeters[0])),
        5)

    elif height < delimeters[0]:
        color = (5,
                 120 * ((height) / delimeters[0]),
                 240 * ((height) / delimeters[0]))

    r, g, b = color
    return int(r), int(g), int(b)


def make_a_bitmap(name, size_x, size_y):
    """
        Handles creation
    :param name:
    :param size_x:
    :param size_y:
    :return:
    """
    land_map = create_map(size_x, size_y)

    land_map = rain_craters(land_map, size_x, size_y, 10000)
    #
    land_map = calculate_v_map(land_map, size_x, size_y)
    calculate_s_map(land_map, size_x, size_y)

    img = Image.new('RGB', (size_x, size_y), "black")  # create a black image
    pixels = []  # create the pixel map

    mx = 0
    for x in range(size_x):
        for y in range(size_y):
            # if mx < land_map['s'][x][y]:
            #     print(mx)
            mx = max(mx, land_map['s'][x][y])

    mx = mx / 255

    for x in range(size_x):
        for y in range(size_y):
            color = get_color(land_map['s'][x][y] // mx)
            # print(color)
            pixels.append(color)
            # (int(land_map['s'][x][y] // mx),
            #            int(land_map['s'][x][y] // mx),
            #            int(land_map['s'][x][y] // mx)))
    img.putdata(pixels)

    # print('\naaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n')
    # for layer in land_map['a']:
    #     s = ''
    #     for o in layer:
    #         s += str(o) + '\t'
    #     print(s)
    #
    # print('\nvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\n')
    #
    # for layer in land_map['s']:
    #     s = ''
    #     for o in layer:
    #         s += str(o) + '\t'
    #     print(s)

    img.show()
    img.save(name + ".jpg")
    #
    # for c in [10, 50, 100, 150, 200]:
    #     print(c, get_color(c))


make_a_bitmap("small", 1000, 1000)
