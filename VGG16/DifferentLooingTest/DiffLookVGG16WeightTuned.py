

import numpy as np
import os
import time
from keras.layers.normalization import BatchNormalization
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.layers import Dense, Activation, Flatten
from keras.layers import merge, Input
from keras.models import Model
import keras.applications
from keras.utils import np_utils
from sklearn.utils import shuffle
from sklearn.cross_validation import train_test_split
from keras.preprocessing.image import ImageDataGenerator
import pickle as pickle
from keras.models import load_model

#Rerun 0 is from scratch 1 is load previous model
############################
############################
############################
Icon = 1
############################
############################
############################
############################
# Loading the training data
PATH = os.getcwd()
# Define data path
data_path = PATH + '/Aves'
data_dir_list = os.listdir(data_path)

img_data_list=[]

for dataset in data_dir_list:
	img_list=os.listdir(data_path+'/'+ dataset)
	print ('Loaded the images of dataset-'+'{}\n'.format(dataset))
	for img in img_list:
		img_path = data_path + '/'+ dataset + '/'+ img
		img = image.load_img(img_path, target_size=(224, 224))
		x = image.img_to_array(img)
		x = np.expand_dims(x, axis=0)
		x = preprocess_input(x)
		print('Input image shape:', x.shape)
		img_data_list.append(x)

img_data = np.array(img_data_list)
print (img_data.shape)
img_data=np.rollaxis(img_data,1,0)
print (img_data.shape)
img_data=img_data[0]
print (img_data.shape)


# Define the number of classes
num_classes = 10
num_of_samples = img_data.shape[0]
labels = np.ones((num_of_samples,),dtype='int64')

labels[0:574]=0
labels[574:671]=1
labels[671:1240]=2
labels[1240:1323]=3
labels[1323:1845]=4
labels[1845:1866]=5
labels[1866:1949]=6
labels[1949:1993]=7
labels[1993:2567]=8
labels[2567:3127]=9


names = ['Calidris alba','Gallus gallus domesticus','Geococcyx californianus',
		 'Phoenicopterus roseus','Picoides villosus','Spheniscus demersus',
		 'Sterna striata','Struthio camelus','Thryothorus ludovicianus','Tyrannus verticalis']

# convert class labels to on-hot encoding
Y = np_utils.to_categorical(labels, num_classes)

#Shuffle the dataset
x,y = shuffle(img_data,Y, random_state=2)
# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=2)

class_weight = {0:1, 1:5.91, 2:1, 3:6.91,4:1.1, 5:27,6:6.91,7:13,8:1,9:1}
# class_weight = {0:1, 1:0, 2:0, 3:0,4:0, 5:0,6:0,7:0,8:0,9:0}
# class_weight = [1,5.91,1,6.91,1.1,27,6.91,13,1,1]

#########################################################################################
#Training the classifier alone
if(Icon == 0):
	image_input = Input(shape=(224, 224, 3))

	model = keras.applications.vgg16.VGG16(include_top=True, weights='imagenet', input_tensor=image_input, classes=1000)
	model.summary()
	last_layer = model.get_layer('fc2').output

	#x= Flatten(name='flatten')(last_layer)
	out = Dense(num_classes, activation='softmax', name='output')(last_layer)
	custom_vgg_model = Model(image_input, out)
	custom_vgg_model.summary()

	for layer in custom_vgg_model.layers[:-1]:
		layer.trainable = False

	custom_vgg_model.layers[3].trainable

#Re-run the pre-model weight
elif(Icon == 1):
	custom_vgg_model = load_model('VGG16custom_WeightChange_Diff22.h5')

#Begin Model Training
custom_vgg_model.compile(loss='categorical_crossentropy',optimizer='Adam',metrics=['accuracy'])
t=time.time()
	# t = now()
hist = custom_vgg_model.fit(X_train, y_train, batch_size=16, epochs=12, verbose=1, validation_data=(X_test, y_test),class_weight=class_weight)
print('Training time: %s' % (t - time.time()))

# hist = custom_vgg_model.fit_generator(datagen.flow(X_train,y_train, batch_size=16),steps_per_epoch=len(X_train)/16,epochs=5)



(loss, accuracy) = custom_vgg_model.evaluate(X_test, y_test, batch_size=10, verbose=1)

print("[INFO] loss={:.4f}, accuracy: {:.4f}%".format(loss,accuracy * 100))

custom_vgg_model.save('VGG16custom_WeightChange_Diff.h5')

np_all = np.array(hist.history['acc'])
np_all = np.append(np_all, np.array(hist.history['loss']), axis=0)
np_all = np.append(np_all, np.array(hist.history['val_acc']), axis=0)
np_all = np.append(np_all, np.array(hist.history['val_loss']), axis=0)
np.savetxt('save0.txt', np_all)





