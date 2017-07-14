import os
import unittest

import numpy as np
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt

import pygco
PLOT_SIZE = 6


# def get_uniform_smoothness_pw_single_image(img):
#     """
#     Generate uniform smoothness pairwise potential for a single image of size
#     img. Pixel indices are assumed to be in row-major order.
#     In a uniform smoothness pairwse potential, for any pair of neighboring
#     pixels i and j, p(i,j) = 1
#     img: a tuple of two integers H,W for height and width of the image
#     return: edges, edge_weights
#         edges is a E*2 matrix, E is the number of edges in the grid graph.
#             For 4-connected graphs, E=(H-1)*W + H*(W-1). Each row is a pair of
#             pixel indices for an edge
#         edge_weights is a E-dimensional vector of 1's.
#
#     see: https://github.com/kelvinxu/Segmentation-Code/blob/master/imgtools/pairwise.py
#     """
#     H, W = img
#     E = (H - 1) * W + H * (W - 1)
#
#     edges = np.empty((E, 2), dtype=np.int)
#     edge_weights = np.ones(E, dtype=np.single)
#     idx = 0
#
#     # horizontal edges
#     for row in range(H):
#         edges[idx:idx+W-1,0] = np.arange(W-1) + row * W
#         edges[idx:idx+W-1,1] = np.arange(W-1) + row * W + 1
#         idx += W-1
#
#     # vertical edges
#     for col in range(W):
#         edges[idx:idx+H-1,0] = np.arange(0, (H-1)*W, W) + col
#         edges[idx:idx+H-1,1] = np.arange(W, H*W, W) + col
#         idx += H-1
#
#     return [edges, edge_weights]




def test_gc():
    """  """
    gc = pygco.gco()
    gc.createGeneralGraph(3, 2, True)
    gc.handle is not None
    gc.destroy_graph()


def test_integer():
    """  """
    unary = np.array([[2, 8, 8],
                      [7, 3, 7],
                      [8, 8, 2],
                      [6, 4, 6]])
    edges = np.array([[0, 1], [1, 2], [2, 3]])
    edge_weight = np.array([3, 10, 1])
    smooth = 1 - np.eye(3)

    labels = pygco.cut_general_graph(edges, edge_weight, unary, smooth,
                                     n_iter=1)
    assert np.array_equal(labels, np.array([0, 2, 2, 1]))


def test_float():
    """  """
    unary = np.array([[0.0, 1.0, 2.0],
                      [4.0, 1.0, 0.0],
                      [1.0, 0.0, 2.0]])
    edges = np.array([[0, 1],
                      [1, 2],
                      [0, 2]]).astype(np.int32)
    smooth = (1 - np.eye(3)).astype(np.float)
    edge_weights = np.array([2.0, 0.0, 0.0])

    labels = pygco.cut_general_graph(edges, edge_weights, unary, smooth,
                                     n_iter=-1, algorithm="swap")
    assert np.array_equal(labels, np.array([0, 2, 1]))


def test_grid():
    """  """
    annot = np.zeros((100, 100))
    annot[:, 60:] = 2
    annot[15:65, 35:85] = 1

    np.random.seed(0)
    noise = annot + np.random.randn(*annot.shape)

    unary = np.tile(noise[:, :, np.newaxis], [1, 1, 3])

    tmp = (unary[:, :, 1] - 1)
    tmp[annot == 0] *= -1
    unary[:, :, 1] = tmp
    unary[:, :, 2] = 2 - unary[:, :, 2]

    fig, axarr = plt.subplots(ncols=unary.shape[-1],
                              figsize=(unary.shape[-1] * PLOT_SIZE, PLOT_SIZE))
    for i in range(unary.shape[-1]):
        axarr[i].set_title('unary term #%i' % i)
        bm = axarr[i].imshow(unary[:, :, i], cmap='gray',
                             interpolation='nearest')
        plt.colorbar(bm, ax=axarr[i])  # , plt.contour(annot, colors='r')

    fig.tight_layout()
    fig.savefig('./images/grid_unary.png')

    pairwise = (1 - np.eye(3)) * 10
    labels = pygco.cut_grid_graph_simple(unary, pairwise, n_iter=-1)

    fig, axarr = plt.subplots(ncols=2, figsize=(2 * PLOT_SIZE, PLOT_SIZE))
    axarr[0].set_title('original annotation')
    axarr[0].imshow(annot, interpolation="nearest")
    axarr[1].set_title('resulting labeling')
    axarr[1].imshow(labels.reshape(*annot.shape), interpolation="nearest")
    axarr[1].contour(annot, colors='w')
    fig.tight_layout()
    fig.savefig('./images/grid_labels.png'), plt.close()


