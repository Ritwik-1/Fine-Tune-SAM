# Fine-Tune-SAM

**Fine tune 1 :**
Freezed parameters for the image encoder for now as there are a lot of parameters already
Added 2 extra MLP layers at the very final layer of the mask decoder to make model extract more
complex details from features
Now only providing BOX prompts to the model as most accuracy in medical imaging is achieved by this 
prompt only.

**Methodology:**
calculating the dice loss between the label and what the actual unchanged sam is producing 
Now after making the full dataset and training the changed model , will see the accuracy 
of new model and compare with the original
To make the confusion matrix and ROC curves for the test set as well

**Problems:** 
1) GPU and system RAM is getting crashed on colab for 40 patients as well ?
2) How to see how many tensors are to be connected to gpu ?
3) GPU runtime has a limit after which we cannot access a GPU , ????
4) In CT dataset : there are more segmentations in the dataset than the CT slices
5) How to like make packages be permanantly installed in colab with pip install

**TODO**
1) Try using a seperate file for training the model , 
2) But connecting files is not easy in colab?? 
3) Images need to be reshaped from 512x512 to 128x128 for saving RAM,
4) but masks are not getting reshaped to (128,128)?????
**Solved:**
1) Tensors need to be connected to gpu to use GPU RAM
2) Segmentation masks are tensors with each tensor[i] being a mask 
   They are contained in one file only

