#  Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserve.
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
import unittest
import numpy as np

from op_test import OpTest
from test_softmax_op import stable_softmax


class TestSoftmaxWithCrossEntropyOp(OpTest):
    """
    Test softmax with cross entropy operator with discreate one-hot labels.
    """

    def setUp(self):
        self.op_type = "softmax_with_cross_entropy"
        batch_size = 2
        class_num = 37

        logits = np.random.uniform(0.1, 1.0,
                                   [batch_size, class_num]).astype("float64")
        softmax = np.apply_along_axis(stable_softmax, 1, logits)
        labels = np.random.randint(0, class_num, [batch_size, 1], dtype="int64")

        cross_entropy = np.asmatrix(
            [[-np.log(softmax[i][labels[i][0]])]
             for i in range(softmax.shape[0])],
            dtype="float64")

        self.inputs = {"Logits": logits, "Label": labels}
        self.outputs = {
            "Softmax": softmax.astype("float64"),
            "Loss": cross_entropy.astype("float64")
        }

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(["Logits"], "Loss")


class TestSoftmaxWithCrossEntropyOp2(OpTest):
    """
    Test softmax with cross entropy operator with soft labels.
    """

    def setUp(self):
        self.op_type = "softmax_with_cross_entropy"
        batch_size = 2
        class_num = 37

        logits = np.random.uniform(0.1, 1.0,
                                   [batch_size, class_num]).astype("float64")
        softmax = np.apply_along_axis(stable_softmax, 1, logits)
        labels = np.random.uniform(0.1, 1.0,
                                   [batch_size, class_num]).astype("float64")
        labels /= np.sum(labels, axis=1, keepdims=True)

        cross_entropy = (-labels * np.log(softmax)).sum(
            axis=1, keepdims=True).astype("float64")

        self.inputs = {"Logits": logits, "Label": labels}
        self.outputs = {
            "Softmax": softmax.astype("float64"),
            "Loss": cross_entropy.astype("float64")
        }
        self.attrs = {"soft_label": True}

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(["Logits"], "Loss")


if __name__ == "__main__":
    unittest.main()
