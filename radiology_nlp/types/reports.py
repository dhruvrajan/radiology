import re
from enum import Enum, auto
import string
from typing import Dict


class ReportHeaders(Enum):
    """
    Enumeration of headers found in radiology reports.
    """
    # COMPARISON = auto()
    # COMPARISON_DATED = auto()
    # COMPARISON_STUDY = auto()
    
    PROCEDURE_AND_FINDINGS = auto()
    PROCEDURE = auto()
    FINDINGS = auto()

    CLINICAL_INDICATION = auto()
    CONCLUSION = auto()

    REPORT = auto()
    HISTORY = auto()
    IMPRESSION = auto()
    NARRATIVE = auto()

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

    def __init__(self, id: str, original: str, findings: str = "", procedure: str = "", impression: str = "",
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
        self.original = original

    def __repr__(self):
        return "Report( {} )".format(self.id)

    @staticmethod
    def from_sections(id, original, sections: Dict[ReportHeaders, str]):
        report = Report(id, original)
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
            # elif key == ReportHeaders.COMPARISON:
                # report.comparison = sections[key]
            elif key == ReportHeaders.RESULT:
                report.result = sections[key]
        return report


def make_report_header_delimiter():
    def optional_case(word: str):
        return "".join(["[" + c.lower() + c.upper() + "]" if c.isalnum() else r"\s" if c == " " else c for c in word]) + "[:\n]\s*"

    names = ReportHeaders.header_names().keys()
    return "(" + "|".join(list(map(lambda name: optional_case(name) + ":?", names))) + ")"


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
            section_type = header_names[match.group(0).lower().strip().strip(string.punctuation)]
            section_text = ""
            if not re.match(delimiter, split_report[i + 1]):
                section_text = split_report[i + 1].strip(string.whitespace)

            sections[section_type] = section_text

    return Report.from_sections(id, raw_report, sections)
    

if __name__ == "__main__":
    delimiter = make_report_header_delimiter()
    print(delimiter)
    print(re.match("([Pp]rocedure\sand\sFindings)",
                   "Procedure and Findings: a dog in the bathtub"))
