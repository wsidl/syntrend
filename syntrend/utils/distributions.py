from syntrend.config import model

from random import randint, normalvariate


def dist_no_dist(_):
    def _generate(input_value):
        return input_value

    return _generate


def dist_linear(prop_dist: model.PropertyDistribution):
    def _generator(input_value):
        return input_value + randint(prop_dist.min_offset, prop_dist.max_offset)

    return _generator


def dist_standard_deviation(prop_dist: model.PropertyDistribution):
    # if prop_dist.min_offset >= prop_dist.max_offset:
    #     raise ValueError("min_offset must be less than max_offset")
    # scale = prop_dist.max_offset - prop_dist.min_offset
    # unscaled_variance = (float(prop_dist.std_dev_factor) / scale) ** 2
    # unscaled_mean = -prop_dist.min_offset / scale
    # t = unscaled_mean / (1 - unscaled_mean)
    # beta = ((t / unscaled_variance) - (t * t) - (2 * t) - 1) / (
    #     (t * t * t) + (3 * t * t) + (3 * t) + 1
    # )
    # alpha = beta * t
    # if alpha <= 0 or beta <= 0:
    #     raise ValueError("Cannot create value in Std Dev with given numbers", alpha, beta)

    def _generator(input_value):
        return normalvariate(input_value, float(prop_dist.std_dev_factor))

    return _generator


DISTRIBUTIONS = {
    model.DistributionTypes.NoDistribution: dist_no_dist,
    model.DistributionTypes.Linear: dist_linear,
    model.DistributionTypes.StdDev: dist_standard_deviation,
}


def get_distribution(prop_def: model.PropertyDistribution):
    return DISTRIBUTIONS[prop_def.type](prop_def)
