"""proto_template.html に repo の CSV を埋め込んで proto.html を作る（build.py と同じ読み方）"""
import csv, json, sys, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
HERE = pathlib.Path(__file__).parent
NUM = {"id_min_in","id_max_in","reposition_limit_min","id_distal_in","id_proximal_in","od_distal_fr","od_proximal_fr","max_gw_in","min_guide_id_in","upper_id_in"}
def load(n):
    rows = list(csv.DictReader(open(ROOT/"data"/n, encoding="utf-8-sig", newline="")))
    for r in rows:
        for k, v in r.items():
            if k in NUM: r[k] = float(v) if v.strip() else None
            elif k in ("verified","detachable"): r[k] = v.strip() == "1"
    return rows
data = {"coils": load("coils.csv"), "catheters": load("catheters.csv"), "limits": load("platform_limits.csv"), "built": datetime.date.today().isoformat()}
t = (HERE/"v3_proto_template.html").read_text(encoding="utf-8")
(HERE/"v3_proto.html").write_text(t.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
print("ok")
