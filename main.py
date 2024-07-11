## this code is just for my practce
from PIL import Image
import io



def get_image_size_in_mbs(image: Image,image_format:str) -> float:

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image_format)
    

    img_byte_arr.seek(0)
    size_in_bytes = len(img_byte_arr.getvalue())
    

    size_in_mbs = size_in_bytes / (1024 * 1024)
    
    return size_in_mbs

im=Image.open("eureka.jpg")
img_format = im.format
print("Before Resizing")
print(im.size)
print(get_image_size_in_mbs(im, img_format))

parts=0.95
while get_image_size_in_mbs(im,img_format)>1:
    im=im.resize(  (  int(im.width * parts) ,  int(im.height * parts)     ),Image.LANCZOS)

print("\n\nAfter Resizing")
print(im.size)
print(get_image_size_in_mbs(im, img_format))



