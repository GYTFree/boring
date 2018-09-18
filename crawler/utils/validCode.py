import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def get_random_color():
    return (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))


def get_font_color():
    return (random.randint(10, 150), random.randint(10, 150), random.randint(10, 150))


def get_img_code(request):
    f = BytesIO()
    img = Image.new('RGB', (155, 33), color=get_random_color())
    font = ImageFont.truetype("static/crawler/fonts/Sunnydale.ttf", size=25)
    draw = ImageDraw.Draw(img)

    valid_code = ''
    for var in range(5):
        random_num = str(random.randint(0, 9))
        random_lower_alpha = chr(random.randint(95, 122))
        random_upper_alpha = chr(random.randint(65, 90))
        char = random.choice([random_num, random_lower_alpha, random_upper_alpha])
        draw.text((8 + 30 * var, 8), char, get_font_color(), font=font)
        valid_code += char
    request.session['valid_code'] = valid_code
    width = 155
    height = 33

    for i in range(3):
        x1 = random.randint(5, 10)
        x2 = random.randint(100, width)
        y1 = random.randint(5, 30)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_font_color())

    img.save(f, 'png')
    data = f.getvalue()
    return data
