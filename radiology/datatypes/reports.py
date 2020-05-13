import re
import string
from typing import Dict

from datatypes.headers import ReportHeaders, DellHeaders


class Report:
    """
    Represents a radiology report as a collection
    of (optional) individual sections.
    """

    SOURCES = ["dell_labeled", "dell_unlabeled"]

    def __init__(self, id: str, sections: Dict[ReportHeaders, str], raw=None, source=None):
        # Identifier for Report
        self.id = id

        # Report Sections
        self.sections = sections
        self.raw = raw
        self.source = source

    def get(self, header: ReportHeaders) -> str:
        if header not in self.sections:
            return ""

        return self.sections[header]

    def has_section(self, header: ReportHeaders) -> bool:
        return self.get(header) != ""

    def __repr__(self):
        return "Report (%s)" % self.id


class DellReport(Report):
    def __init__(self, id: str, sections: Dict[ReportHeaders, str], raw: str = None, source: str = None):
        super().__init__(id, sections, raw, source)

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
                            sections[DellHeaders.COMPARISON] = \
                                split_report[i + 3].strip(string.whitespace).split("\n\n")[0]
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


if __name__ == "__main__":
    with open("data/labeled_neuro_reports/reports/2729232.txt") as f:
        for k, v in DellReport.from_raw(f.read()).items():
            print(k, v)
