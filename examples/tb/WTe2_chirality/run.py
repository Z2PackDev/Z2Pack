#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import lzma
import pickle
from contextlib import suppress

import z2pack
from tbmodels import Model
import matplotlib.pyplot as plt

MODEL_NAME = 'wte2_soc'
MODEL_SOURCE = os.path.join('data', MODEL_NAME + '.json')
MODEL_PATH = os.path.join('data', MODEL_NAME + '.p')

# creating the necessary subfolders
subfolders = ['results', 'plots']
for s in subfolders:
    with suppress(FileExistsError):
        os.mkdir(s)


def calculate_chirality(tag, center, radius, overwrite=False, **kwargs):
    # converting the Model to the pickle format (which is quicker to load)
    # Note that keeping only the pickle format is dangerous, because it
    # may become unreadable -- use the JSON format for long-term saving.
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
    except IOError:
        # The .xz compression is used to avoid the GitHub file size limit
        with lzma.open(MODEL_SOURCE + '.xz') as fin, open(
            MODEL_SOURCE, 'wb'
        ) as fout:
            fout.write(fin.read())

        model = Model.from_json_file(MODEL_SOURCE)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)

    system = z2pack.tb.System(model)
    full_name = MODEL_NAME + '_' + tag
    res = z2pack.surface.run(
        system=system,
        surface=z2pack.shape.Sphere(center, radius),
        save_file=os.path.join('results', full_name + '.p'),
        load=not overwrite,
        **kwargs
    )
    # Again, the pickle format is used because it is faster than JSON
    # or msgpack. If you wish to permanently store the result, use
    # z2pack.io.save(res, os.path.join('results', full_name + '.json'))
    print('Chern number:', z2pack.invariant.chern(res))


def plot_chirality(tag, ax):
    full_name = MODEL_NAME + '_' + tag
    res = z2pack.io.load(os.path.join('results', full_name + '.p'))
    z2pack.plot.chern(res, axis=ax)


if __name__ == "__main__":
    # calculate
    calculate_chirality('0', [0.1203, 0.05232, 0.], 0.005)
    calculate_chirality(
        '1', [0.1211, 0.02887, 0.], 0.005, iterator=range(10, 33, 2)
    )

    # plot
    fig, ax = plt.subplots(
        1, 2, figsize=[4, 2], sharey=True, gridspec_kw=dict(wspace=0.3)
    )
    ax[0].set_xticks([0, 1])
    ax[1].set_xticks([0, 1])
    ax[0].set_xticklabels([r'$-\pi$', r'$0$'])
    ax[1].set_xticklabels([r'$-\pi$', r'$0$'])
    ax[0].set_yticks([0, 1])
    ax[1].set_yticks([0, 1])
    ax[1].set_yticklabels([r'$0$', r'$2\pi$'])
    ax[0].set_xlabel(r'$\theta$')
    ax[1].set_xlabel(r'$\theta$')
    ax[0].set_ylabel(r'$\bar{\varphi}$', rotation='horizontal')
    ax[0].text(-0.2, 1.05, r'(a)', ha='right')
    ax[1].text(-0.05, 1.05, r'(b)', ha='right')
    plot_chirality('0', ax[0])
    plot_chirality('1', ax[1])
    plt.savefig(
        'plots/WTe2_chirality.pdf', bbox_inches='tight', rasterized=True
    )
