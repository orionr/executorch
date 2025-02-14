# Copyright (c) Qualcomm Innovation Center, Inc.
# All rights reserved
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
from typing import Dict

import executorch.backends.qualcomm.python.PyQnnWrapperAdaptor as PyQnnWrapper

import torch

from .node_visitor import NodeVisitor, register_node_visitor


@register_node_visitor
class Arange(NodeVisitor):
    target = ["aten.arange.start_step"]

    def __init__(self, *args) -> None:
        super().__init__(*args)

    def define_node(
        self,
        node: torch.fx.Node,
        nodes_to_wrappers: Dict[torch.fx.Node, PyQnnWrapper.TensorWrapper],
    ) -> PyQnnWrapper.PyQnnOpWrapper:
        start, end = node.args[0:2]
        step = node.args[2] if len(node.args) > 2 else 1
        out_tensor = torch.arange(start, end, step)

        # since we can derive the constant value of current op in AoT stage
        # we only build static tensor here for consumers of current node
        # to correctly reference the data
        self.define_tensor(
            node,
            node,
            out_tensor,
            PyQnnWrapper.Qnn_TensorType_t.QNN_TENSOR_TYPE_STATIC,
            nodes_to_wrappers,
        )
