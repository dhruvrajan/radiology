import re
from enum import Enum, auto
import string
from typing import Dict


class ReportHeaders(Enum):
    @classmethod
    def header_names(cls):
        """
        Retrieves a list of header names as strings
        (as they would appear in a text report).
        """
        return dict(map(lambda header: (re.sub("_", " ", header.name.lower()), header), cls))


class DellHeaders(ReportHeaders):
    """
    Enumeration of headers found in radiology reports.
    """
    COMPARISON = auto()
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

    @staticmethod
    def optional_case(word: str):
        return "".join(["[" + c.lower() + c.upper() + "]" if c.isalnum()
                        else r"\s" if c == " " else c for c in word]) + "[:\n]\s*"

    @staticmethod
    def make_delimiter():

        names = DellHeaders.header_names().keys()
        return "(" + "|".join(list(map(lambda name: DellHeaders.optional_case(name) + ":?", names))) + ")"

    @staticmethod
    def from_raw(raw_report: str) -> Dict[ReportHeaders, str]:
        header_names = DellHeaders.header_names()
        delimiter = DellHeaders.make_delimiter()

        split_report = re.split(delimiter, raw_report)
        sections = dict()
        for i, section in enumerate(split_report):
            match = re.match(delimiter, section.strip())
            if match:
                section_type = header_names[match.group(
                    0).lower().strip().strip(string.punctuation)]
                section_text = ""
                if not re.match(delimiter, split_report[i + 1]):
                    section_text = split_report[i + 1].strip(string.whitespace)

                if section_type == DellHeaders.PROCEDURE_AND_FINDINGS:
                    try:
                        comp_delim = DellHeaders.optional_case("comparison")
                        if re.match(comp_delim, split_report[i + 2]):
                            sections[DellHeaders.PROCEDURE] = section_text
                            sections[DellHeaders.COMPARISON] = split_report[i + 3].strip(string.whitespace).split("\n\n")[0]
                            sections[DellHeaders.FINDINGS] = "\n\n".join(
                                split_report[i + 3].strip(string.whitespace).split("\n\n")[1:])
                            i += 3
                        else:
                            sections[DellHeaders.PROCEDURE] = section_text.split("\n\n")[
                                0]
                            sections[DellHeaders.FINDINGS] = "\n\n".join(
                                section_text.split("\n\n")[1:])
                            i += 2
                    except:
                        pass
                else:
                    sections[section_type] = section_text
                i += 1

        return sections


class Report:
    """
    Represents a radiology report as a collection
    of (optional) individual sections.
    """

    def __init__(self, id: str, sections: Dict[ReportHeaders, str], raw=None):
        # Identifier for Report
        self.id = id

        # Report Sections
        self.sections = sections

        self.raw = raw

    def get(self, header: ReportHeaders):
        if header not in self.sections:
            return ""

        return self.sections[header]

    def __repr__(self):
        return "Report (%s)" % self.id


if __name__ == "__main__":
    with open("data/labeled_neuro_reports/reports/2729232.txt") as f:
        for k, v in DellHeaders.from_raw(f.read()).items():
            print(k, v)
