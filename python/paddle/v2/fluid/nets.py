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
import layers

__all__ = [
    "simple_img_conv_pool",
    "sequence_conv_pool",
    "glu",
]


def simple_img_conv_pool(input,
                         num_filters,
                         filter_size,
                         pool_size,
                         pool_stride,
                         act,
                         param_attr=None,
                         pool_type='max'):
    conv_out = layers.conv2d(
        input=input,
        num_filters=num_filters,
        filter_size=filter_size,
        param_attr=param_attr,
        act=act)

    pool_out = layers.pool2d(
        input=conv_out,
        pool_size=pool_size,
        pool_type=pool_type,
        pool_stride=pool_stride)
    return pool_out


def img_conv_group(input,
                   conv_num_filter,
                   pool_size,
                   conv_padding=1,
                   conv_filter_size=3,
                   conv_act=None,
                   param_attr=None,
                   conv_with_batchnorm=False,
                   conv_batchnorm_drop_rate=None,
                   pool_stride=1,
                   pool_type=None):
    """
    Image Convolution Group, Used for vgg net.
    """
    tmp = input
    assert isinstance(conv_num_filter, list) or \
        isinstance(conv_num_filter, tuple)

    def __extend_list__(obj):
        if not hasattr(obj, '__len__'):
            return [obj] * len(conv_num_filter)
        else:
            return obj

    conv_padding = __extend_list__(conv_padding)
    conv_filter_size = __extend_list__(conv_filter_size)
    param_attr = __extend_list__(param_attr)
    conv_with_batchnorm = __extend_list__(conv_with_batchnorm)
    conv_batchnorm_drop_rate = __extend_list__(conv_batchnorm_drop_rate)

    for i in xrange(len(conv_num_filter)):
        local_conv_act = conv_act
        if conv_with_batchnorm[i]:
            local_conv_act = None

        tmp = layers.conv2d(
            input=tmp,
            num_filters=conv_num_filter[i],
            filter_size=conv_filter_size[i],
            padding=conv_padding[i],
            param_attr=param_attr[i],
            act=local_conv_act)

        if conv_with_batchnorm[i]:
            tmp = layers.batch_norm(input=tmp, act=conv_act)
            drop_rate = conv_batchnorm_drop_rate[i]
            if abs(drop_rate) > 1e-5:
                tmp = layers.dropout(x=tmp, dropout_prob=drop_rate)

    pool_out = layers.pool2d(
        input=tmp,
        pool_size=pool_size,
        pool_type=pool_type,
        pool_stride=pool_stride)
    return pool_out


def sequence_conv_pool(input,
                       num_filters,
                       filter_size,
                       param_attr=None,
                       act="sigmoid",
                       pool_type="max"):
    conv_out = layers.sequence_conv(
        input=input,
        num_filters=num_filters,
        filter_size=filter_size,
        param_attr=param_attr,
        act=act)

    pool_out = layers.sequence_pool(input=conv_out, pool_type=pool_type)
    return pool_out


def glu(input, dim=-1):
    """
    The gated linear unit composed by split, sigmoid activation and elementwise 
    multiplication. Specifically, Split the input into two equal sized parts 
    :math:`a` and :math:`b` along the given dimension and then compute as 
    following:

        .. math::

            {GLU}(a, b)= a \otimes \sigma(b)

    Refer to `Language Modeling with Gated Convolutional Networks 
    <https://arxiv.org/pdf/1612.08083.pdf>`_.
    
    Args:
        input (Variable): The input variable which is a Tensor or LoDTensor.
        dim (int): The dimension along which to split. If :math:`dim < 0`, the 
            dimension to split along is :math:`rank(input) + dim`.

    Returns:
        Variable: The Tensor variable with half the size of input.

    Examples:
        .. code-block:: python

            # x is a Tensor variable with shape [3, 6, 9]
            fluid.nets.glu(input=x, dim=1)  # shape of output: [3, 3, 9]
    """

    a, b = layers.split(input, num_or_sections=2, dim=dim)
    act_b = layers.sigmoid(x=b)
    out = layers.elementwise_mul(x=a, y=act_b)
    return out
