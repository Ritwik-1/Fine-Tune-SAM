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
3) In CT dataset : there are more segmentations in the dataset than the CT slices

**Solved:**
1) Tensors need to be connected to gpu to use GPU RAM
2) Segmentation masks are tensors with each tensor[i] being a mask 
   They are contained in one file only

