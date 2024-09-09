import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import sys
from typing import Callable
from functools import partial

T_IMG = tuple[float, float, float]


def smooth1d(x, window_len):
    s = np.r_[2*x[0] - x[window_len:1:-1], x, 2*x[-1] - x[-1:-window_len:-1]]
    w = np.hanning(window_len)
    y = np.convolve(w/w.sum(), s, mode='same')
    return y[window_len-1:-window_len+1]


def gaussian_filter(sigma: float, alpha: float = 0.5, color: T_IMG = (0., 0., 0.)) -> Callable[[T_IMG, float], tuple[T_IMG, float, float]]:

    def _run_filter(image: T_IMG, dpi: float) -> tuple[T_IMG, float, float]:
        pad = int(sigma * 3 / 72. * dpi)
        padded_src = np.pad(image, [(pad, pad), (pad, pad), (0, 0)], "constant")
        target_image = np.empty_like(padded_src)
        target_image[:, :, :3] = color

        scaled_sigma = sigma / 72. * dpi
        alpha_src = padded_src[:, :, -1] * alpha
        window_len = max(int(scaled_sigma), 3) * 2 + 1
        alpha_src = np.apply_along_axis(smooth1d, 0, alpha_src, window_len)
        # alpha_src = np.apply_along_axis(smooth1d, 1, alpha_src, int(window_len / 10))
        ratio = alpha / np.max(alpha_src)
        target_image[:, :, 3] = alpha_src * ratio

        # margin = pad * .1
        # inner_pad = int(pad - margin)
        # target_image = target_image[inner_pad:-inner_pad, inner_pad:-inner_pad]
        return target_image, -pad, -pad

    return _run_filter


def apply_gaussian_blur(plot: plt.Axes, sigma: float, alpha: float, **kwargs):
    l, = plot.get_lines()
    yy = l.get_ydata()
    gauss = gaussian_filter(sigma=sigma, alpha=alpha, color=colors.to_rgb(kwargs['color']))
    line, = plot.plot(l.get_xdata(), yy)
    line.update_from(l)
    line.set_agg_filter(gauss)
    line.set_rasterized(True)
    line.update(kwargs)


GRAPH_TYPE = ''
X = np.linspace(0, 29, 30)
X_TREND = np.array([5.0] * 30)
Y = {
    'none': [5.0] * 30,
    'linear': [
        3.4286597355069164, 2.759552727927165, 5.139106683692621, 7.846772286339835, 4.370221795766835, 6.163291543687663, 5.760275442542536, 4.883550131468994, 7.958263680754884, 2.4737366106868652, 8.50466700352673, 5.8691653857392545, 7.880160966544324, 7.9982299762617295, 7.463460637918457, 3.9290881421875508, 8.894258971032642, 8.955755609952814, 4.288907058893064, 5.388089616412426, 6.559485074178385, 6.496753657232439, 9.881486962248243, 6.2532589849034395, 5.245457904462363, 7.730317837887085, 7.8299044838888285, 4.727513065234957, 5.19795733463555, 3.757641452375263
    ],
    'std_dev': [
        6.539895504932106, 5.864296778185984, 6.58124836310444, 1.5985193382969385, 4.711970924784011, 6.6513144302880285, 2.9541544268680777, 5.483990056762898, 5.772204523194729, 6.058900154473583, 0.5072872916252509, 5.512192691464881, 7.172460636216519, 6.672910636744286, 7.338767339760278, 5.735282162631125, 7.269013928563343, 6.961476081597453, 4.439704547471921, 1.6496701535925196, 0.9593543409724301, 1.9368649803801063, 6.9704527608035995, 4.686448324720903, 6.289802586590157, 3.3627063781552518, 4.038932129681856, 6.035254516582815, 6.281155903537542, 6.675274226713796
    ],
}
AREA = {
    'none': lambda plot: None,
    'linear': lambda plot: partial(plot.fill_between, X, y1=X_TREND + 5, y2=X_TREND - 3, alpha=0.2),
    'std_dev': lambda plot: partial(apply_gaussian_blur, plot, alpha=0.2, sigma=70),
}

def draw_value_diagram(plot: plt.Axes):
    values = np.array(Y[GRAPH_TYPE])
    plot.tick_params(axis='y', left=False, labelleft=False)
    plot.grid()
    trend_line, = plot.plot(X, X_TREND, color='blue', label='Trend Expression')
    dist_area = AREA[GRAPH_TYPE](plot)
    if dist_area:
        r = dist_area(label='Area of Distribution', color=trend_line.get_color())
    plot.plot(X, values, 'o', color='green', label='Generated Values')
    plot.set_ylim((-5, 15))
    plot.legend(loc='best', fancybox=True)


DIST_BIN_SIZE = 0.01
ALPHA = 2
DIST_GRAPH = {
    'none': lambda: np.array([100 if i * DIST_BIN_SIZE == 5 else 0 for i in range(0, int(10 / DIST_BIN_SIZE))]),
    'linear': lambda: np.array([100 if 2 <= i * DIST_BIN_SIZE <= 10 else 0 for i in range(0, int(10 / DIST_BIN_SIZE))]),
    'std_dev': lambda: 1.0 / (np.sqrt(2.0 * np.pi) * 2.) * np.exp(-np.power((np.arange(0., 10., DIST_BIN_SIZE) - 5.) / 2., 2.0) / 2)
}


def draw_distribution_graph(plot: plt.Axes):
    plot.set_title('Dist @ 0')
    plot.tick_params(axis='y', bottom=False, labelbottom=False)
    plot.grid()
    plot.fill_betweenx(np.arange(0., 10., DIST_BIN_SIZE), DIST_GRAPH[GRAPH_TYPE](), 0, color='blue', alpha=0.2)
    plot.axhline(5, color='blue')


def draw_plot():
    fig = plt.figure(figsize=(6, 3))
    grid_spec = fig.add_gridspec(1, 2, width_ratios=(1, 4), left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.05)
    pl_trend = fig.add_subplot(grid_spec[0, 1])
    pl_dist = fig.add_subplot(grid_spec[0, 0], sharey=pl_trend)
    draw_value_diagram(pl_trend)
    draw_distribution_graph(pl_dist)
    fig.show()


def none():
    global GRAPH_TYPE
    GRAPH_TYPE = 'none'
    draw_plot()


def linear():
    global GRAPH_TYPE
    GRAPH_TYPE = 'linear'
    draw_plot()


def std_dev():
    global GRAPH_TYPE
    GRAPH_TYPE = 'std_dev'
    draw_plot()
#
#
# if __name__ == '__main__':
#     print("Plot Call", sys.argv)
#     cmd, GRAPH_TYPE = sys.argv
#     draw_plot()
