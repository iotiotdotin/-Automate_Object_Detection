import tensorflow as tf
from google.protobuf import text_format
from object_detection.protos import pipeline_pb2
import os
import argparse
import glob


parser = argparse.ArgumentParser(
    description="Configure file for the model")
    
parser.add_argument("-r",
                    "--root",
                    help="Path of root directory",
                    type=str)
parser.add_argument("-c",
                    "--classes",
                    help="Number of classes in dataset",
                    type=int)

parser.add_argument("-s",
                    "--steps",
                    help="Number of steps to be performed by the model",
                    default=500,
                    type=int)

parser.add_argument("-ne",
                    "--examples",
                    help="Number of examples to be evaluated in dataset",
                    default=10,
                    type=int)

parser.add_argument("-bs",
                    "--batch_size",
                    help="Batch size for training",
                    default=24,
                    type=int)

parser.add_argument("-lr",
                    "--learning_rate",
                    help="Initial Learning Rate",
                    default=0.004,
                    type=float)

args = parser.parse_args()  

PATH_ROOT=args.root

os.environ['PYTHONPATH'] += ':' + PATH_ROOT + '/tf/research/:'+PATH_ROOT+'/tf/research/slim/:'+PATH_ROOT+'/tf/research/object_detection/utils/:'+PATH_ROOT+'/tf/research/object_detection'



pipeline = pipeline_pb2.TrainEvalPipelineConfig()                                                                                                                                                                                                          
config_path = ''.join(glob.glob(os.getcwd()+"/tf/*.config"))
with tf.gfile.GFile( config_path, "r") as f:                                                                                                                                                                                                                     
    proto_str = f.read()                                                                                                                                                                                                                                          
    text_format.Merge(proto_str, pipeline)

pipeline.train_input_reader.tf_record_input_reader.input_path[:] = [PATH_ROOT+'/tfrecords/train.record']
pipeline.train_config.fine_tune_checkpoint_type = "detection" 
pipeline.train_input_reader.label_map_path = PATH_ROOT + '/tfrecords/label_map.pbtxt'
pipeline.eval_input_reader[0].tf_record_input_reader.input_path[:] = [PATH_ROOT+'/tfrecords/test.record'] 
pipeline.eval_input_reader[0].label_map_path = PATH_ROOT + '/tfrecords/label_map.pbtxt'
pipeline.train_config.fine_tune_checkpoint = PATH_ROOT + '/tf/pretrained_model/model.ckpt'
pipeline.train_config.num_steps = args.steps
pipeline.model.ssd.num_classes = args.classes
pipeline.eval_config.num_examples = args.examples
pipeline.train_config.batch_size = args.batch_size
pipeline.train_config.optimizer.rms_prop_optimizer.learning_rate.exponential_decay_learning_rate.initial_learning_rate=args.learning_rate


config_text = text_format.MessageToString(pipeline)                                                                                                                                                                                                        
with tf.gfile.Open( config_path, "wb") as f:                                                                                                                                                                                                                       
    f.write(config_text)