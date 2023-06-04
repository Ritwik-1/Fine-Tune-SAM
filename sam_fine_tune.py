# -*- coding: utf-8 -*-
"""SAM_fine_tune.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AQCnpR2bU0bczVM_OsVR0Gi0k7qyOOtd
"""

pip install git+https://github.com/facebookresearch/segment-anything.git

"""**GPU Device**

PROBLEM : 1) GPU and System RAM crash
             How many tensors to the GPU?
          2) Dataset as well
"""

import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

"""# TPU Device"""

!pip install cloud-tpu-client==0.10 torch==2.0.0 torchvision==0.15.1 https://storage.googleapis.com/tpu-pytorch/wheels/colab/torch_xla-2.0-cp310-cp310-linux_x86_64.whl

import torch
# imports the torch_xla package
import torch_xla
import torch_xla.core.xla_model as xm

device = xm.xla_device()

"""# FINE TUNE APPROACH 1 """

from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

model_checkpoint = "/content/drive/MyDrive/Colab Notebooks/assets/sam_vit_h_4b8939.pth"
model_type = "vit_h"
sam = sam_model_registry[model_type](checkpoint = model_checkpoint)

"""**FREEZING ALL IMAGE ENCODER PARAMS**"""

print(type(sam))

# Freezed all the Image encoder parameters 
for param in sam.image_encoder.parameters():
    param.requires_grad = False

"""PARAMS IN PROMPT ENCODER"""

# IDEA : FREEZE THE POINT AND TEXT PROMPTS 
# BUT WHOLE MODULE HAS SUCH LESS PARAMS 

prompt_params = 0

for name,param in sam.prompt_encoder.named_parameters():
    # print(name)
    # print(param)
    prompt_params += param.numel()

print(prompt_params)

# Bas 6220?

"""PARAMS IN IMAGE ENCODER"""

image_params = 0

for name,param in sam.image_encoder.named_parameters():
    # print(name)
    # print(param)
    image_params += param.numel()

print(image_params)

"""PARAMS IN MASK DECODER"""

mask_params = 0

for name,param in sam.mask_decoder.named_parameters():
    # print(name)
    # print(param)
    mask_params += param.numel()

print(mask_params)

trainable_params = 0
non_trainable_params = 0

# parameters are tensors , for getting actual no. of parameters we need to 
# count the no. of elements in each tensor 
# which is done using numel() function

for i in sam.parameters():
    if(i.requires_grad == False):
        # print(name)
        non_trainable_params+=i.numel()
    else:
        trainable_params+=i.numel()

print("Trainable params : ",trainable_params)
print("Non-trainable params : ",non_trainable_params)

"""**TO ADD MORE MLP LAYERS TO THE MASK DECODER**"""

# for name,param in sam.mask_decoder.named_parameters():
#     print(name)

for name,param in sam.mask_decoder.named_parameters():
  #  if(name == 'MLP'):
      print(name)

for name in sam.mask_decoder.children():
  #  if(name == 'MLP'):
      print(name)

for i in range(4):
  for j in range(3):
     print(sam.mask_decoder.output_hypernetworks_mlps[i].layers[j].weight.shape)
     print(sam.mask_decoder.output_hypernetworks_mlps[i].layers[j].bias.shape)
     print("lol")

# Adding another MLP to the IoU prediction 

# DO NOT RUN AGAIN

import torch.nn as nn

additional_layer2 = nn.Linear(in_features=256, out_features=256,bias = True)

sam.mask_decoder.iou_prediction_head.layers.insert(1,additional_layer2)

for name in sam.mask_decoder.children():
      print(name)

# Checking dimensions again :
for i in range(4):
     print(sam.mask_decoder.iou_prediction_head.layers[i].weight.shape)
     print(sam.mask_decoder.iou_prediction_head.layers[i].bias.shape)
     print("lol")

# ADDING MLPs to THE OUTPUT_HYPERNETWORKS MLP MODULE

# DO NOT RUN AGAIN 

module = sam.mask_decoder.output_hypernetworks_mlps

for i in range(4):
    lin_layer = nn.Linear(in_features=256, out_features=256,bias = True)
    module[i].layers.insert(1,lin_layer)

print(module)

for name in sam.mask_decoder.children():
      print(name)

for i in range(4):
  for j in range(4):
     if(j == 2):
      print("This is added layer")
     print(sam.mask_decoder.output_hypernetworks_mlps[i].layers[j].weight.shape)
     print(sam.mask_decoder.output_hypernetworks_mlps[i].layers[j].bias.shape)

