from __future__ import print_function
import dotscience as ds
import os
import shutil

# defaults to connecting to prod
ds.connect(
    os.getenv("DOTSCIENCE_USERNAME"), 
    os.getenv("DOTSCIENCE_APIKEY"), 
    os.getenv("DOTSCIENCE_PROJECT_NAME"),
    os.getenv("DOTSCIENCE_URL")
)

import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras import backend as K

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

batch_size = ds.parameter("batch_size", 128)
num_classes = ds.parameter("num_classes", 10)
epochs = ds.parameter("epochs", 1)

# input image dimensions
img_rows, img_cols = 28, 28
limit = ds.parameter("limit", 1000)

# the data, split between train and test sets
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train[:limit]
y_train = y_train[:limit]

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
              optimizer=tf.keras.optimizers.Adam(),
              metrics=['accuracy'])

model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          verbose=1,
          validation_data=(x_test, y_test))

score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', ds.metric("loss", score[0]))
print('Test accuracy:', ds.metric("accuracy", score[1]))

if os.path.isdir("model"):
    shutil.rmtree("model", ignore_errors=True)

MODEL_DIR = "./model"
export_path = os.path.join(MODEL_DIR)

model.save(export_path)

# copy file into the model dir for the upload
shutil.copyfile("classes.json", "model/classes.json")

ds.model(tf, "mnist", "model", classes="model/classes.json")
ds.publish("trained mnist model", deploy=True)
