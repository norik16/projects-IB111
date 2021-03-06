from PIL import Image
import random
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
    for y in range(size_x):
        for x in range(1, size_y):
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
    for y in range(size_x):
        for x in range(1, size_y):
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
        center = random_point(size_y, size_x, radius)
        land_map = make_crater(land_map, center, radius)

    return land_map


def create_map(size_x, size_y):
    sub_map = [[0 for x in range(size_x)] for y in range(size_y)]

    return {'s': copy.deepcopy(sub_map), 'v': copy.deepcopy(sub_map),
            'a': copy.deepcopy(sub_map)}


def get_color(height):
    """

    :param height:
    :return:
    """

    color = (0, 0, 0)
    delimeters = [170, 180]
    if height in [190, 205, 220]:
        color = (0, 0, 0)

    elif height > delimeters[1]:
        ch = ((height - delimeters[1]) / (255 - delimeters[1]))
        color = (260 * ch,
                 210 + 80 * ch,
                 -240 + 510 * ch)

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

def print_map(land_map):
    """
        Print for debugging or explaining the solution
    :param land_map:
    :return:
    """

    print('\naaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n')
    for layer in land_map['a']:
        s = ''
        for o in layer:
            s += str(o) + '\t'
        print(s)

    print('\nvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\n')
    for layer in land_map['v']:
        s = ''
        for o in layer:
            s += str(o) + '\t'
        print(s)

    print('\nssssssssssssssssssssssssssssssssssssssssssss\n')
    for layer in land_map['s']:
        s = ''
        for o in layer:
            s += str(o) + '\t'
        print(s)

def make_a_bitmap(name, size_x, size_y):
    """
        Handles creation
    :param name:
    :param size_x:
    :param size_y:
    :return:
    """
    land_map = create_map(size_x, size_y)

    land_map = rain_craters(land_map, size_x, size_y, 100000)

    land_map = calculate_v_map(land_map, size_x, size_y)
    calculate_s_map(land_map, size_x, size_y)

    img = Image.new('RGB', (size_x, size_y), "black")   # create a black image
    pixels = []                                         # create the pixel map

    mx = 0
    for x in range(size_y):
        for y in range(size_x):
            mx = max(mx, land_map['s'][x][y])

    mx = mx / 255

    for x in range(size_y):
        for y in range(size_x):
            color = get_color(land_map['s'][x][y] // mx)
            pixels.append(color)

    img.putdata(pixels)

    img.show()
    img.save(name + ".jpg")


make_a_bitmap("terrain", 820*2, 312*2)
