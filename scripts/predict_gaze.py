import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, BatchNormalization
from keras.layers import Embedding
from keras.layers import Conv1D, MaxPooling1D
from sklearn import preprocessing
from keras.callbacks import CSVLogger
import statsmodels.api as sm



def format_train_test_data(train_tsv_path, test_tsv_path, show_corr_map=False):

    # #path to directory that holds output of running OpenFace
    # processed_directory = os.path.dirname(os.path.realpath(__file__)) + '/processed/'
    # #finds csv output from running OpenFace
    # data = pd.read_csv(processed_directory + video_name + ".csv", engine='python', delimiter = ', ')
    # #forms DataFrame in desired output format
    # reformatted_data = pd.DataFrame(columns=['Time', 'Duration', 'Trackname', 'Comments'])

    # original_df = pd.read_csv(original_tsv_path, engine='python', delimiter = '\t')

    # read/clean data
    train_df = pd.read_csv(train_tsv_path, engine='python', delimiter = '\t', header=0)
    train_df.fillna(method='ffill', inplace=True)
    test_df = pd.read_csv(test_tsv_path, engine='python', delimiter = '\t', header=0)
    test_df.dropna()

    # create y labels
    y_train = pd.get_dummies(train_df.loc[:, 'trackname']).to_numpy()
    y_test = pd.get_dummies(test_df.loc[:, 'trackname']).to_numpy()


    # dropped features for training
    columns_to_drop = ['trackname', 'frame', 'face_id', 'timestamp', 'confidence', 'success', 'AU01_r',
                       'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r', 'AU09_r', 'AU10_r',
                       'AU12_r', 'AU14_r', 'AU15_r', 'AU17_r', 'AU20_r', 'AU23_r', 'AU25_r',
                       'AU26_r', 'AU45_r', 'AU01_c', 'AU02_c', 'AU04_c', 'AU05_c', 'AU06_c',
                       'AU07_c', 'AU09_c', 'AU10_c', 'AU12_c', 'AU14_c', 'AU15_c', 'AU17_c',
                       'AU20_c', 'AU23_c', 'AU25_c', 'AU26_c', 'AU28_c', 'AU45_c']

    train_df = train_df.drop(columns_to_drop, axis=1)
    test_df = test_df.drop(columns_to_drop, axis=1)

    # removing features with high correlation
    corr = train_df.corr()
    columns = np.full((corr.shape[0],), True, dtype=bool)
    for i in range(1, corr.shape[0]):
        for j in range(i + 1, corr.shape[0]):
            if corr.iloc[i, j] >= 0.9: # should this be absolute value?
                if columns[j]:
                    columns[j] = False

    selected_columns = train_df.columns[columns]
    train_df = train_df[selected_columns]
    test_df = test_df[selected_columns]

    #create x labels
    x_train = train_df.to_numpy()
    x_train = preprocessing.scale(x_train)
    x_test = test_df.to_numpy()
    x_test = preprocessing.scale(x_test)
    print(x_train.shape, x_test.shape, y_train.shape, y_test.shape)

    # correlation map
    if show_corr_map:
        corr_map = plt.figure(figsize=(9, 10))
        plt.matshow(train_df.corr(), fignum=corr_map.number)
        plt.xticks(range(0, train_df.shape[1], 20), rotation=45)
        plt.yticks(range(0, train_df.shape[1], 20))
        cb = plt.colorbar()
        cb.ax.tick_params(labelsize=14)
        plt.title('Correlation Matrix', fontsize=16)
        plt.show()

    return x_train, y_train, x_test, y_test


def train_model(x_train, y_train, x_test, y_test):

    # set parameters:
    batch_size = 32
    filters = 250
    kernel_size = 3
    epochs = 10

    print(len(x_train), 'train sequences')
    print(len(x_test), 'test sequences')

    x_train = np.expand_dims(x_train, axis=2)  # reshape (a, b) to (a, b, 1)
    x_test = np.expand_dims(x_test, axis=2)  # reshape (a, b) to (a, b, 1)
    print(x_train.shape)
    print(x_test.shape)

    print('Build model...')
    model = Sequential()

    #CNN layer
    model.add(Conv1D(filters, kernel_size, padding='valid', strides=3, input_shape=(x_test.shape[1], 1)))
    model.add(BatchNormalization())
    model.add(Activation("relu"))

    #max pooling
    model.add(MaxPooling1D(pool_size=2))

    #CNN layer
    model.add(Conv1D(filters, 1, padding='valid', strides=3))
    model.add(BatchNormalization())
    model.add(Activation("relu"))

    #max pooling
    model.add(MaxPooling1D(pool_size=2))

    # flatten
    model.add(Flatten())

    # hidden layer
    model.add(Dense(64))
    model.add(Dropout(0.4))
    model.add(Activation('relu'))

    #output layer
    model.add(Dense(y_train.shape[1], activation='softmax'))

    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    model.summary()

    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              verbose=1,
              validation_data=(x_test, y_test))


if __name__ =='__main__':
    train_tsv_path = '~/PycharmProjects/gaze-detection-project/openface_data/train.tsv'
    test_tsv_path = '~/PycharmProjects/gaze-detection-project/openface_data/test.tsv'
    x_train, y_train, x_test, y_test = format_train_test_data(train_tsv_path, test_tsv_path, show_corr_map=False)
    train_model(x_train, y_train, x_test, y_test)

