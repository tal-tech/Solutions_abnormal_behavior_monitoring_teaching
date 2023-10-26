# -*- coding: utf-8 -*-
import tensorflow as tf
import os
class Body_parsing(object):
    # deviceid:gpu设备id
    def __init__(self, sess,graph):

        # body-parsing
        self.isess1 = sess
        with graph.as_default():
            parse_names = 'ExpandDims_1'

            ##########################################################################
            output_graph_def = tf.GraphDef()
            with open(os.path.join(os.path.dirname(__file__),'models/parse_body_tf_GES_v2.0.0.pb'), "rb") as f:
                output_graph_def.ParseFromString(f.read())
                _ = tf.import_graph_def(output_graph_def, name="")

            self.isess1.run(tf.global_variables_initializer())
            self.img_input = self.isess1.graph.get_tensor_by_name("Placeholder:0")
            self.parse_result = self.isess1.graph.get_tensor_by_name(parse_names + ':0')

        print('load human-parsing model')

    # image detect
    def parse(self, img):
        parsing_ = self.isess1.run([self.parse_result], feed_dict={self.img_input: img})
        return parsing_