def test_binary():
    """  """
    annot = np.zeros((100, 100))
    annot[20:70, 30:80] = 1
    np.random.seed(0)
    img = np.random.randn(*annot.shape)
    img += 2 * annot - 1

    # !!! Be careful when doing this concatenation,
    # it seems 'c_' does not create a copy
    # u = np.c_[img.flatten().copy(), - img.flatten().copy()]

    unary = np.tile(img[:, :, np.newaxis], [1, 1, 2])
    unary[:, :, 0] = img
    unary[:, :, 1] = -img
    unary += 4

    fig, axarr = plt.subplots(ncols=unary.shape[-1],
                              figsize=(unary.shape[-1] * PLOT_SIZE, PLOT_SIZE))
    for i in range(unary.shape[-1]):
        axarr[i].set_title('unary term #%i' % i)
        bm = axarr[i].imshow(unary[:, :, i], cmap='gray', interpolation='nearest')
        plt.colorbar(bm, ax=axarr[i])  # , plt.contour(annot, colors='r')
    fig.tight_layout()
    fig.savefig('./images/binary_unary.png')

    # edges, edge_weights = get_uniform_smoothness_pw_single_image(img.shape)
    smooth = 1 - np.eye(2)

    # y = pygco.cut_grid_graph_simple(unary, pw_cost*0, n_iter=-1)
    # labels = pygco.cut_grid_graph_simple(unary_new + np.random.
    #   randn(unary.shape[0], unary.shape[1], unary.shape[2])*0,
    #   pw_cost*0, n_iter=-1)

    labels = pygco.cut_grid_graph_simple(unary, smooth, n_iter=-1)
    labels_0 = pygco.cut_grid_graph_simple(unary, smooth * 0., n_iter=-1)

    fig, axarr = plt.subplots(ncols=3, figsize=(3 * PLOT_SIZE, PLOT_SIZE))
    axarr[0].set_title('image')
    axarr[0].imshow(img, cmap='gray', interpolation='nearest')
    axarr[0].contour(annot, colors='r')
    axarr[1].set_title('labeling (smooth=1)')
    axarr[1].imshow(labels.reshape(*annot.shape), interpolation='nearest')
    axarr[1].contour(annot, colors='w')
    axarr[2].set_title('labeling (smooth=0)')
    axarr[2].imshow(labels_0.reshape(*annot.shape), interpolation='nearest')
    axarr[2].contour(annot, colors='w')
    fig.tight_layout()
    fig.savefig('./images/binary_labels-4conn.png'), plt.close()

    labels = pygco.cut_grid_graph_simple(unary, smooth, connect=8, n_iter=-1)
    labels_0 = pygco.cut_grid_graph_simple(unary, smooth * 0., connect=8, n_iter=-1)

    fig, axarr = plt.subplots(ncols=3, figsize=(3 * PLOT_SIZE, PLOT_SIZE))
    axarr[0].set_title('image')
    axarr[0].imshow(img, cmap='gray', interpolation='nearest')
    axarr[0].contour(annot, colors='r')
    axarr[1].set_title('labeling (smooth=1)')
    axarr[1].imshow(labels.reshape(*annot.shape), interpolation='nearest')
    axarr[1].contour(annot, colors='w')
    axarr[2].set_title('labeling (smooth=0)')
    axarr[2].imshow(labels_0.reshape(*annot.shape), interpolation='nearest')
    axarr[2].contour(annot, colors='w')
    fig.tight_layout()
    fig.savefig('./images/binary_labels-8conn.png'), plt.close()


class TestGCO(unittest.TestCase):

    def test_all(self):
        test_gc()
        test_integer()
        test_float()
        test_binary()
        test_grid()


if __name__ == "__main__":
    unittest.main()

    if not os.path.exists('images'):
        os.mkdir('images')
    test_binary()
    test_grid()