# SAVING THE MODEL IN THIS CONFIGURATION

# i.e 1) Image encoder is freezed 
    # 2) added 1 more MLP layer to the final output predictions

  # for now

  # Now moving to training

import torch

torch.save(sam,'/content/drive/MyDrive/SAM_FT1/sam.pt')

# torch.save(sam.state_dict(), '/content/drive/MyDrive/SAM_FT1/sam.pth')

"""# START RUNNING HERE

"""

# Loading the model
import torch
sam_loaded = torch.load('/content/drive/MyDrive/SAM_FT1/sam.pt')
sam_loaded.to(device)

from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

model_checkpoint = "/content/drive/MyDrive/Colab Notebooks/assets/sam_vit_h_4b8939.pth"
model_type = "vit_h"
sam_original = sam_model_registry[model_type](checkpoint = model_checkpoint)
sam_original.to(device)

import torch 
from segment_anything import SamPredictor

predictor_loaded = SamPredictor(sam_loaded)

# predictor_original = SamPredictor(sam_original)

"""# PYDICOM INSTALL"""

from google.colab.patches import cv2_imshow
from scipy.ndimage import zoom

pip install pydicom

"""# RUNNING ON ONLY 1 EXAMPLE

**Trying to run on 1 image/label first**
"""

import cv2
import pydicom
import matplotlib.pyplot as plt

# First patient ki 35th slice of CT
test_image = "/content/drive/MyDrive/manifest-1680809675630/Adrenal-ACC-Ki67-Seg/Adrenal_Ki67_Seg_001/08-22-2000-NA-CT ABDOMEN-56266/2.000000-Pre Abd 5.0 B40f-18492/1-35.dcm"

# Taking the 35th segmentation from this
label_seg = "/content/drive/MyDrive/manifest-1680809675630/Adrenal-ACC-Ki67-Seg/Adrenal_Ki67_Seg_001/08-22-2000-NA-CT ABDOMEN-56266/300.000000-Segmentation-33545/1-1.dcm"


dicom_image = pydicom.dcmread(test_image)
pixel_data = dicom_image.pixel_array


plt.imshow(pixel_data, cmap='gray')
plt.axis('off')  
plt.show()

dicom_image_labels = pydicom.dcmread(label_seg)
pixel_data_labels = dicom_image_labels.pixel_array

plt.imshow(pixel_data_labels[35], cmap='gray')
plt.axis('off') 
plt.show()

print(type(pixel_data_labels))
print(pixel_data_labels.shape)
print(pixel_data_labels[35].shape)

"""**SEEING SHAPES OF BOTH THE IMAGES**"""

test_CT_image = pixel_data
label_CT_seg = pixel_data_labels[35]

print(test_CT_image.shape)
print(label_CT_seg.shape)

"""**GETTING THE BOUNDING BOX OF THE SEG
IN THE 512x512 plane**
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

threshold = 0  # Choose an appropriate threshold value
binary_mask = (label_CT_seg > threshold).astype(np.uint8)

# Find contours of the binary mask
contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Create a blank 512x512 plane
plane = np.zeros((512, 512), dtype=np.uint8)

# Iterate over the contours and compute the bounding box coordinates
bounding_boxes = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    bounding_boxes.append((x, y, x + w, y + h))
    
    # Plot the bounding box on the plane
    cv2.rectangle(plane, (x, y), (x + w, y + h), (255, 255, 255), 1)

# Plot the plane with bounding boxes
plt.imshow(plane, cmap='gray')
plt.axis('off')
plt.show()


print(bounding_boxes)

# Now have the box , image , can produce the mask and also have the label can calc loss

import cv2
import numpy as np

image_jpg = cv2.cvtColor(test_CT_image, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR (OpenCV default format)
cv2.imwrite('image.jpg', image_jpg)  # Save the JPEG image

# Read JPEG image and convert it back to NumPy array
image_loaded = cv2.imread('image.jpg')  # Read the JPEG image
image_np_loaded = cv2.cvtColor(image_loaded, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

test_CT_image = image_np_loaded

print(type(test_CT_image))
print(test_CT_image.shape)
print(test_CT_image.dtype)

predictor_loaded.set_image(test_CT_image)

def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)
    return mask_image

input_box = np.array(bounding_boxes[0])

masks, _, _ = predictor_original.predict(
    point_coords=None,
    point_labels=None,
    box=input_box[None, :],
    multimask_output=False,
)

print(type(masks))

print(masks[0])

print(masks[0].shape)

mask_image = show_mask(masks[0], plt.gca())

print("---------------------------------------")
print(mask_image)
print(mask_image.shape)
ax = plt.gca()
ax.imshow(masks[0])

# now loss is between masks[0] and pixel_data_labels[35]

# CONVERSION TO FLOAT32 AND CONVERTING TRUE TO 0 and 1s 

mask_int = masks[0].astype(int)
mask_float = masks[0].astype("float32")

pixel_data_labels_float = pixel_data_labels[35].astype("float32")

print(mask_float)
print(pixel_data_labels_float)

print(mask_float.shape)
print(pixel_data_labels_float.shape)

# loss calculation between mask and this output dekhna padega 
import torch.nn.functional as F
import torch

t1 = torch.from_numpy(mask_float)                    # output
t2 = torch.from_numpy(pixel_data_labels_float)         # label

print(t1.shape)
print(t2.shape)


intersection = (t1 * t2).sum().item()
union = t1.sum().item() + t2.sum().item()

dice_coefficient = (2.0 * intersection) / (union + 1e-8)  # Adding a small constant to avoid division by zero

print(dice_coefficient)

"""# START OF FULL DATASET CREATION

