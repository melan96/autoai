# Copyright 2021 BlobCity, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Takes data frame, and target only. 
# Should do automatic feature selection
# Should return a trained model
# Should output progress, in an interactive manner while training is in progress

import pickle
import tensorflow as tf
from blobcity.store import DictClass
from blobcity.utils import getDataFrameType
from blobcity.utils import dataCleaner
from blobcity.utils import AutoFeatureSelection as AFS
from blobcity.utils import writeYml
from blobcity.main.modelSelection import modelSearch

def train(file=None, df=None, target=None,features=None):
    """
    Performs a model search on the data proivded. A yaml file is generated once the best fit model configuration
    is discovered. The yaml file is later used for generating source code. 

    Input to the function must be one of file or data frame (df). Passing both parameters of file and df in a single
    invocation is an incorrect use.
    """
    dc=DictClass()
    dc.resetVar()
    #data read
    if file!=None:
        dataframe= getDataFrameType(file, dc)
    else: 
        dataframe = df
        dc.addKeyValue('data_read',{"class":"df"})
        
    if(features==None):
        featureList=AFS.FeatureSelection(dataframe,target,dc)
        CleanedDF=dataCleaner(dataframe,featureList,target,dc)
    else:
        CleanedDF=dataCleaner(dataframe,features,target,dc)
    #model search space
    modelClass = modelSearch(CleanedDF,target,dc)

    #YML generation
    writeYml(dc.getdict())
    #return modelClass object
    dc.resetVar()
    return modelClass
# Performs an automated model training. 


# Reads a BlobCity published model file, and loads it into memory.
# This can be combination of yml and other related artifacts of a trained model
# Need to see if a h5 file of TensorFlow, and a pickel file for other models can be combined into say a .bcm file for storage
# .bcm would be a custom format, standing for a BlobCity Model
def load(modelFile):
        """
        param: (required) the filepath to the stored model. Supports .h5 or .pkl models.
        returns: Model file

        function loads the serialized model from .pkl or .h5 format to usable format.
        """
        path_components = modelFile.split('.')
        if len(path_components)<=2:
            extension = path_components[1]
        else:
            extension = path_components[2]
        
        if extension == 'pkl':
            model = pickle.load(open(modelFile, 'rb'))
        elif extension == 'h5':
            model = tf.keras.models.load_model(modelFile)
       
        return model


