import os, random, imagehash
from PIL import Image

layers_dir = os.listdir('layers')

def nft_count():
    num_layers = len(layers_dir)
    num_var = 1
    for l in layers_dir:
        num_var = num_var * len(os.listdir(os.path.join('layers', l)))
    print(f"Creating {num_var} unique NFT images. Based on {num_layers} layers and a number variations for each.")
    return(num_var)

def create_layer_list(): 
    layers = []  
    for l in layers_dir:
        layer_sub_dir = os.path.join('layers', l)
        rand_var = random.choice(os.listdir(layer_sub_dir))
        layers.append(Image.open(os.path.join(layer_sub_dir, rand_var)))
    return layers

def save_layer_stack(nft_path):
    layers = create_layer_list()
    layer_stack = layers[0]  
    for img in range(0, len(layers)-1):
        next_layer = layers[img + 1]
        layer_stack.paste(next_layer, (0,0), next_layer.convert('RGBA'))
    layer_stack.save(nft_path, 'PNG')

def create_temp_hash(nft_path):
    with Image.open(nft_path) as img:
        temp_hash = str(imagehash.average_hash(img))
    return temp_hash

def check_nfts():
    return(len(os.listdir('nft_images')))
    
def save_final_img():
    hashes = []
    i = 1
    nft_counts = nft_count()
    while check_nfts() < nft_counts:
        nft_path = f'nft_images\\nft_{i}.PNG'
        save_layer_stack(nft_path)

        temp_hash = create_temp_hash(nft_path)

        if temp_hash in hashes:
            os.remove(nft_path)
        else:
            hashes.append(temp_hash)
            i+=1

save_final_img() 