POINTS FOR FULL DATASET 

-> Train_set_X 
   images = a vector 
   first 120 = patient 1 
   next 120 = patient 2
   and so on
   image ko dicom se jpg
   mai karna hai and then to 
   numpy array 

-> bounding_boxes = a vector
   bb[i] is bb for images[i]
   how to calculate , make a
   function image jayegi and
   BB return karegi and then 
   append bb[0] to array

-> labels = a vector
   labels[i] correspond to label
   for images[i]
   512x512 ka seg mask directly daaldo
   after convert to float32

-> NOW TRAINING,
   output of SAM is a mask 
   Take mask[0] then it is 512x512
   convert to float32
   and then compare that with label
   loss = loss_fn(output,label) 
    
   ese training loop done 

  -> OUTPUT OF SAM IS A MASK WITH TRUE AND FALSE
     WE HAVE TO CONVERT IT TO 0 and 1 and also 
     to float32 for the dice_loss to work
"""

import pydicom
import numpy as np
import cv2
import matplotlib.pyplot as plt

# label_CT_seg is the 512x512 seg map tensor for the tumour

def getBoundingBox(label_CT_seg):
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt
    threshold = 0  # Choose an appropriate threshold value
    binary_mask = (label_CT_seg > threshold).astype(np.uint8)

    # Find contours of the binary mask
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a blank 512x512 plane
    # plane = np.zeros((512, 512), dtype=np.uint8)

    plane = np.zeros((64, 64), dtype=np.uint8)

    # Iterate over the contours and compute the bounding box coordinates
    bounding_boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        bounding_boxes.append((x, y, x + w, y + h))
        
        # Plot the bounding box on the plane
        cv2.rectangle(plane, (x, y), (x + w, y + h), (255, 255, 255), 1)

    return bounding_boxes[0]
    # # Plot the plane with bounding boxes
    # plt.imshow(plane, cmap='gray')
    # plt.axis('off')
    # plt.show()

# # Load the DICOM file
# dcm = pydicom.dcmread("/content/drive/MyDrive/Colab Notebooks/assets/Patient-1-seg.dcm")

# # Extract the pixel data
# pixel_array = dcm.pixel_array

# print(pixel_array.shape)

# p = pixel_array[28]  # Extract the first channel

# print(p.shape)

# normalized_array = ((p - np.min(p)) / np.ptp(p) * 255).astype(np.uint8)
# bgr_image = cv2.cvtColor(normalized_array, cv2.COLOR_GRAY2BGR)

# cv2_imshow(bgr_image)
# # Normalize the pixel values
# # normalized_array = ((pixel_array - np.min(pixel_array)) / np.ptp(pixel_array) * 255).astype(np.uint8)

# # # Convert to BGR format (assuming the segmentation map is grayscale)
# # bgr_image = cv2.cvtColor(normalized_array, cv2.COLOR_GRAY2BGR)

# import pydicom

# # Load the DICOM image
# # dcm = pydicom.dcmread("/content/drive/MyDrive/Colab Notebooks/assets/1-25.dcm")

# dcm_2 = pydicom.dcmread("/content/drive/MyDrive/manifest-1680809675630/Adrenal-ACC-Ki67-Seg/Adrenal_Ki67_Seg_039/02-08-2010-NA-CT Abdomen-18373/300.000000-Segmentation-78069/1-1.dcm")
# # Get the pixel data
# # pixels = dcm.pixel_array
# p = dcm_2.pixel_array

# print(p.shape)
# print(pixels.shape)

# # Display the image using matplotlib
# plt.imshow(pixels, cmap=plt.cm.gray)
# plt.imshow(p[36], cmap='jet', alpha=0.05) # interpolation='none'
# plt.show()

"""**COLORECTAL CANCER DATASET LOADING**

