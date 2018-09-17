from django.shortcuts import render, HttpResponse


# Create your views here.

def login(request):
    return render(request, 'crawler/login.html')


def get_img_code(request):
    import random
    def get_random_color():
        return (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))

    def get_font_color():
        return (random.randint(10, 150), random.randint(10, 150), random.randint(10, 150))

    from PIL import Image, ImageDraw, ImageFont

    # 方式一：先在磁盘生成图片验证码文件，再读取内容返回给页面
    # img = Image.new('RGB', (155, 33), color=get_random_color())
    # with open('valid_img.png', 'wb') as f:
    #     img.save(f, 'png')
    #
    # with open('valid_img.png', 'rb') as f:
    #     data = f.read()

    # 方式二：直接在内存中生成图片，返回给页面
    from io import BytesIO

    f = BytesIO()
    img = Image.new('RGB', (155, 33), color=get_random_color())
    font = ImageFont.truetype("static/crawler/fonts/Sunnydale.ttf", size=25)
    draw = ImageDraw.Draw(img)

    for var in range(5):
        random_num = str(random.randint(0, 9))
        random_lower_alpha = chr(random.randint(95, 122))
        random_upper_alpha = chr(random.randint(65, 90))
        char = random.choice([random_num, random_lower_alpha, random_upper_alpha])
        draw.text((8 + 30 * var, 8), char, get_font_color(), font=font)

    width = 155
    height = 33

    for i in range(5):
        x1 = random.randint(5, width)
        x2 = random.randint(5, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=get_font_color())

    for i in range(5):
        pass
    img.save(f, 'png')
    data = f.getvalue()
    return HttpResponse(data)
