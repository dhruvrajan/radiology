from radiology.loaders import Reports, list_all_reports
from radiology.datatypes.reports import DellHeaders as DH
import re


if __name__ == "__main__":
    reports = Reports.unlabeled()
    l = list(filter(lambda r: re.match("1\..*2\..*", r.get(DH.IMPRESSION)), reports.reports.values()))
    for i in range(5):
        print(l[i].get(DH.FINDINGS))
        print()
        print(l[i].get(DH.IMPRESSION))
        input()