HERE PROBLEM IS PATIENT 1 HAS MORE SEG MAPS THAN CT SLICES
"""

# SEGMENTATION FILE FOR PATIENT 1 WHO HAS 161 slices of CT but 439 segmentations ????????????

dcm = pydicom.dcmread("/content/drive/MyDrive/manifest-1669817128730(Colorectal)/Colorectal-Liver-Metastases/CRLM-CT-1001/06-06-1992-NA-CT ANGIO ABD WITH PEL-75163/100.000000-Segmentation-46600/1-1.dcm")
pixels = dcm.pixel_array
print(pixels.shape)

# dcm_images = pydicom.dcmread()
# pixels_images = dcm_images.pixel_array

n_images_patient1 = len(os.listdir('/content/drive/MyDrive/manifest-1669817128730(Colorectal)/Colorectal-Liver-Metastases/CRLM-CT-1001/06-06-1992-NA-CT ANGIO ABD WITH PEL-75163/101.000000-NA-71548'))
print("No. of images for patient 1  : ",n_images_patient1)
print("No. of segmentations for patient 1 : ",pixels.shape[0])

print(pixels[10].shape)
print(type(pixels[10]))

# pixels[10] = np.reshape(pixels[10],(128,128))

resized_image = zoom(pixels[10], zoom=(128/512, 128/512), order=1)

print(resized_image.shape)
# for i in range(pixels.shape[0]):
#     plt.figure()
#     plt.imshow(pixels[i], cmap='gray')
#     plt.title(f"Segmentation Map {i+1}")
#     plt.axis('off')
#     plt.show()

"""YE FINALLY USE HONGE TRAINING MAI"""

CT_Images = []
Bounding_Boxes = []
Seg_Labels = []

"""THIS IS DATASET SORTING USING OS MODULE"""

def ConvertDCMtoArray(path_to_DCM):
   import pydicom
   import cv2
   import numpy as np
   dcm_file = pydicom.dcmread(path_to_DCM)
   pixels = dcm_file.pixel_array.astype(np.uint8)
   image_jpg = cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR (OpenCV default format)
  #  cv2.imwrite('/content/CTImages/image.jpg',image_jpg)  # Save the JPEG image
  #  # Read JPEG image and convert it back to NumPy array
  #  image_loaded = cv2.imread('/content/CTImages/image.jpg')  # Read the JPEG image
  #  image_np_loaded = cv2.cvtColor(image_loaded, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
   image_np_loaded = cv2.cvtColor(image_jpg, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
   image_np_loaded = cv2.resize(image_np_loaded, (64,64))
   return image_np_loaded

# import os

# # local drive directory containing all patient files
# patients_dir = "/content/drive/MyDrive/manifest-1669817128730(Colorectal)/Colorectal-Liver-Metastases"

# os.chdir(patients_dir)

# patients = os.listdir(patients_dir)
# patients = patients[::-1]
# patients.pop()

# total_images = 0
# total_segs = 0
# total_patients = 0

# for patient in patients:
#     total_patients += 1
#     if(total_patients == 40):
#       break
#    # Now we are in patient say CRLM-CT-1001
    
#     # CT_mode is the only folder(which contains further files) in the patient folder
#     CT_mode = os.listdir(os.path.join(patients_dir,patient))
    
#     patient_path = os.path.join(patients_dir,patient)

#     patient_files_folders = os.listdir(os.path.join(patient_path,CT_mode[0]))
#     # Now patient_files_folders[0] must be CT images folder ka name
#     # and patient_files_folders[1] must be masks ke folder ka name
    
#     CT_mode_path = os.path.join(patient_path,CT_mode[0])

#     seg_folder_number = 1
#     images_folder_number = 0

#     # If the first folder contains Segmentation then search for segs in 0
#     if("Segmentation" in patient_files_folders[0]):
#       seg_folder_number = 0
#       images_folder_number = 1
    
#     patient_seg_path = os.path.join(CT_mode_path,patient_files_folders[seg_folder_number])

#     patient_images_path = os.path.join(CT_mode_path,patient_files_folders[images_folder_number])

#     # patient_seg is a vector which contains 1 seg file of patient patient only)
#     patient_seg = os.listdir(patient_seg_path)
    

#     # Now we have the seg file in patient_seg[0] we can see its first dim
#     seg_file_path = os.path.join(patient_seg_path,patient_seg[0])
#     dcm_file = pydicom.dcmread(seg_file_path)
#     pixels = dcm_file.pixel_array
#     segmentation_files = pixels.shape[0]

#     # converted 0s and 1s of seg map to float32
#     # pixels[0] = pixels[0].astype("float32")

#     # bounding_boxes = getBoundingBox(pixels[0])

#     # print("Bounding Box : ",bounding_boxes)
#     # print("Segmentation file : ",pixels[0])
#     # print("Segmetation file dim ",pixels[0].shape)
#     # print("Segmentation file type",pixels[0].dtype)
        
#     #patient CT_images contains all the patient CT_images (1 patient only)
#     patient_CT_images = os.listdir(patient_images_path)
    
#     for i in range(len(patient_CT_images)):
#         image_path = os.path.join(patient_images_path,patient_CT_images[i])
#         image = ConvertDCMtoArray(image_path)
#         # add the images to array
#         CT_Images.append(image)

#     # Adding only image ke jitne seg masks for now
#     for i in range(len(patient_CT_images)):
#         pixels[i] = pixels[i].astype("float32")
#         bounding_box = getBoundingBox(pixels[i])

#         Bounding_Boxes.append(bounding_box)
#         Seg_Labels.append(pixels[i])
    
#     total_images += len(patient_CT_images)
#     total_segs += segmentation_files

#     # print(f"patient {total_patients} images",len(patient_CT_images))
#     # print(f"patient {total_patients} seg",segmentation_files)
#     # print()
  
# print("Total patients : ",total_patients)
# print("Total Images : ",total_images)
# print("Total_segmentation_files : ",total_segs)

import torch
import torch.nn.functional as F
import os

# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

patients_dir = "/content/drive/MyDrive/manifest-1669817128730(Colorectal)/Colorectal-Liver-Metastases"
os.chdir(patients_dir)

patients = os.listdir(patients_dir)
patients = patients[::-1]
patients.pop()

total_images = 0
total_segs = 0
total_patients = 0

CT_Images = []
Bounding_Boxes = []
Seg_Labels = []

print(patients)
patients.remove('.ipynb_checkpoints')
patients.remove('image.jpg')


for patient in patients:
    total_patients += 1
    if total_patients == 10:
        break
    
    CT_mode = os.listdir(os.path.join(patients_dir, patient))
    patient_path = os.path.join(patients_dir, patient)
    patient_files_folders = os.listdir(os.path.join(patient_path, CT_mode[0]))

    CT_mode_path = os.path.join(patient_path, CT_mode[0])
    seg_folder_number = 1
    images_folder_number = 0

    if "Segmentation" in patient_files_folders[0]:
        seg_folder_number = 0
        images_folder_number = 1

    patient_seg_path = os.path.join(CT_mode_path, patient_files_folders[seg_folder_number])
    patient_images_path = os.path.join(CT_mode_path, patient_files_folders[images_folder_number])

    patient_seg = os.listdir(patient_seg_path)
    seg_file_path = os.path.join(patient_seg_path, patient_seg[0])
    dcm_file = pydicom.dcmread(seg_file_path)
    pixels = dcm_file.pixel_array
    segmentation_files = pixels.shape[0]

    patient_CT_images = os.listdir(patient_images_path)
    
    for i in range(len(patient_CT_images)):
        image_path = os.path.join(patient_images_path, patient_CT_images[i])

        # IMAGE DIM ARE ALSO CHANGED TO 64x64
        image = ConvertDCMtoArray(image_path)
        CT_Images.append(torch.tensor(image, dtype=torch.float32))

    for i in range(len(patient_CT_images)):
        pixels[i] = pixels[i].astype("float32")
        bounding_box = getBoundingBox(pixels[i])

        # CHANGING LABEL DIM TO 64x64 
        pixels[i] = zoom(pixels[i], zoom=(64/512, 64/512), order=1)
        Bounding_Boxes.append(torch.tensor(bounding_box, dtype=torch.float32))
        Seg_Labels.append(torch.tensor(pixels[i], dtype=torch.float32))
    
    total_images += len(patient_CT_images)
    total_segs += segmentation_files

# Convert the lists to tensors
CT_Images = torch.stack(CT_Images)
Bounding_Boxes = torch.stack(Bounding_Boxes)
Seg_Labels = torch.stack(Seg_Labels)

print("Total patients: ", total_patients)
print("Total Images: ", total_images)
print("Total segmentation files: ", total_segs)

# import torch
# import torch.nn.functional as F
# import os

# # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# patients_dir = "/content/drive/MyDrive/manifest-1669817128730(Colorectal)/Colorectal-Liver-Metastases"
# os.chdir(patients_dir)

# patients = os.listdir(patients_dir)
# patients = patients[::-1]
# patients.pop()

# total_images = 0
# total_segs = 0
# total_patients = 0

# CT_Images = []
# Bounding_Boxes = []
# Seg_Labels = []

# print(patients)
# patients.remove('.ipynb_checkpoints')


# for patient in patients:
#     total_patients += 1
#     if total_patients == 40:
#         break
    
#     CT_mode = os.listdir(os.path.join(patients_dir, patient))
#     print(CT_mode)
#     patient_path = os.path.join(patients_dir, patient)
#     patient_files_folders = os.listdir(os.path.join(patient_path, CT_mode[0]))

#     CT_mode_path = os.path.join(patient_path, CT_mode[0])
#     seg_folder_number = 1
#     images_folder_number = 0

#     if "Segmentation" in patient_files_folders[0]:
#         seg_folder_number = 0
#         images_folder_number = 1

#     patient_seg_path = os.path.join(CT_mode_path, patient_files_folders[seg_folder_number])
#     patient_images_path = os.path.join(CT_mode_path, patient_files_folders[images_folder_number])

#     patient_seg = os.listdir(patient_seg_path)
#     seg_file_path = os.path.join(patient_seg_path, patient_seg[0])
#     dcm_file = pydicom.dcmread(seg_file_path)
#     pixels = dcm_file.pixel_array
#     segmentation_files = pixels.shape[0]

#     patient_CT_images = os.listdir(patient_images_path)
    
#     for i in range(len(patient_CT_images)):
#         image_path = os.path.join(patient_images_path, patient_CT_images[i])
#         image = ConvertDCMtoArray(image_path)
#         CT_Images.append(image)

#     for i in range(len(patient_CT_images)):
#         pixels[i] = pixels[i].astype("float32")
#         bounding_box = getBoundingBox(pixels[i])

#         Bounding_Boxes.append(bounding_box)
#         Seg_Labels.append(pixels[i])
    
#     total_images += len(patient_CT_images)
#     total_segs += segmentation_files

# # Convert the lists to tensors
# CT_Images = torch.stack(CT_Images)
# Bounding_Boxes = torch.stack(Bounding_Boxes)
# Seg_Labels = torch.stack(Seg_Labels)

# print("Total patients: ", total_patients)
# print("Total Images: ", total_images)
# print("Total segmentation files: ", total_segs)

"""# TRAINING

