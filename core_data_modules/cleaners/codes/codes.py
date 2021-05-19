class Codes(object):
    # Demographic codes
    MAN = "man"
    WOMAN = "woman"

    YES = "yes"
    NO = "no"
    AMBIVALENT = "ambivalent"

    URBAN = "urban"
    RURAL = "rural"

    # Pipeline support codes
    TRUE = "true"
    FALSE = "false"

    MATRIX_0 = "0"
    MATRIX_1 = "1"

    # Control Codes
    STOP = "STOP"
    DELETED = "DELETED"
    TRUE_MISSING = "NA"
    SKIPPED = "NS"
    NOT_INTERNALLY_CONSISTENT = "NIC"
    CODING_ERROR = "CE"
    NOT_REVIEWED = "NR"
    NOT_CODED = "NC"
    WRONG_SCHEME = "WS"
    NOISE_OTHER_CHANNEL = "NOC"

    CONTROL_CODES = {
        STOP, DELETED, TRUE_MISSING, SKIPPED, NOT_INTERNALLY_CONSISTENT, CODING_ERROR, NOT_REVIEWED, NOT_CODED,
        WRONG_SCHEME, NOISE_OTHER_CHANNEL
    }

    # Meta Codes
    PUSH_BACK = "push_back"
    SHOWTIME_QUESTION = "showtime_question"
    QUESTION = "question"
    GREETING = "greeting"
    OPT_IN = "opt_in"
    SIMILAR_CONTENT = "similar_content"
    PARTICIPATION_INCENTIVE = "participation_incentive"
