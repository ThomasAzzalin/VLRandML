import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
import tensorflow as tf
import pandas as pd
import keras
import tensorflow as tf

# Funzione per generare il dataset di input
def make_input_fn(data, labels, num_epochs=100000, shuffle=True, batch_size=128):
    dataset = tf.data.Dataset.from_tensor_slices((dict(data), labels))
    if shuffle:
        dataset = dataset.shuffle(1000)
    dataset = dataset.batch(batch_size)
    return dataset.repeat(num_epochs)

if __name__ == '__main__':
    reg = input("Insert the region you want to save the data: ")
    dftrain = pd.read_csv(f".\\{reg}\\data_sets\\training_dataset.csv")
    dfeval = pd.read_csv(f".\\{reg}\\data_sets\\evaluation_dataset.csv")

    label_train = dftrain.pop("team_a_won")
    label_eval = dfeval.pop("team_a_won")

    # Creazione del dataset di input
    train_input_fn = make_input_fn(dftrain, label_train)
    eval_input_fn = make_input_fn(dfeval, label_eval, num_epochs=1, shuffle=True, batch_size=64)

    # Creazione delle colonne di feature
    feature_columns = [tf.keras.layers.Input(shape=(1,), name=key) for key in [
                                                                             "team_a_atk_win",
                                                                             "team_a_def_win",
                                                                             "team_b_atk_win",
                                                                             "team_b_def_win"]]

    # Concatenazione delle feature
    concatenated = tf.keras.layers.Concatenate()(feature_columns)

    # Creazione del modello con Keras
    output = tf.keras.layers.Dense(1, activation='sigmoid')(concatenated)

    model = tf.keras.Model(inputs=feature_columns, outputs=output)

    # Compilazione del modello
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # Addestramento del modello
    model.fit(train_input_fn, epochs=1)

    # Valutazione del modello
    result = model.evaluate(eval_input_fn)

    print(result)