import os, random, time
from PIL import Image

img_list = []
id_list = []

def create_image_list():   
    layers_dir = os.listdir('layers')
    for l in layers_dir:
        layer_sub_dir = os.path.join('layers', l)
        rand_var = random.choice(os.listdir(layer_sub_dir))
        img_list.append(Image.open(os.path.join(layer_sub_dir, rand_var)))
    return img_list

def save_final_img():
    for i in range(0, 1000):
        img_list = create_image_list()
        img_final = img_list[0]
        for x in range(0, len(img_list)-1):
            next = img_list[x+1]
            img_final.paste(next, (0,0), next.convert('RGBA'))
        
        img_path = f'nft_images\\nft_{i}.PNG'
        img_final.save(img_path, 'PNG')
        time.sleep(0.1)

    nft_images_dir = os.listdir('nft_images')
    for nft in nft_images_dir:
        nft_path = os.path.join('nft_images', nft)
        with open(nft_path, encoding = "Latin-1") as img:
            f = img.read()
            b = bytearray(f, encoding = "Latin-1")
        time.sleep(0.1)
        if b in id_list:
            os.remove(nft_path)
            time.sleep(0.1) 
        else:
            id_list.append(b)

save_final_img()  
