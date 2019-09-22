from __future__ import print_function
import dotscience as ds
import os

# defaults to connecting to prod
ds.connect(os.getenv("DOTSCIENCE_USERNAME"), os.getenv("DOTSCIENCE_APIKEY"))

###

def foo(x, deploy=True):
    print("Uploading model files... done\n")
    print("Building docker image... done")
    print("Docker image: hub.dotscience.com/username/tensorflow:a1b2c3\n")
    print("Deploying to Kubernetes... done")
    print("Endpoint: https://tensorflow-a1b2c3.models.cloud.dotscience.com/\n")
    print("Creating Grafana dashboard... done")
    print("Dashboard: https://tensorflow-a1b2c3.dashboards.cloud.dotscience.com/\n")
#ds.publish = foo

###

import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras import backend as K

batch_size = ds.parameter("batch_size", 128)
num_classes = ds.parameter("num_classes", 10)
epochs = ds.parameter("epochs", 1)

# input image dimensions
img_rows, img_cols = 28, 28

# the data, split between train and test sets
(x_train, y_train), (x_test, y_test) = mnist.load_data()

if K.image_data_format() == 'channels_first':
    x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
    x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
    input_shape = (1, img_rows, img_cols)
else:
    x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
    input_shape = (img_rows, img_cols, 1)

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = tf.keras.utils.to_categorical(y_train, num_classes)
y_test = tf.keras.utils.to_categorical(y_test, num_classes)

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=input_shape))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

model.compile(loss=tf.keras.losses.categorical_crossentropy,
              optimizer=tf.keras.optimizers.Adadelta(),
              metrics=['accuracy'])

model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          verbose=1,
          validation_data=(x_test, y_test))
score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', ds.metric("loss", score[0]))
print('Test accuracy:', ds.metric("accuracy", score[1]))

#model.save("model.h5")
#tf.keras.experimental.export_saved_model(model, ds.model(tf, 'model'))
tf.keras.experimental.export_saved_model(model, ds.output('model'))

ds.publish("trained mnist model")
