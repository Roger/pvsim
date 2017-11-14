# coding: utf-8


def time_to_fraction(hour, minute=0, second=0):
    """Returns the fraction of the day based on hour, minutes, seconds"""
    return ((hour * 3600 + minute * 60) + second) / (24 * 3600)


def date_to_fraction(date):
    return time_to_fraction(date.hour, date.minute, date.second)


SUNRISE = time_to_fraction(6, 0)
END_SUNRISE = time_to_fraction(8, 0)
CENIT = time_to_fraction(12, 39)
BEGIN_SUNDOWN = time_to_fraction(20, 0)
SUNDOWN = time_to_fraction(21, 0)

EFIC_LOW_LIGHT = 0.1
EFIC_STD = 0.92
KW_TOP = 3500


def calc_parabola_vertex(x1, y1, x2, y2, x3, y3):
    '''
    Adapted and modifed to get the unknowns for defining a parabola:
    http://stackoverflow.com/questions/717762/how-to-calculate-the-vertex-of-a-parabola-given-three-points
    '''

    denom = (x1 - x2) * (x1 - x3) * (x2 - x3)
    A = (x3 * (y2-y1) + x2 * (y1-y3) + x1 * (y3-y2)) / denom
    B = (x3 * x3 * (y1 - y2) +
         x2 * x2 * (y3 - y1) +
         x1 * x1 * (y2 - y3)) / denom
    C = (x2 * x3 * (x2 - x3) * y1 +
         x3 * x1 * (x3 - x1) * y2 +
         x1 * x2 * (x1 - x2) * y3) / denom

    return A, B, C


def start_rect(x):
    A = (EFIC_LOW_LIGHT * KW_TOP) / (END_SUNRISE - SUNRISE)
    B = A * SUNRISE * -1
    return A * x + B


def end_rect(x):
    A = ((-END_SUNRISE) * KW_TOP * EFIC_LOW_LIGHT) / (SUNDOWN - BEGIN_SUNDOWN)
    B = A * SUNDOWN * -1
    return A * x + B


PARABOLA_VERTEX = calc_parabola_vertex(
                    END_SUNRISE, start_rect(END_SUNRISE),
                    CENIT, (EFIC_STD * KW_TOP),
                    BEGIN_SUNDOWN, end_rect(BEGIN_SUNDOWN))


def parabola(x):
    (A, B, C) = PARABOLA_VERTEX
    return A * (x ** 2) + (B * x) + C


def calculate_pv_curve(date):
    """Calculate PV curve using a rect for SUNRISE
    a parabola for CENIT and another rect for SUNDOWN"""

    value = 0.0
    time = date_to_fraction(date)

    if time >= SUNRISE and time <= END_SUNRISE:
        value = start_rect(time)
    elif time > END_SUNRISE and time < BEGIN_SUNDOWN:
        value = parabola(time)
    elif time >= BEGIN_SUNDOWN and time <= SUNDOWN:
        value = end_rect(time)

    return value
