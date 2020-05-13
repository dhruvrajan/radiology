import re
from enum import Enum, auto


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
    Header titles found in Dell Radiology Reports
    """
    COMPARISON = auto()
    COMPARISON_DATED = auto()
    COMPARISON_STUDY = auto()

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
    RESULT_NOTIFICATION = auto()
    TECHNIQUE = auto()

    ATTENDING_COMMENTS = auto()


if __name__ == '__main__':
    for x in DellHeaders:
        print(x)