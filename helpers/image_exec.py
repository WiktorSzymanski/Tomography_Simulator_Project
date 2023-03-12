import numpy as np


# def bresenhams_line(start_point, end_point, height, width):
#     x1 = start_point[0]
#     y1 = start_point[1]
#     x2 = end_point[0]
#     y2 = end_point[1]

#     delta_x = x2 - x1
#     delta_y = y2 - y1

#     j = y1

#     e = delta_y - delta_x

#     points = []

#     for i in range(x1, x2):
#         if i >= 0 and i < width and j >= 0 and j < height:
#             points.append((i, j))

#         if (e >= 0):
#             j += 1
#             e -= delta_x

#         e += delta_y

#     return points


def bresenhams_line(start_point, end_point, height, width):
    points = []

    def get_pixel(i, j):
        if i >= 0 and i < width and j >= 0 and j < height:
            return (i, j)
        return None

    x1, y1 = start_point
    x2, y2 = end_point

    rise = y2 - y1
    run = x2 - x1

    if run == 0:
        if y2 < y1:
            y1, y2 = (y2, y1)
        for y in range(y1, y2 + 1):
            pixel = get_pixel(x1, y)

            if (pixel):
                points.append(pixel)
    else:
        m = float(rise) / run
        adjust = 1 if m >= 0 else -1
        offset = 0
        threshold = 0.5

        if m <= 1 and m >= -1:
            delta = abs(m)
            y = y1
            if x2 < x1:
                x1, x2 = (x2, x1)
                y = y2
            for x in range(x1, x2 + 1):
                pixel = get_pixel(x, y)

                if (pixel):
                    points.append(pixel)

                offset += delta
                if offset >= threshold:
                    y += adjust
                    threshold += 1
        else:
            delta = abs(float(run) / rise)
            x = x1
            if y2 < y1:
                y1, y2 = (y2, y1)
                x = x2
            for y in range(y1, y2 + 1):
                pixel = get_pixel(x, y)

                if (pixel):
                    points.append(pixel)

                offset += delta
                if offset >= threshold:
                    x += adjust
                    threshold += 1

    return points
