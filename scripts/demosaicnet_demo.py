#!/usr/bin/env python
"""Demo script on using demosaicnet for inference."""

import os
from pkg_resources import resource_filename
import time

import argparse
import numpy as np
import torch as th
import imageio

import demosaicnet

_TEST_INPUT = resource_filename("demosaicnet", 'data/test_input.png')


def main(args):
    print("Running demosaicnet demo on {}, outputing to {}".format(_TEST_INPUT, args.output))
    bayer = demosaicnet.BayerDemosaick()
    xtrans = demosaicnet.XTransDemosaick()

    # Load some ground-truth image
    gt = np.array(imageio.imread(args.input).astype(np.float32) / 255.0)

    # Network expects channel first
    gt = np.transpose(gt, [2, 0, 1])


    mosaicked = demosaicnet.bayer(gt)
    # xmosaicked = demosaicnet.xtrans(gt)

    # Run the model (expects batch as first dimension)
    mosaicked = th.from_numpy(mosaicked).unsqueeze(0)
    # xmosaicked = th.from_numpy(xmosaicked).unsqueeze(0)
    start_time = time.time()
    with th.no_grad():  # inference only
        out = bayer(mosaicked).squeeze(0).cpu().numpy()
        out = np.clip(out, 0, 1)
        # xout = xtrans(xmosaicked).squeeze(0).cpu().numpy()
        # xout = np.clip(xout, 0, 1)
    print("--- %s seconds ---" % (time.time() - start_time))

    print("done")

    if not os.path.exists(args.output):
        os.makedirs(args.output)
    output = args.output

    imageio.imwrite(os.path.join(output, "bayer_mosaick.png"), mosaicked.squeeze(0).permute([1, 2, 0]))
    imageio.imwrite(os.path.join(output, "bayer_result.png"), np.transpose(out, [1, 2, 0]))
    # skio.imsave(os.path.join(output, "xtrans_mosaick.png"), xmosaicked.squeeze(0).permute([1, 2, 0]))
    # skio.imsave(os.path.join(output, "xtrans_result.png"), np.transpose(xout, [1, 2, 0]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="result", help="output directory")
    parser.add_argument("--input", default=_TEST_INPUT,
                        help="test input, uses the default test input provided if no argument.")
    args = parser.parse_args()
    main(args)
