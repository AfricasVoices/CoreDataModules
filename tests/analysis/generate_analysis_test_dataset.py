import json
import uuid
from dataclasses import dataclass
from random import Random
from typing import List

from core_data_modules.analysis import AnalysisConfiguration
from core_data_modules.cleaners import Codes
from core_data_modules.data_models import Label, Origin, CodeScheme, CodeTypes
from core_data_modules.traced_data import TracedData, Metadata
from core_data_modules.util import TimeUtils

PARTICIPANT_UUID_FIELD = "participant_uuid"
CONSENT_WITHDRAWN_FIELD = "consent_withdrawn"


def _create_label(code, config):
    origin = Origin(Metadata.get_call_location(depth=2), "test", "External")
    label = Label(config.code_scheme.scheme_id, code.code_id, TimeUtils.utc_now_as_iso_string(), origin,
                  checked=True)
    return label


def _generate_column_td(random, rqa_configs, demographic_configs, na_configs=[]):
    """
    Generates a TracedData in column-format, representing either a message or a participant, by assigning random codes
    for the provided code schemes.

    Automatically assigns a random participant id, consent status, and labels.

    :param random: Random number generator to use. Providing a random number generator with the same seed will always
                   generate the same output.
    :type random: random.Random
    :param rqa_configs: RQA configurations to input between 1 and 3 random codes for.
    :type rqa_configs: list of AnalysisConfiguration
    :param demographic_configs: Demographic configurations to input a random code for.
    :type demographic_configs: list of AnalysisConfiguration
    :param na_configs: Configurations to assign the code 'NA'. For example, this can be used to set some datasets to
                       'NA' when creating a message.
    :type na_configs: list of AnalysisConfiguration
    """
    # 10 % chance of withdrawing consent
    consent_withdrawn = Codes.TRUE if random.random() > 0.9 else Codes.FALSE

    data = {
        PARTICIPANT_UUID_FIELD: f"participant-{uuid.uuid4()}",
        CONSENT_WITHDRAWN_FIELD: consent_withdrawn
    }

    if consent_withdrawn:
        for config in rqa_configs + demographic_configs:
            stop_code = config.code_scheme.get_code_with_control_code(Codes.STOP)
            label = _create_label(stop_code, config)
            data[config.coded_field] = [label.to_dict()]
            data[config.raw_field] = "STOP"

    # Assign a control code, or between 1 and 3 other codes for each rqa_config.
    for config in rqa_configs:
        data[config.coded_field] = []
        data[config.raw_field] = ""

        control = True if random.random() > 0.8 else False
        if control:
            control_codes = [c for c in config.code_scheme.codes if c.code_type == CodeTypes.CONTROL and c.control_code != Codes.STOP]
            code = random.choice(control_codes)
            label = _create_label(code, config)
            data[config.coded_field].append(label.to_dict())
            data[config.raw_field] += f"Synthetic raw text: {code.string_value}; "
        else:
            non_control_codes = [c for c in config.code_scheme.codes if c.code_type != CodeTypes.CONTROL]
            for i in range(random.choice([1, 2, 3])):
                code = random.choice(non_control_codes)
                label = _create_label(code, config)
                data[config.coded_field].append(label.to_dict())
                data[config.raw_field] += f"Synthetic raw text: {code.string_value}; "

    # Assign the code 'NA' to all the NA configs.
    for config in na_configs:
        na_code = config.code_scheme.get_code_with_control_code(Codes.TRUE_MISSING)
        data[config.coded_field] = _create_label(na_code, config).to_dict()
        data[config.raw_field] = ""

    # Select a single, random code for each demographic.
    for config in demographic_configs:
        non_stop_codes = [c for c in config.code_scheme.codes if c.control_code != Codes.STOP]
        code = random.choice(non_stop_codes)
        label = _create_label(code, config)
        data[config.coded_field] = [label.to_dict()]
        data[config.raw_field] = f"Synthetic raw text: {code.string_value}"

    return TracedData(data, Metadata("test", Metadata.get_call_location(), TimeUtils.utc_now_as_iso_string()))


def _generate_demographic_configs():
    with open("tests/analysis/resources/gender_code_scheme.json") as f:
        gender_scheme = CodeScheme.from_firebase_map(json.load(f))

    demographic_configs = [
        AnalysisConfiguration(dataset_name="gender", raw_field="gender_raw", coded_field="gender_coded",
                              code_scheme=gender_scheme)
    ]

    return demographic_configs


def _generate_rqa_configs():
    with open("tests/analysis/resources/s01e01_code_scheme.json") as f:
        s01e01_scheme = CodeScheme.from_firebase_map(json.load(f))
    with open("tests/analysis/resources/s01e02_code_scheme.json") as f:
        s01e02_scheme = CodeScheme.from_firebase_map(json.load(f))

    rqa_configs = [
        AnalysisConfiguration(dataset_name="s01e01", raw_field="s01e01_raw", coded_field="s01e01_coded",
                              code_scheme=s01e01_scheme),
        AnalysisConfiguration(dataset_name="s01e02", raw_field="s01e02_raw", coded_field="s01e02_coded",
                              code_scheme=s01e02_scheme)
    ]

    return rqa_configs


@dataclass
class SyntheticAnalysisData:
    PARTICIPANT_UUID_FIELD = PARTICIPANT_UUID_FIELD
    CONSENT_WITHDRAWN_FIELD = CONSENT_WITHDRAWN_FIELD

    participants: List[TracedData]
    messages: List[TracedData]
    rqa_configs: List[AnalysisConfiguration]
    demographic_configs: List[AnalysisConfiguration]


def generate_synthetic_analysis_data():
    """
    Generates synthetic analysis data for testing this project's automated analysis routines.

    Note that the messages and participants are each random and contain independent data.

    :return: Synthetic analysis data for testing automated analysis.
    :rtype: SyntheticAnalysisData
    """
    random = Random(0)
    rqa_configs = _generate_rqa_configs()
    demographic_configs = _generate_demographic_configs()

    # Generate 500 random participants
    participants = []
    for i in range(500):
        participants.append(_generate_column_td(random, rqa_configs, demographic_configs))

    # Generate 500 random messages for each RQA config
    messages = []
    for i in range(500):
        for rqa_config in rqa_configs:
            na_configs = [c for c in rqa_configs if c != rqa_config]
            messages.append(_generate_column_td(random, [rqa_config], demographic_configs, na_configs))

    return SyntheticAnalysisData(participants, messages, rqa_configs, demographic_configs)
