""" Sample TensorFlow XML-to-TFRecord converter

usage: generate_tfrecord.py [-h] [-f FILE_DIR] [-o OUTPUT_PATH] [-i IMAGE_DIR] [-c CSV_PATH]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE_DIR, --file_dir FILE_DIR
                        Path to the folder where the input .xml , .csv , .json files are stored.
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path of output TFRecord (.record) file.
  -i IMAGE_DIR, --image_dir IMAGE_DIR
                        Path to the folder where the input image files are stored.
  -c CSV_PATH, --csv_path CSV_PATH
                        Path of output .csv file. If none provided, then no file will be written.
"""

import os
import glob
import pandas as pd
import io
import xml.etree.ElementTree as ET
import argparse
import json

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    # Suppress TensorFlow logging (1)
import tensorflow.compat.v1 as tf

from PIL import Image
from object_detection.utils import dataset_util, label_map_util
from collections import namedtuple

 



# Initiate argument parser
parser = argparse.ArgumentParser(
    description="Sample TensorFlow XML-to-TFRecord converter")
parser.add_argument("-f",
                    "--file_dir",
                    help="Path to the folder where the input .xml ,.json ,.csv files are stored.",
                    type=str)

parser.add_argument("-o",
                    "--output_path",
                    help="Path of output TFRecord (.record) file.", type=str)

parser.add_argument("-i",
                    "--image_dir",
                    help="Path to the folder where the input image files are stored. "
                         "Defaults to the same directory as XML_DIR.",
                    type=str, default=None)
parser.add_argument("-c",
                    "--csv_path",
                    help="Path of output .csv file. If none provided, then no file will be "
                         "written.",
                    type=str, default=None)
parser.add_argument("-s",
                    "--split",
                    type=int, default=70)

args = parser.parse_args()

if args.image_dir is None:
    args.image_dir = args.file_dir

labelpath = args.output_path + '/label_map.pbtxt'



def create_label_map(df) :
    
    labels = df['class'].unique()

    with open(args.output_path + "/label_map.pbtxt", "w+") as f:
        count = 1
        for label in labels:
            f.write('item { \n')
            f.write('\tname:\'{}\'\n'.format(label))
            f.write('\tid:{}\n'.format(count))
            f.write('}\n')
            count+=1


def generate_map(cat) :
    map = {}
    for x in cat :
        map[x["id"]] = x["name"]
    return map


def json_to_csv(path) : 
    f = open(path)
    count = 0
    data = json.load(f)

    imgs = data["images"]
    annot = data["annotations"]
    cat = data["categories"]
    cat_map = generate_map(cat)    
    json_list = []
    total_rec = len(annot)

    for x in imgs:
        filename =  x["file_name"]
        img_id = x["id"]
        height = x["height"]
        width = x["width"]

        for a in annot :
            if a["image_id"] == img_id:
                bbox =  a["bbox"]
                cat_id =  a["category_id"]
                cat_name = cat_map[cat_id]


                value = (filename,
                            width,
                            height,
                            cat_name,
                            bbox[0],
                            bbox[1],
                            bbox[0] + bbox[2] ,
                            bbox[1] + bbox[3] 
                            )
                json_list.append(value)
                count = count+1
                print(count , "/" ,total_rec , "Records converted" ,end="\r")

    column_name = ['filename', 'width', 'height',
                'class', 'xmin', 'ymin', 'xmax', 'ymax']
    json_df = pd.DataFrame(json_list, columns=column_name)

    return json_df



def xml_to_csv(path):
    """Iterates through all .xml files (generated by labelImg) in a given directory and combines
    them in a single Pandas dataframe.

    Parameters:
    ----------
    path : str
        The path containing the .xml files
    Returns
    -------
    Pandas DataFrame
        The produced dataframe
    """

    record_list = []
    filetype = 0
    annot =  glob.glob(path + '/*.xml')
    if(len(annot)==0):
        annot =  glob.glob(path + '/*.json')
        filetype=1

    print("Total files : ",len(annot))
    if filetype==0:
        print("File format : XML")
        for xml_file in annot:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            filename = root.find('filename').text
            width = int(root.find('size').find('width').text)
            height = int(root.find('size').find('height').text)
            for member in root.findall('object'):
                bndbox = member.find('bndbox')
                value = (filename,
                        width,
                        height,
                        member.find('name').text,
                        int(float(bndbox.find('xmin').text)),
                        int(float(bndbox.find('ymin').text)),
                        int(float(bndbox.find('xmax').text)),
                        int(float(bndbox.find('ymax').text)),
                        )
                record_list.append(value)
    if filetype==1:
        print("File format : JSON")
        for json_file in annot:
            f = open(json_file)
            data = json.load(f)
            file_path = data["imagePath"].replace("\\","/")
            filename = os.path.basename(file_path)
            
            width =data["imageWidth"]
            height = data["imageHeight"]
            for shape in data["shapes"]:
                xmin = shape["points"][0][0]
                ymin = shape["points"][0][1]
                xmax = shape["points"][1][0]
                ymax = shape["points"][1][1]
                value = (filename,
                         width,
                         height,
                         shape["label"],
                         int(float(xmin)),
                         int(float(ymin)),
                         int(float(xmax)),
                         int(float(ymax))
                        )
                record_list.append(value)

    column_name = ['filename', 'width', 'height',
                   'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(record_list, columns=column_name)
    return xml_df

   




def list_to_dict(labels) :
    label_id = 1
    label_dict = {}
    for x in labels :
        label_dict[x] = label_id
        label_id = label_id+1
    return label_dict

def class_text_to_int(row_label):
    return label_dict[row_label]


def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]



def train_test_split(df) :
    df = df.sample(frac=1)
    split = args.split
    train_rows = int(df.shape[0]*(split/100))

    df_train = df[:train_rows]
    df_test = df[train_rows:]
    return df_train , df_test

    


def create_tf_example(group, path):
    with tf.io.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    if(group.filename.find(".jpg")==-1):
        image_format = b'png'
    else:
        image_format=b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example

def write_record(examples , record_name):

    if args.csv_path is not None:
        examples.to_csv(args.csv_path+"/"+record_name+".csv" , index=None)
        print('Successfully created the CSV file: {}'.format(args.csv_path))

    writer = tf.io.TFRecordWriter(args.output_path + "/"+record_name) # Write tfrecord to output path
    print("Writerline exectuted")

    grouped = split(examples, 'filename') #passing the dataframe , and namedtuple attribute

    for group in grouped:
        tf_example = create_tf_example(group, path)
        writer.write(tf_example.SerializeToString())
    writer.close()
    print('Successfully created the TFRecord file: {}'.format(args.output_path))


path = os.path.join(args.image_dir)

if args.file_dir is not None :
    if args.file_dir[-4:] == ".csv" :
        print("File format : CSV")
        examples = pd.read_csv(args.file_dir)

    elif args.file_dir[-5:] == ".json" :
        print("File format : JSON")
        examples = json_to_csv(args.file_dir)  

    else : 
        examples = xml_to_csv(args.file_dir) # path to xml annotations directory


create_label_map(examples)
labels = (examples['class'].unique()).tolist()
label_dict = list_to_dict(labels)

train_example , test_example = train_test_split(examples)
write_record(train_example,"train.record" )
write_record(test_example,"test.record" )



