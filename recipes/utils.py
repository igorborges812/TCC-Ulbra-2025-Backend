from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def resize_image(image_field, size=(400, 300)):
    img = Image.open(image_field)
    img.convert('RGB')
    img.thumbnail(size, Image.ANTIALIAS)

    background = Image.new('RGB', size, (255, 255, 255))
    offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
    background.paste(img, offset)

    buffer = BytesIO()
    background.save(fp=buffer, format='JPEG')
    return ContentFile(buffer.getvalue())
