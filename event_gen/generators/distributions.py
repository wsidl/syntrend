from event_gen.config import model

from random import random, betavariate


def dist_no_dist(prop_def: model.PropertyDefinition, gen_func: callable):
    return gen_func


def dist_linear(prop_def: model.PropertyDefinition, gen_func: callable):
    assert prop_def.type in {'integer', 'float'}, "Linear Distribution can only support numeric values"
    scale = prop_def.distribution.offset_max + prop_def.distribution.offset_min

    def _generator():
        return random() * scale + gen_func() + prop_def.distribution.offset_min

    return _generator


def dist_standard_deviation(prop_def: model.PropertyDefinition, gen_func: callable):
    assert prop_def.type in {'integer', 'float'}, "Standard Deviation Distribution can only support numeric values"
    dist_cfg = prop_def.distribution
    scale = dist_cfg.offset_max - dist_cfg.offset_min
    unscaled_variance = (float(dist_cfg.std_dev_factor) / scale) ** 2
    unscaled_mean = -dist_cfg.offset_min / scale
    t = unscaled_mean / (1 - unscaled_mean)
    beta = ((t / unscaled_variance) - (t * t) - (2 * t) - 1) / (
        (t * t * t) + (3 * t * t) + (3 * t) + 1
    )
    alpha = beta * t
    if alpha <= 0 or beta <= 0:
        raise ValueError("Cannot create value in Std Dev with given numbers")

    beta_var_factor = betavariate(alpha, beta) * scale + dist_cfg.std_dev_factor

    def _generator():
        return beta_var_factor * gen_func()

    return _generator


DISTRIBUTIONS = {
    model.DistributionTypes.NoDistribution: dist_no_dist,
    model.DistributionTypes.Linear: dist_linear,
    model.DistributionTypes.StdDev: dist_standard_deviation,
}


def get_distribution(prop_def: model.PropertyDefinition, gen_func: callable):
    return DISTRIBUTIONS[prop_def.distribution.type](prop_def, gen_func)
