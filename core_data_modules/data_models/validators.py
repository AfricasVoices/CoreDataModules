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


def validate_url(s, validate_scheme=None, variable_name=""):
    validate_string(s, variable_name)

    try:
        parsed_url = urlparse(s)
    except:
        assert False, f"{variable_name} not a valid URL"

    if validate_scheme is not None:
        assert parsed_url.scheme == validate_scheme, f"{variable_name} not a URL with scheme {validate_scheme}"

    return s
