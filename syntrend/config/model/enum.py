from enum import Enum


class DistributionTypes(Enum):
    NoDistribution = 'none'
    Linear = 'linear'
    StandardDeviation = 'std_dev'


class Progress(Enum):
    Trend = 'trend'
    Last = 'last'
