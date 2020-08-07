from datetime import datetime
from urllib.parse import urlparse

from dateutil.parser import isoparse


def validate_string(s, variable_name=""):
    assert isinstance(s, str), "{} not a string".format(variable_name)
    assert s != "", "{} is empty".format(variable_name)
    return s


def validate_int(i, variable_name=""):
    assert isinstance(i, int), "{} not an int".format(variable_name)
    return i


def validate_double(d, variable_name=""):
    assert isinstance(d, float), "{} not a double".format(variable_name)
    return d


def validate_bool(b, variable_name=""):
    assert isinstance(b, bool), "{} not a bool".format(variable_name)
    return b


def validate_list(l, variable_name=""):
    assert isinstance(l, list), "{} not a list".format(variable_name)
    return l


def validate_dict(d, variable_name=""):
    assert isinstance(d, dict), "{} not a dict".format(variable_name)
    return d


def validate_datetime(dt, variable_name=""):
    assert isinstance(dt, datetime), "{} not a datetime".format(variable_name)
    assert dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None, "{} not timezone-aware".format(variable_name)
    return dt


def validate_iso_string(s, variable_name=""):
    validate_string(s, variable_name)
    try:
        isoparse(s)
    except:
        assert False, "{} not an ISO string".format(variable_name)
    return s


def validate_utc_iso_string(s, variable_name=""):
    validate_iso_string(s, variable_name)
    assert s.endswith("Z") or s.endswith("+00:00"), "{} not a UTC ISO string".format(variable_name)
    return s


def validate_url(s, variable_name="", scheme=None):
    validate_string(s, variable_name)

    try:
        parsed_url = urlparse(s)
    except:
        assert False, f"{variable_name} not a valid URL"

    if scheme is not None:
        assert parsed_url.scheme == scheme, f"{variable_name} not a URL with scheme {scheme}"

    return s
