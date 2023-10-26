from PIL import Image
import numpy as np


n_classes = 20
# colour map
label_colours = [(0,0,0)
                # 0=Background
                ,(128,0,0),(255,0,0),(0,85,0),(170,0,51),(255,85,0)
                # 1=Hat,  2=Hair,    3=Glove, 4=Sunglasses, 5=UpperClothes
                ,(0,0,85),(0,119,221),(85,85,0),(0,85,85),(85,51,0)
                # 6=Dress, 7=Coat, 8=Socks, 9=Pants, 10=tosor-skin
                ,(52,86,128),(0,128,0),(0,0,255),(51,170,221),(0,255,255)
                # 11=Scarf, 12=Skirt, 13=Face, 14=LeftArm, 15=RightArm
                ,(85,255,170),(170,255,85),(255,255,0),(255,170,0)]
                # 16=LeftLeg, 17=RightLeg, 18=LeftShoe, 19=RightShoe

label_name = ['Background', 'Hat', 'Hair', 'Glove', 'Sunglasses', 'UpperClothes', 'Dress', 'Coat', 'Socks',
              'Pants', 'tosor-skin','Scarf', 'Skirt', 'Face', 'LeftArm', 'RightArm', 'LeftLeg', 
              'RightLeg', 'LeftShoe', 'RightShoe']

# image mean
IMG_MEAN = np.array((104.00698793,116.66876762,122.67891434), dtype=np.float32)


def decode_labels(mask, num_images=1, num_classes=20):
    """Decode batch of segmentation masks.
    
    Args:
      mask: result of inference after taking argmax.
      num_images: number of images to decode from the batch.
      num_classes: number of classes to predict (including background).
    
    Returns:
      A batch with num_images RGB images of the same size as the input. 
    """
    n, h, w, c = mask.shape
    assert(n >= num_images), 'Batch size %d should be greater or equal than number of images to save %d.' % (n, num_images)
    outputs = np.zeros((num_images, h, w, 3), dtype=np.uint8)

    count_dict={'tosor-skin':0,'UpperClothes':0,'Coat':0,'Dress':0,'LeftArm':0,'RightArm':0}
    var_dict={'skin_ratio':0,'skin_pixel':0,'arm_pixel':0}

    for i in range(num_images):
      img = Image.new('RGB', (len(mask[i, 0]), len(mask[i])))
      pixels = img.load()
      for j_, j in enumerate(mask[i, :, :, 0]):
          for k_, k in enumerate(j):
              if k < num_classes:
                  pixels[k_,j_] = label_colours[k]
                  if label_name[k] in count_dict:
                    count_dict[label_name[k]]=count_dict[label_name[k]]+1
      outputs[i] = np.array(img)
      # print(count_dict)

    skin_pixel = count_dict['tosor-skin']
    all_pixel = count_dict['tosor-skin']+count_dict['UpperClothes']+count_dict['Coat']+count_dict['Dress']
    arm_pixel = count_dict['LeftArm']+ count_dict['RightArm']

    skin_ratio=0
    if all_pixel != 0:

        skin_ratio = (skin_pixel) * 1.0 / (all_pixel)

        print('skin ratio:{} arm_pixel:{}'.format(skin_ratio, arm_pixel))

        if skin_ratio >= 0.35 and arm_pixel > 150:
            flag=0
        else:
            flag=1       
    else:
        flag = 1
    
    var_dict['skin_pixel']=skin_pixel
    var_dict['skin_ratio']=skin_ratio
    var_dict['arm_pixel']=arm_pixel
    
    return outputs,flag,var_dict


