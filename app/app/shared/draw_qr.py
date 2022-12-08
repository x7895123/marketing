import qrcode
from PIL import Image
from math import ceil
from .qr_utils import img_radius, distance, paint_qr, make_frame
from pathlib import Path

PROJECT_PATH = Path(__file__).parent


def create_qr(data,
              logo=PROJECT_PATH / 'img/dostyq_back.png',
              gradient_pos=(0.5, 0.5),
              from_color='#0063eb',
              to_color='#392195'):
    qr = qrcode.QRCode(version=7, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    return make_image(qr.modules,
                      logo=logo,
                      gradient_pos=gradient_pos,
                      from_color=from_color,
                      to_color=to_color)


def make_image(modules, logo, from_color, to_color, gradient_pos):
    modules_count = len(modules)
    box_size = 10
    qr_size = modules_count * box_size

    center = ceil(modules_count * 0.5)

    im_logo = Image.open(logo)
    logo_radius_modules = ceil(img_radius(im_logo) / box_size)

    im_eye = Image.open(PROJECT_PATH / 'img/eye_round.tif')
    im_dot = Image.open(PROJECT_PATH / 'img/dot.tif')
    im_dot_square = Image.open(PROJECT_PATH / 'img/dot_square.tif')
    im_dot_left = Image.open(PROJECT_PATH / 'img/dot_left.tif')
    im_dot_right = Image.open(PROJECT_PATH / 'img/dot_right.tif')
    im_dot_up = Image.open(PROJECT_PATH / 'img/dot_up.tif')
    im_dot_down = Image.open(PROJECT_PATH / 'img/dot_down.tif')
    im_dot_top_left = Image.open(PROJECT_PATH / 'img/dot_top_left.tif')
    im_dot_top_right = Image.open(PROJECT_PATH / 'img/dot_top_right.tif')
    im_dot_bot_left = Image.open(PROJECT_PATH / 'img/dot_bot_left.tif')
    im_dot_bot_right = Image.open(PROJECT_PATH / 'img/dot_bot_right.tif')

    img = Image.new("L", (qr_size, qr_size), 255)
    img.paste(im_eye, box=(0, 0))
    img.paste(im_eye, box=(qr_size - 70, 0))
    img.paste(im_eye, box=(0, qr_size - 70))

    if logo:
        for x in range(len(modules)):
            for y in range(len(modules)):

                if (x > center + logo_radius_modules) and (y > center + logo_radius_modules):
                    module_in_logo = distance(center - x, center - y) - logo_radius_modules < 0
                else:
                    module_in_logo = distance(center - x - 1, center - y - 1) - logo_radius_modules < 0

                if module_in_logo:
                    modules[x][y] = False

    for x in range(len(modules)):
        for y in range(len(modules)):

            module_in_eye = (x <= 7 and y <= 7) or \
                            (x <= 7 and y >= modules_count - 7) or \
                            (x >= modules_count - 7 and y <= 7)

            if not module_in_eye and modules[y][x]:

                if y == 0:
                    up = False
                else:
                    up = modules[y - 1][x]

                if x == modules_count - 1:
                    right = False
                else:
                    right = modules[y][x + 1]

                if y == modules_count - 1:
                    down = False
                else:
                    down = modules[y + 1][x]

                if x == 0:
                    left = False
                else:
                    left = modules[y][x - 1]

                neighbors_count = up + right + down + left

                if neighbors_count == 0:
                    img.paste(im_dot, box=(x * box_size, y * box_size))

                if neighbors_count == 1:
                    if up:
                        img.paste(im_dot_down, box=(x * box_size, y * box_size))

                    if right:
                        img.paste(im_dot_left, box=(x * box_size, y * box_size))

                    if down:
                        img.paste(im_dot_up, box=(x * box_size, y * box_size))

                    if left:
                        img.paste(im_dot_right, box=(x * box_size, y * box_size))

                if neighbors_count == 2:
                    if down and right:
                        img.paste(im_dot_top_left, box=(x * box_size, y * box_size))
                    elif down and left:
                        img.paste(im_dot_top_right, box=(x * box_size, y * box_size))
                    elif up and right:
                        img.paste(im_dot_bot_left, box=(x * box_size, y * box_size))
                    elif up and left:
                        img.paste(im_dot_bot_right, box=(x * box_size, y * box_size))
                    else:
                        img.paste(im_dot_square, box=(x * box_size, y * box_size))

                if neighbors_count > 2:
                    img.paste(im_dot_square, box=(x * box_size, y * box_size))

    # qrdir = PROJECT_PATH / 'qr_images/'
    # try:
    #     # Create target Directory
    #     Path.mkdir(qrdir)
    #     # print("Directory ", qrdir, " Created ")
    # except FileExistsError:
    #     pass
    #     # print("Directory ", qrdir, " already exists")
    #
    # img.save(PROJECT_PATH / 'qr_images/L.png')
    img = paint_qr(img, gradient_pos, from_color, to_color)

    img.paste(im_logo,
              box=(int(qr_size / 2 - im_logo.size[0] / 2), int(qr_size / 2 - im_logo.size[1] / 2)),
              mask=im_logo)

    img = make_frame(img, box_size*5)
    return img