ONLY STRUCTURE , THIS IS TO BE MODIFIED ALOT
"""

def dice_loss(pred, target):
    intersection = (pred * target).sum()
    dice_coef = (2.0 * intersection) / (pred.sum() + target.sum() + 1e-8)  
    return 1 - dice_coef

"""This is the function which would produce outputs for a batch using 
SAM modified model
"""

def calculateOutputSAM(sam,images,bounding_boxes,batch_size):
    import torch.nn.functional as F
    import torch
    # here all are tensors of size batch_size 
    # image[i] and bounding_boxes[i] ko sam mai bhejo 
    # and output nikalo
    # sabko vector mai daalo 
    # tensor banake and return karado 
    outputs = []

    for i in range(batch_size):
        # tensor_cpu = images[i].cpu()
        array = images[i].cpu().numpy()
        array = array.astype("uint8")
        # print(type(images[i]))
        # print(images[i].shape)
        predictor_loaded.set_image(array)
        input_box = np.array(bounding_boxes[i].cpu())

        masks, _, _ = predictor_loaded.predict(
            point_coords=None,
            point_labels=None,
            box=input_box[None, :],
            multimask_output=False,
        )
        mask_int = masks[0].astype(int)
        mask_float = masks[0].astype("float32")

        t1 = torch.from_numpy(mask_float) 
        outputs.append(t1)
  
    tensor = torch.stack(outputs)

    return tensor

import torch
import torch.nn.functional as F

# Assume 
# Train_images = [t1,t2,t3,t4]
# Bounding_box_train = [b1,b2,b3,b4]
# Train_labels = [l1,l2,l3,l4]

# Test_images , Bounding_box_Test , Test_labels 
# same for validation 

# We use the AdamW [68] optimizer (β1 =0.9, β2 = 0.999)

# The batch size is 256 images

# To regularize SAM,
# we set weight decay (wd) to 0.1 and apply drop path [53]
# (dp) with a rate of 0.4. We use a layer-wise learning rate
# decay [5] (ld) of 0.8.

#  No data augmentation is applied

optimizer = torch.optim.AdamW(
    sam_loaded.parameters(),
    lr = 8e-4,
    betas = (0.9,0.999)
)

batch_size = 256
num_epochs = 2

# train_images_tensor = torch.tensor(CT_Images, dtype=torch.float32).to(device)
# bounding_boxes_tensor = torch.tensor(Bounding_Boxes, dtype=torch.float32).to(device)
# segmentation_masks_tensor = torch.tensor(Seg_Labels, dtype=torch.float32).to(device)

# Convert the input vectors to PyTorch tensors
train_images_tensor = CT_Images.to(device)
bounding_boxes_tensor = Bounding_Boxes.to(device)
segmentation_masks_tensor = Seg_Labels.to(device)

# Combine the input tensors into a single dataset
dataset = torch.utils.data.TensorDataset(train_images_tensor, bounding_boxes_tensor, segmentation_masks_tensor)

# Create a data loader for batching
data_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Training loop
for epoch in range(num_epochs):
    print(f"Epoch {epoch+1}/{num_epochs}")
    
    # Set the model to training mode
    sam_loaded.train()

    # Variables to track accuracy
    correct = 0
    total = 0
    
    # Iterate over the data loader
    for batch_idx, (images, bounding_boxes, masks) in enumerate(data_loader):
        
        # images , bounding_boxes,masks are tensors with 
        # first dimensions as 256 (batch size)

        images = images.to(device)
        bounding_boxes = bounding_boxes.to(device)
        masks = masks.to(device)
        
        print(images.shape)
        print(bounding_boxes.shape)
        print(masks.shape)
        # Clear the gradients
        optimizer.zero_grad()
        
        outputs = calculateOutputSAM(sam_loaded,images,bounding_boxes,batch_size)
        
        outputs.to(device)

        # Calculate the Dice loss
        loss = dice_loss(outputs, masks)
        
        # Backward pass
        loss.backward()
        
        # Update the model parameters
        optimizer.step()

        # Calculate accuracy
        predicted_masks = (outputs > 0.5).float()
        correct += (predicted_masks == masks).sum().item()
        total += masks.numel()
        
        # Print the loss for every few iterations
        if (batch_idx+1) % 10 == 0:
           accuracy = 100 * correct / total
           print(f"Batch {batch_idx+1}/{len(data_loader)} Loss: {loss.item():.4f} Accuracy: {accuracy:.2f}%")

import torch
import torch.nn.functional as F

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

# Assume 
# Train_images = [t1,t2,t3,t4]
# Bounding_box_train = [b1,b2,b3,b4]
# Train_labels = [l1,l2,l3,l4]

# Test_images , Bounding_box_Test , Test_labels 
# same for validation 

# We use the AdamW [68] optimizer (β1 =0.9, β2 = 0.999)

# The batch size is 256 images

# To regularize SAM,
# we set weight decay (wd) to 0.1 and apply drop path [53]
# (dp) with a rate of 0.4. We use a layer-wise learning rate
# decay [5] (ld) of 0.8.

# No data augmentation is applied

optimizer = torch.optim.AdamW(
    sam_loaded.parameters(),
    lr=8e-4,
    betas=(0.9, 0.999),
    weight_decay=0.1
)

batch_size = 16
num_epochs = 2
gradient_accumulation_steps = 8
counter = 0

# Convert the input vectors to PyTorch tensors
train_images_tensor = torch.tensor(CT_Images, dtype=torch.float32).to(device)
bounding_boxes_tensor = torch.tensor(Bounding_Boxes, dtype=torch.float32).to(device)
segmentation_masks_tensor = torch.tensor(Seg_Labels, dtype=torch.float32).to(device)

# Combine the input tensors into a single dataset
dataset = torch.utils.data.TensorDataset(train_images_tensor, bounding_boxes_tensor, segmentation_masks_tensor)

# Create a data loader for batching
data_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

# Training loop
for epoch in range(num_epochs):
    print(f"Epoch {epoch+1}/{num_epochs}")
    
    # Set the model to training mode
    sam_loaded.train()

    # Variables to track accuracy
    correct = 0
    total = 0
    
    # Iterate over the data loader
    for batch_idx, (images, bounding_boxes, masks) in enumerate(data_loader):
        
        # images , bounding_boxes,masks are tensors with 
        # first dimensions as 16 (batch size)

        images = images.to(device)
        bounding_boxes = bounding_boxes.to(device)
        masks = masks.to(device)
        
        # Clear the gradients only at the beginning of each accumulation cycle
        if counter % gradient_accumulation_steps == 0:
            optimizer.zero_grad()
        
        outputs = calculateOutputSAM(sam_loaded, images, bounding_boxes, batch_size)
        
        # Calculate the Dice loss
        loss = dice_loss(outputs, masks)
        
        # Backward pass
        loss.backward()
        
        # Perform the backward pass only at the end of each accumulation cycle
        if counter % gradient_accumulation_steps == gradient_accumulation_steps - 1:
            optimizer.step()
        
        counter += 1

        # Calculate accuracy
        predicted_masks = (outputs > 0.5).float()
        correct += (predicted_masks == masks).sum().item()
        total += masks.numel()
        
        # Print the loss for every few iterations
        if (batch_idx+1) % 10 == 0:
            accuracy = 100 * correct / total
            print(f"Batch {batch_idx+1}/{len(data_loader)} Loss: {loss.item():.4f} Accuracy: {accuracy:.2f}%")

"""# TESTING

