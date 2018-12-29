from keras.models import Sequential
from keras.layers import Dense


def train_mlp(train_x, train_y, verbose=True):
    """
    VERY basic multi layer perceptron neurel network
    Using keras only for POC
    """
    model = Sequential()

    model.add(Dense(256, activation='relu', kernel_initializer='normal',
                    input_dim=train_x.shape[1]))
    model.add(Dense(256, activation='relu', kernel_initializer='normal'))
    model.add(Dense(128, activation='relu', kernel_initializer='normal'))
    model.add(Dense(1, activation='sigmoid', kernel_initializer='normal'))

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    if verbose:
        model.summary()
    model.fit(train_x, train_y, epochs=20, validation_split=.1)

    return model
