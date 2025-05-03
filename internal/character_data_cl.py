from PIL import Image
import numpy as np

class CharacterData:
    def __init__(self, char_value, info_pixel):
        self.char_value = char_value
        self.info_pixel_np_raw = info_pixel

        image = Image.fromarray(info_pixel)
        
        resized_image = image.resize( (int(info_pixel.shape[1]/2) , int(info_pixel.shape[0]/2) ))
        self.info_half_pixel_np = np.array(resized_image)

        image = Image.fromarray(info_pixel)
        resized_image = image.resize( (int(info_pixel.shape[1]/4) , int(info_pixel.shape[0]/4) ))
        self.info_quar_pixel_np = np.array(resized_image)

        self.info_pixel_np = self.info_pixel_np_raw.astype(np.int16)
        self.info_half_pixel_np = self.info_half_pixel_np.astype(np.int16)
        self.info_quar_pixel_np = self.info_quar_pixel_np.astype(np.int16)

        self.average_color = np.mean(np.mean(self.info_pixel_np,axis=0),axis=0).astype(np.int16)

