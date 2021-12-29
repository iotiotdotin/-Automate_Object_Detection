# Automate_Object_Detection

## Tutorial :

#### Click here for tutorial : [Collab](https://colab.research.google.com/drive/1FfevYpXXd-wAzmNWmX3vN7cJQ-xd-49Q#scrollTo=n4EucbVWTa1r)

## Steps to run :
1. Upload your dataset folder containing `images (.jpg or .png)` and `annotation files (.xml , .json , .csv)` to Google Drive
2. Make a `copy of Collab` [Link given above in tutorial].
3. Open the copied collab and `mount your drive`.
4. Navigate to any folder and clone the repository
   > ```markdown
   > ! git clone https://github.com/iotiotdotin/Automate_Object_Detection.git
   > ```
5. Run setup.py script to create necessary folder structure and downlaoding pretrained models
   > ```markdown
   > %run setup.py
   > ```
6. Run resize_dataset.py this will resize images to 224x224 and change the annotation files accordingly so that they fit into colabs memory while training.
   >```markdown
   > !python resize_dataset.py -p /content/gdrive/MyDrive/images_2
   > ```
7. Lets prepare our dataset and create tfrecords.
   > ```markdown
   > %run prepare_dataset.py
   > ```
8. Start training our model.
   > #### Parameters:
   >
   > -st : Number of steps in training<br>
   > -c : classes in dataset
   >
   > ```markdown
   > !python train.py -st 250 -c 2
   > ```
9. Freeze the trained model.
   > ```markdown
   > %run eval_freeze.py
   > ```
10. Check your predictions
   >
   > #### Parameters:
   >
   > -c : Number of classes in dataset<br>
   > -n : Number of images to show predictions on
   >
   > ```markdown
   > %run plot.py -c 2 -n 10
   > ```