def pixel_count_v2(mask):
    """Decode batch of segmentation masks.

    Args:
      mask: result of inference after taking argmax.
      num_images: number of images to decode from the batch.
      num_classes: number of classes to predict (including background).

    Returns:
      A batch with num_images RGB images of the same size as the input.
    """
    nudity_count = 0

    count_dict = {'tosor-skin': 0, 'UpperClothes': 0, 'Coat': 0, 'Dress': 0, 'LeftArm': 0, 'RightArm': 0, 'Face':0}
    count_dict['tosor-skin'] = len(mask[mask == label_name.index('tosor-skin')])
    count_dict['all_pixels'] = len(mask[mask != label_name.index('Background')])
    count_dict['UpperClothes'] = len(mask[mask == label_name.index('UpperClothes')])
    count_dict['Coat'] = len(mask[mask == label_name.index('Coat')])
    count_dict['Dress'] = len(mask[mask == label_name.index('Dress')])
    count_dict['LeftArm'] = len(mask[mask == label_name.index('LeftArm')])
    count_dict['RightArm'] = len(mask[mask == label_name.index('RightArm')])
    count_dict['Face'] = len(mask[mask == label_name.index('Face')])

    # #计算tosor-skin区域的长度和宽度：
    coordinate_tosor_skin = np.argwhere(mask == label_name.index('tosor-skin'))
    if len(coordinate_tosor_skin) != 0:
        coordinate_tosor_skin_bl_y = sorted(coordinate_tosor_skin, key = lambda x: x[0] ,reverse=True)[0][0]
        coordinate_tosor_skin_bl_x = sorted(coordinate_tosor_skin, key = lambda x: x[1], reverse=False)[0][1]
        coordinate_tosor_skin_rt_y = sorted(coordinate_tosor_skin, key = lambda x: x[0] ,reverse=False)[0][0]
        coordinate_tosor_skin_rt_x = sorted(coordinate_tosor_skin, key = lambda x: x[1], reverse=True)[0][1]
        tosor_height = np.abs(coordinate_tosor_skin_rt_y-coordinate_tosor_skin_bl_y)
        tosor_width = np.abs(coordinate_tosor_skin_rt_x-coordinate_tosor_skin_bl_x)
    else:
        tosor_height = 0.
        tosor_width = 0.

    #计算person出现的长度和宽度:
    coordinate_person_pixel = np.argwhere(mask != label_name.index('Background'))
    if len(coordinate_person_pixel) != 0:
        coordinate_person_pixel_bl_y = sorted(coordinate_person_pixel, key = lambda x: x[0] ,reverse=True)[0][0]
        coordinate_person_pixel_bl_x = sorted(coordinate_person_pixel, key = lambda x: x[1], reverse=False)[0][1]
        coordinate_person_pixel_rt_y = sorted(coordinate_person_pixel, key = lambda x: x[0] ,reverse=False)[0][0]
        coordinate_person_pixel_rt_x = sorted(coordinate_person_pixel, key = lambda x: x[1], reverse=True)[0][1]
        person_height = np.abs(coordinate_person_pixel_rt_y-coordinate_person_pixel_bl_y)
        person_width = np.abs(coordinate_person_pixel_rt_x-coordinate_person_pixel_bl_x)
    else:
        person_height = 0.
        person_width = 0.

    #计算tosor占person的ratio（长度和宽度）:

    if len(coordinate_tosor_skin) != 0 and len(coordinate_person_pixel) != 0:
        tosor_height_ratio = float(tosor_height/person_height)
        tosor_width_ratio = float(tosor_width/person_width)
    else:
        tosor_height_ratio = 0
        tosor_width_ratio = 0


    #胸前皮肤占脸的比例
    skin_face_ratio = 0
    skin_pixel = count_dict['tosor-skin']
    face_pixel = count_dict['Face']
    if skin_pixel != 0 and face_pixel != 0:
        skin_face_ratio = (skin_pixel) * 1.0 / (face_pixel)

    skin_pixel = count_dict['tosor-skin']
    all_pixel = count_dict['all_pixels']
    arm_pixel = count_dict['LeftArm'] + count_dict['RightArm']

    # 计算tosor_skin / full_person  and upper_arm pixels / full_person
    if all_pixel != 0 and skin_pixel != 0:
        tosor_partof_fullps = (skin_pixel) * 1.0 / (all_pixel)
        upperarm_partof_fullps = (arm_pixel) * 1.0 / (all_pixel)
    else:
        tosor_partof_fullps = 0
        upperarm_partof_fullps = 0

    if tosor_height_ratio >= 0.31:
        nudity_count += 1
    if tosor_partof_fullps >= 0.14:
        nudity_count += 1
    if tosor_width_ratio >= 0.42:
        nudity_count += 1
    if upperarm_partof_fullps >= 0.05:
        nudity_count += 1

    if nudity_count >= 2:
        flag = 1
    else:
        flag = 0

    return flag