ONLY STRUCTURE , THIS IS TO BE MODIFIED ALOT
"""

import torch
import torch.nn.functional as F
from sklearn.metrics import confusion_matrix

# Assuming test_images, test_bounding_boxes, and test_segmentation_masks are your test input vectors
# Assuming model is your trained model

# Set the device for computations
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Define the batch size
batch_size = 256

test_images = []
test_bounding_boxes = []
test_segmentation_masks = []

# Convert the test input vectors to PyTorch tensors
test_images_tensor = torch.tensor(test_images, dtype=torch.float32).to(device)
test_bounding_boxes_tensor = torch.tensor(test_bounding_boxes, dtype=torch.float32).to(device)
test_segmentation_masks_tensor = torch.tensor(test_segmentation_masks, dtype=torch.float32).to(device)

# Combine the test input tensors into a single dataset
test_dataset = torch.utils.data.TensorDataset(test_images_tensor, test_bounding_boxes_tensor, test_segmentation_masks_tensor)

# Create a data loader for batching the test data
test_data_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size)

# Set the model to evaluation mode
sam_loaded.eval()

# Variables to track accuracy and predictions
correct = 0
total = 0
all_predictions = []
all_labels = []

# Iterate over the test data loader
with torch.no_grad():
    for images, bounding_boxes, masks in test_data_loader:
        # Transfer the batch tensors to the device
        images = images.to(device)
        bounding_boxes = bounding_boxes.to(device)
        masks = masks.to(device)
        
        # Forward pass
        outputs = sam_loaded(images)
        
        # Threshold the predicted masks to obtain binary predictions (0 or 1)
        predicted_masks = (outputs > 0.5).float()
        
        # Flatten the predicted masks and ground truth masks
        predicted_masks = predicted_masks.view(-1)
        masks = masks.view(-1)
        
        # Calculate accuracy
        correct += (predicted_masks == masks).sum().item()
        total += masks.numel()
        
        # Store the predictions and labels for confusion matrix
        all_predictions.extend(predicted_masks.cpu().tolist())
        all_labels.extend(masks.cpu().tolist())

# Calculate accuracy
accuracy = 100 * correct / total

# Create the confusion matrix
confusion_mat = confusion_matrix(all_labels, all_predictions)

print(f"Accuracy: {accuracy:.2f}%")
print("Confusion Matrix:")
print(confusion_mat)