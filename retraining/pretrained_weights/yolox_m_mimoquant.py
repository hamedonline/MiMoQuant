#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) Megvii, Inc. and its affiliates.

# import torch.nn as nn
from yolox.exp import Exp as MyExp


class Exp(MyExp):
    def __init__(self):
        super(Exp, self).__init__()
        self.num_classes = 2
        self.depth = 1.0
        self.width = 1.0
        self.input_size = (320, 320)
        self.test_size = (320, 320)
        self.multiscale_range = 5

        # Define yourself dataset path
        self.exp_name = "mimoquant_fine_tune"
        self.data_dir = f"datasets/{self.exp_name}"
        self.train_ann = "train.json"
        self.val_ann = "validation.json"
        self.test_ann = "test.json"

        # --------------  training config --------------------- #
        self.data_num_workers = 4
        self.warmup_epochs = 5
        self.max_epoch = 512
        self.eval_interval = 1
        self.warmup_lr = 0
        self.basic_lr_per_img = 0.01 / 64.0
        self.scheduler = "yoloxwarmcos"
        self.no_aug_epochs = 15
        self.min_lr_ratio = 0.05
        self.ema = True
        self.weight_decay = 5e-4
        self.momentum = 0.9
        self.save_history_ckpt = False

    # --------------- transform config ----------------- #
        self.hsv_prob = 0.1
        self.flip_prob = 0.4
        self.mixup_prob = 0
        self.degrees = 10.0
        self.translate = 0.1
        self.scale = (0.2, 2)
        self.mosaic_prob = 0.3
        self.mosaic_scale = (0.8, 1.6)
