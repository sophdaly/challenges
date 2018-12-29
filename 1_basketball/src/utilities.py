"""
Utility Methods
"""


def add_info_a(field):
    return _split_info(field=field, order=0)


def add_info_b(field):
    return _split_info(field=field, order=1)


def _split_info(field, order):
    return field.split(' - ')[order]
