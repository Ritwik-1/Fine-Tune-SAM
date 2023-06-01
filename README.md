# Fine-Tune-SAM

Fine tune 1:
Freezed parameters for the image encoder for now as there are a lot of parameters already
Added 2 extra MLP layers at the very final layer of the mask decoder to make model extract more
complex details from features
Now only providing BOX prompts to the model as most accuracy in medical imaging is achieved by this 
prompt only.

Methodology:
calculating the dice loss between the label and what the actual unchanged sam is producing 
Now after making the full dataset and training the changed model , will see the accuracy 
of new model and compare with the original
To make the confusion matrix and ROC curves for the test set as well
