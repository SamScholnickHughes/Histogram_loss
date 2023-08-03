"""Module containing the run code for time series experiments.

Usage: 
    python main.py data_path

Params:
    data_path - path to the input data file
"""

import tensorflow as tf
from tensorflow import keras
from experiment.models import HLGaussian, Regression
from time_series.base_models import transformer, linear, lstm_encdec
import json
import sys
from experiment.bins import get_bins
from time_series.datasets import get_time_series_dataset


def main(data_path):
    """Run the time series experiment.
    
    Params:
        data_path - path to the data file
    """
    pred_len = 336
    seq_len = 96
    epochs = 40
    sig_ratio = 2.
    pad_ratio = 3.
    n_bins = 25
    chans = 7
    # head_size = 512
    # n_heads = 8
    # features = 128
    layers = 5
    width = 128
    test_ratio = 0.25
    batch_size = 32
    drop = "date"
    metrics = ["mse", "mae"]
    lr = 1e-4

    keras.utils.set_random_seed(1)
    train, test, dmin, dmax = get_time_series_dataset(data_path, drop, seq_len, pred_len, pred_len, test_ratio, batch_size, chans)

    borders, sigma = get_bins(n_bins, pad_ratio, sig_ratio, dmin, dmax)
    borders = tf.expand_dims(borders, -1)
    sigma = tf.expand_dims(sigma, -1)

    shape = train.element_spec[0].shape[1:]

    #base = get_model(shape, head_size, n_heads, features)
    #base = linear_model(chans, seq_len)
    for layers in [2, 3, 5, 7]:
        for width in [128, 256, 512]:
            base = lstm_encdec(width, layers, 0.5, shape)

            hlg = HLGaussian(base, borders, sigma, out_shape=(chans, pred_len))    
            hlg.compile(keras.optimizers.Adam(lr), None, metrics)
            hist = hlg.fit(train, epochs=epochs, verbose=2, validation_data=test)
            with open(f"HL_transformer_{layers}_{width}.json", "w") as file:
                json.dump(hist.history, file)

            #base = get_model(shape, head_size, n_heads, features)
            #base = linear_model(chans, seq_len)
            base = lstm_encdec(width, layers, 0.5, shape)

            reg = Regression(base, out_shape=(chans, pred_len))    
            reg.compile(keras.optimizers.Adam(lr), "mse", metrics)
            hist = reg.fit(train, epochs=epochs, verbose=2, validation_data=test)
            with open(f"Reg_transformer_{layers}_{width}.json", "w") as file:
                json.dump(hist.history, file)


if __name__ == "__main__":
    data_path = sys.argv[1]
    main(data_path)