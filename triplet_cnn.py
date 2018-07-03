import cv2
import sys
import numpy as np 
import matplotlib 
matplotlib.use('agg')
import matplotlib.pyplot as plt
import os
import h5py
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from sklearn.model_selection import train_test_split
from keras.utils import plot_model
from keras.applications.vgg16 import VGG16
from keras.applications.resnet50 import preprocess_input, decode_predictions
from keras.preprocessing import image
from keras.applications.resnet50 import ResNet50
from keras.models import Model
from keras.layers import LSTM, Dense
from keras.layers import Input, Embedding, LSTM, Dense
from keras.callbacks import EarlyStopping, ModelCheckpoint
import math

##  

path= "Videovectors"
files= os.listdir(path)
a=[]
b=[]
c=[]


diction= {"Bro":0, "Cotton":1,"Felt": 2, "Sha":3,"Silk":4, "Sweater":5}


for i, folders in enumerate(files):
	video_folder_path= os.path.join(path,folders)
	video_files= os.listdir(video_folder_path)
	for j, videos in enumerate(video_files):
		file_path=os.path.join(video_folder_path,videos)
		feature= np.load(file_path)
		print(folders,videos)

		vid_name=os.path.splitext(videos)[0]
		spt=vid_name.split("_")
		spt[1]=spt[1][1:]
		spt[2]=spt[2][1:]

		a.append(feature)
		b.append(float(spt[1]))
		c.append(diction[spt[0]])
		print(float(spt[1]),diction[spt[0]],spt[0])


input_to_lstm=np.asarray(a)
bs_label=np.asarray(b)
texture_label=  np.asarray(c)
texture_label=keras.utils.to_categorical(texture_label,6)


bs_label=bs_label.reshape(len(bs_label),1)

## Extra dimag
bs_label=np.log10(bs_label)
bs_label=bs_label+2


texture_label=np.append(texture_label,bs_label,axis=1)
print(input_to_lstm.shape,bs_label.shape,texture_label.shape) 



X_train, X_test, y_train, y_test = train_test_split( input_to_lstm,texture_label, test_size=0.2, shuffle= True, random_state=42)

print(X_train.shape, y_train.shape, X_test.shape,y_test.shape)

input_train=X_train
input_test=X_test
bs_label_train= y_train[:,-1]
bs_label_test=y_test[:,-1]
texture_label_train=y_train[:,0:y_train.shape[1]-1]
texture_label_test=y_test[:,0:y_test.shape[1]-1]

print(input_train.shape,input_test.shape, bs_label_train.shape, bs_label_test.shape, texture_label_train.shape,texture_label_test.shape)

#print(bs_label_train)

timesteps=input_train.shape[1]
data_dim= input_train.shape[2]
num_classes=6
main_input = Input(shape=(timesteps,data_dim), name='main_input')
x = LSTM(96, activation='relu')(main_input)
x = Dense(32, activation='sigmoid')(x)
output_1= Dense(1,name='output_1')(x)
output_2= Dense(num_classes,name='output_2',activation='softmax')(x)


model = Model(inputs=[main_input], outputs=[output_1, output_2])
adam=keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
model.compile(optimizer=adam,
              loss={'output_1': 'mean_squared_error', 'output_2': 'categorical_crossentropy'},
              loss_weights={'output_1': 0.5, 'output_2': 0.5})

#callback=[keras.callbacks.EarlyStopping(monitor='val_loss',min_delta=0,patience=10,verbose=0, mode='auto')]
print(model.summary())
#print(model.summary())
history=model.fit({'main_input':input_train},
          {'output_1': bs_label_train, 'output_2':texture_label_train},
          validation_data=({'main_input':input_test}, {'output_1': bs_label_test, 'output_2':texture_label_test}),
          epochs=100, batch_size=10)


print(history.history['loss'])

print(model.predict(input_test))
print(bs_label_test)
print(texture_label_test)