import numpy as np
from math import sqrt, ceil
from PIL import Image, ImageOps
from colormap.colors import hex2rgb


def distance(x, y):
    return np.sqrt(x**2 + y**2)


def distance_matrix(size, center):
    nrows, ncols = size
    row_center, col_center = ceil(nrows * center[0]), ceil(ncols * center[1])
    row, col = np.ogrid[:nrows, :ncols]
    return distance(row - row_center, col - col_center)


def img_radius(img):
    img_array = np.array(img)
    dist_matrix = distance_matrix(img.size, (0.5, 0.5))
    return max(dist_matrix[img_array[:, :, 3] > 0])


def calc_color(from_color, to_color, dist):
    return from_color * (1 - dist) + to_color * dist


def paint_qr(img, gradient_pos, from_color, to_color):

    from_rgb = hex2rgb(from_color)
    to_rgb = hex2rgb(to_color)

    if from_color == '#000000' and from_color == '#000000':
        return img.convert('RGBA')
    elif from_color == to_color:
        return solid(img, from_rgb)
    else:
        return gradient(img, gradient_pos, from_rgb, to_rgb)


def gradient(img, gradient_pos, from_rgb, to_rgb):

    dist_matrix = distance_matrix(img.size, gradient_pos)/(img.size[0] * 0.75)

    grd_arr = np.array(
        Image.new('RGBA', img.size, (255, 255, 255, 255))
    )

    grd_arr[:, :, 0:3] = np.array([calc_color(from_rgb[x], to_rgb[x], dist_matrix) for x in range(3)]).T
    grd_arr[:, :, 3] = 255-np.array(img)

    return Image.fromarray(grd_arr, 'RGBA')


def solid(img, color):

    solid_arr = np.array(
        Image.new('RGBA', img.size, color)
    )

    solid_arr[:, :, 3] = 255-np.array(img)

    return Image.fromarray(solid_arr, 'RGBA')


def make_frame(img, border_width):
    # return ImageOps.expand(img, border=border_width, fill='white')
    return ImageOps.expand(img, border=border_width)
