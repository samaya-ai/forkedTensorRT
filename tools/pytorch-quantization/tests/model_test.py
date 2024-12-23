#
# SPDX-FileCopyrightText: Copyright (c) 1993-2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Tests of calibrators"""
import numpy as np

import torch

from pytorch_quantization import nn as quant_nn
from examples.torchvision.models.classification import *

np.random.seed(12345)
torch.manual_seed(12345)

# pylint:disable=missing-docstring, no-self-use


class TestExampleModels():

    def test_resnet50(self):
        model = resnet50(pretrained=True, quantize=True)
        model.eval()
        model.cuda()
        quant_nn.TensorQuantizer.use_fb_fake_quant = True
        dummy_input = torch.randn(1, 3, 224, 224, device='cuda')
        torch.onnx.export(model,
                          dummy_input,
                          "/tmp/resnet50.onnx",
                          verbose=False,
                          opset_version=13,
                          enable_onnx_checker=False,
                          do_constant_folding=True)
        quant_nn.TensorQuantizer.use_fb_fake_quant = False
