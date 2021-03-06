# UC Berkeley's Standard Copyright and Disclaimer Notice:
#
# Copyright (c) 2016. The Regents of the University of California (Regents). All
# Rights Reserved. Permission to use, copy, modify, and distribute this software
# and its documentation for educational, research, and not-for-profit purposes,
# without fee and without a signed licensing agreement, is hereby granted,
# provided that the above copyright notice, this paragraph and the following
# two paragraphs appear in all copies, modifications, and distributions.
# Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
# Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, for commercial licensing
# opportunities.
#
# Ronghang Hu, University of California, Berkeley.
#
# IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
# INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
# THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
# THE SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS
# PROVIDED "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT,
# UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
from __future__ import absolute_import, division, print_function

import numpy as np
import tensorflow as tf
from compact_bilinear_pooling import compact_bilinear_pooling_layer

def bp(bottom1, bottom2, sum_pool=True):
    assert(np.all(bottom1.shape[:3] == bottom2.shape[:3]))
    batch_size, height, width = bottom1.shape[:3]
    output_dim = bottom1.shape[-1] * bottom2.shape[-1]
    
    bottom1_flat = bottom1.reshape((-1, bottom1.shape[-1]))
    bottom2_flat = bottom2.reshape((-1, bottom2.shape[-1]))
    
    output = np.empty((batch_size*height*width, output_dim), np.float32)
    for n in range(len(output)):
        output[n, ...] = np.outer(bottom1_flat[n], bottom2_flat[n]).reshape(-1)
    output = output.reshape((batch_size, height, width, output_dim))
    
    if sum_pool:
        output = np.sum(output, axis=(1, 2))
    return output

# Input and output tensors
# Input channels need to be specified for shape inference
input_dim1 = 2048
input_dim2 = 2048
output_dim = 8000
bottom1 = tf.placeholder(tf.float32, [None, None, None, input_dim1])
bottom2 = tf.placeholder(tf.float32, [None, None, None, input_dim2])
top = compact_bilinear_pooling_layer(bottom1, bottom2, output_dim, sum_pool=True)
def cbp(bottom1_value, bottom2_value):
    sess = tf.get_default_session()
    return sess.run(top, feed_dict={bottom1: bottom1_value,
                                    bottom2: bottom2_value})

def run_kernel_approximation_test(batch_size, height, width):
    # Input values
    x = np.random.rand(batch_size, height, width, input_dim1).astype(np.float32)
    y = np.random.rand(batch_size, height, width, input_dim2).astype(np.float32)

    z = np.random.rand(batch_size, height, width, input_dim1).astype(np.float32)
    w = np.random.rand(batch_size, height, width, input_dim2).astype(np.float32)
    
    # Compact Bilinear Pooling results
    cbp_xy = cbp(x, y)
    cbp_zw = cbp(z, w)
    
    # (Original) Bilinear Pooling results
    bp_xy = bp(x, y)
    bp_zw = bp(z, w)

    # Check the kernel results of Compact Bilinear Pooling
    # against Bilinear Pooling
    cbp_kernel = np.sum(cbp_xy*cbp_zw, axis=1)
    bp_kernel = np.sum(bp_xy*bp_zw, axis=1)

    print("ratio between Compact Bilinear Pooling kernel and (original) Bilinear Pooling kernel:")
    print(cbp_kernel / bp_kernel)
    
def run_large_input_test(batch_size, height, width):
    # Input values
    x = np.random.rand(batch_size, height, width, input_dim1).astype(np.float32)
    y = np.random.rand(batch_size, height, width, input_dim2).astype(np.float32)
    
    # Compact Bilinear Pooling results
    cbp_xy = cbp(x, y)
    
def main():
    sess = tf.InteractiveSession()
    run_kernel_approximation_test(batch_size=2, height=3, width=4)
    run_large_input_test(batch_size=16, height=7, width=7)
    sess.close()
    
if __name__ == '__main__':
    main()