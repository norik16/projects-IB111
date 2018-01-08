import svgwrite
import math

dwg = svgwrite.Drawing(filename='sierpenskiho.svg')
dwg.viewbox(width=1000, height=1000)

init_edges = 3
next_rotation = 180
next_size = 0.5
max_iter = 5
next_color = -int(510 / max_iter)
# next_spacing = math.sqrt(3)/3
next_spacing = 1.5


# next_spacing = 1.825


def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    angle = angle / 180 * math.pi

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def translate(origin, point, ratio):
    ox, oy = origin
    px, py = point

    qx = (px - ox) * ratio + ox
    qy = (py - oy) * ratio + oy

    return qx, qy


def drawRect(center: (int, int), size: float, rotation: int, color: int):
    if size < 20:
        return

    x, y = center

    rect = dwg.rect((x - size / 2, y - size / 2), (size, size), 0, 0,
                    # fill='none',
                    # stroke='rgb(' + str(min(255, color)) + ', ' + str(min(255, 510 - color)) + ', 0)',
                    fill='rgb(' + str(min(255, color)) + ', ' + str(
                        min(255, 510 - color)) + ', 0)',
                    stroke='none',
                    stroke_width=size / 25)
    rect.rotate(rotation, center)

    dwg.add(rect)

    drawRect(rotate(center, (x - size / 2, y - size / 2), rotation),
             size * next_size, rotation + next_rotation, color + next_color)
    drawRect(rotate(center, (x + size / 2, y - size / 2), rotation),
             size * next_size, rotation + next_rotation, color + next_color)
    drawRect(rotate(center, (x - size / 2, y + size / 2), rotation),
             size * next_size, rotation + next_rotation, color + next_color)
    drawRect(rotate(center, (x + size / 2, y + size / 2), rotation),
             size * next_size, rotation + next_rotation, color + next_color)


def drawPolygon(number_of_edges: int, center: (int, int), size: float,
                rotation: int, color: int, iter: int):
    if iter > max_iter:
        return

    x, y = center

    points = []
    angle = 0

    for i in range(number_of_edges):
        points.append(rotate(center, (x - size / 2, y - size / 2), angle))
        angle += 360 / number_of_edges

    for i in range(number_of_edges):
        points[i] = rotate(center, points[i], rotation)

    polygon = dwg.polygon(points,
                          fill='none',
                          stroke='rgb(' + str(min(255, color)) + ', ' + str(
                              min(255, 510 - color)) + ', 0)',
                          # fill='rgb(' + str(min(255, color)) + ', ' + str(min(255, 510 - color)) + ', 0)',
                          # stroke='none',
                          stroke_width=math.sqrt(size) / 1
                          )

    for i in range(number_of_edges):
        points[i] = translate(center, points[i], next_spacing)

    for point in points:
        drawPolygon(number_of_edges, point, size * next_size,
                    rotation + next_rotation, color + next_color, iter + 1)

    dwg.add(polygon)


# drawRect((500, 500), 400, 30, 230)
drawPolygon(init_edges, (500, 500), 400, 45, 510, 0)

dwg.save()
