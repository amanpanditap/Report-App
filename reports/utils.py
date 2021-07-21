import base64, uuid
from django.core.files.base import ContentFile

def get_report_image(data):
    f , str_image = data.split(';base64') 
    #print(f)
    # data: image/png
    #print(str_image)
    decoded_img = base64.b64decode(str_image)
    img_name = str(uuid.uuid4())[:10] + '.png'
    data = ContentFile(decoded_img, name=img_name)
    return data