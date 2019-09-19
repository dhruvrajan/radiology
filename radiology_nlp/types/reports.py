import re
from enum import Enum, auto
import string
from typing import Dict


class ReportHeaders(Enum):
    """
    Enumeration of headers found in radiology reports.
    """
    COMPARISON = auto()
    COMPARISON_DATED = auto()
    FINDINGS = auto()
    HISTORY = auto()
    IMPRESSION = auto()
    NARRATIVE = auto()
    PROCEDURE = auto()
    PROCEDURE_AND_FINDINGS = auto
    RESULT = auto()
    TECHNIQUE = auto()

    @classmethod
    def header_names(cls):
        """
        Retrieves a list of header names as strings
        (as they would appear in a text report).
        """
        return dict(map(lambda header: (re.sub("_", " ", header.name.lower()), header), ReportHeaders))


class Report:
    """
    Represents a radiology report as a collection
    of (optional) individual sections.
    """

    def __init__(self, id: str, findings: str = "", procedure: str = "", impression: str = "",
                 technique: str = "", history: str = "", comparison: str = "", result: str = ""):

        # Identifier for Report
        self.id = id

        # Report Sections
        self.findings = findings
        self.procedure = procedure
        self.impression = impression
        self.technique = technique
        self.history = history
        self.comparison = comparison
        self.result = result

    def __repr__(self):
        return "Report( {} )".format(self.id)

    @staticmethod
    def from_sections(id, sections: Dict[ReportHeaders, str]):
        report = Report(id)
        for key in sections:
            if key == ReportHeaders.FINDINGS:
                report.findings = sections[key]
            elif key == ReportHeaders.PROCEDURE:
                report.procedure = sections[key]
            elif key == ReportHeaders.IMPRESSION:
                report.impression = sections[key]
            elif key == ReportHeaders.TECHNIQUE:
                report.technique = sections[key]
            elif key == ReportHeaders.HISTORY:
                report.history = sections[key]
            elif key == ReportHeaders.COMPARISON:
                report.comparison = sections[key]
            elif key == ReportHeaders.RESULT:
                report.result = sections[key]
        return report


def make_report_header_delimiter():
    def optional_case(word: str):
        return "".join(["[" + c.lower() + c.upper() + "]" if c.isalnum() else c for c in word])

    names = ReportHeaders.header_names().keys()
    return "(" + "|".join(list(map(lambda name: optional_case(re.sub(" ", "\s", name)), names))) + ")" + ":?"


def raw_to_report(id, raw_report: str) -> Report:
    """
    From raw report text, splits headers and constructs
    a Report object.
    """
    header_names = ReportHeaders.header_names()
    delimiter = make_report_header_delimiter()

    split_report = re.split(delimiter, raw_report)
    sections = dict()

    for i, section in enumerate(split_report):
        match = re.match(delimiter, section.strip())
        if match:
            section_type = header_names[match.group(0).lower()]

            section_text = ""
            if not re.match(delimiter, split_report[i + 1]):
                section_text = split_report[i + 1].strip(string.whitespace)
            sections[section_type] = section_text

    result = Report.from_sections(id, sections)
    return result


if __name__ == "__main__":
    # print(re.match("finding[sS]", "finding,").group(0))
    # delimeter = make_report_header_delimiter()
    # with open("../dell_medical_data/labeled_neuro_reports/reports/4943027.txt") as f:
    # report = raw_to_report("1", f.read())
    pass