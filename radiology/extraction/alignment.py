from radiology.loaders import Reports, unlabeled_reports
from radiology.datatypes.reports import DellHeaders as DH
import re
import string


if __name__ == "__main__":
    rs = Reports.from_generator(unlabeled_reports)
    count = 0
    total = 0
    for r in rs.reports:
        total += 1
        findings = rs.reports[r].get(DH.FINDINGS)
        impression = rs.reports[r].get(DH.IMPRESSION)
        if re.match("[123456789]\.\s.*", impression):
            count += 1
            # continue
            split = re.split("[123456789]\.\s", impression)
            def f(w): return w.strip(string.whitespace)

            cleaned = [f(w) for w in split if len(f(w)) > 0]
            
            print("findings", findings)
            print("<<<")
            for s in cleaned:
                print(s)

            print()

    print(count, total)