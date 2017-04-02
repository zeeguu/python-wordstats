import math


def compute_frequency(occurrence_count):
    """

        frequency is too coarse.
         taking the log from it is going
         to smooth it somehow

    :param occurrence_count:
    :return:
    """
    return round(math.log(occurrence_count), 2)


def compute_difficulty(rank):
    """

        normalized between 0 and 1
         the difficulty increases in steps of 0.01
         for every 500 ranks
         assumes a frequency list of 50K words

    :param rank:
    :return:
    """
    return rank // 500 / 100.0


def compute_importance(occurrence_count):
    """

        need a better way to think about
        this... but for now we go with
        log of occurrence count

    :param occurrence_count:
    :return:
    """
    return round(math.log(occurrence_count), 2)


def compute_klevel(rank):
    """

        assumes a frequency list of 50K words

    :param rank:
    :return:
    """
    return (rank // 1000) + 1