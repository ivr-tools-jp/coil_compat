"""照合用ページ（Artifact）を data/*.csv から作る。"""
import csv, json, pathlib, sys

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).with_name("coil_verify.html")
TPL = pathlib.Path(__file__).with_name("verify_template.html")

PMDA = "https://www.pmda.go.jp/PmdaSearch/kikiDetail/ResultDataSetPDF/"

def rows(name):
    with open(REPO / "data" / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def pmda(ref):
    if ref.startswith("pmda_bookSearch_"):
        return "https://www.pmda.go.jp/PmdaSearch/bookSearch/01/" + ref.replace("pmda_bookSearch_", "")
    return PMDA + ref.replace("pmda_", "") if ref.startswith("pmda_") else None

RULE = {
    "range": "下限と上限あり",
    "min_only": "下限のみ（上限の記載なし）",
    "min_nomax": "下限のみ（「上限なし」と明記）",
    "single": "1つの値のみ",
    "none": "内径の記載なし",
}

# 原本のどこを見るか（docs/ifu の文字起こしで確認したページ）
COIL_HINT = {
    "AZ-CX18": "p1 の表「コイル外径／マイクロカテーテル内径」。30分は p3 (9)",
    "AZ-CX35": "p1 の表「コイル外径／ガイディングカテーテル内径」。20分は p3 (9)",
    "AZ-S3D": "p1 の表「マイクロカテーテルの内径」。30分は p3 (11)",
    "AZ-HP": "p1 の表「マイクロカテーテルの内径」。10分は p3 (11)",
    "BS-IL18": "p1「内径0.53mm（0.021inch）のマイクロカテーテルを…」",
    "BS-IL35": "内径の数値が無いこと、Imager II 推奨の記載",
    "BS-EMB-F": "【使用方法等】の適合マイクロカテーテル内径（画像 PDF）",
    "BS-EMB-PS": "【使用方法等】の適合マイクロカテーテル内径（画像 PDF）",
    "SK-TGT": "内径の表の「Target その他」の行",
    "SK-TGT-TET": "内径の表の「Target Tetra」の行",
    "SK-TGT-XXL": "内径の表の「Target XXL」の行（最大内径規定なし）",
    "MD-CON-P-S": "p1 の表「コイルの種類／コイル径／マイクロカテーテル最小内径」PGLA 2〜10mm",
    "MD-CON-P-L": "p1 の表 PGLA ≧12mm",
    "MD-CON-N-S": "p1 の表 ナイロン 2〜4mm",
    "MD-CON-N-L": "p1 の表 ナイロン 5〜10mm",
    "KN-IED-10": "p2 の表「一次コイル外径／内径」0.010 インチの行。型名との対応はカタログ",
    "KN-IED-12": "p2 の表 0.012〜0.014 インチの行。型名との対応はカタログ",
    "KN-IED-14": "p2 の表 0.012〜0.014 インチの行。型名との対応はカタログ",
    "JL-AV-10": "p1 右上の型の表（タイプ欄の品番の頭 10CFR- など）と、その下の内径の表「マイクロカテーテル内径適応サイズ」",
    "JL-AV-18": "p1 右上の型の表（タイプ欄の品番の頭 10CFR- など）と、その下の内径の表「マイクロカテーテル内径適応サイズ」",
    "JL-MEGA": "p1 右上の型の表（タイプ欄の品番の頭 10CFR- など）と、その下の内径の表「マイクロカテーテル内径適応サイズ」。MEGA の名前はカタログ p4〜7",
}

TMP_HOME = "https://products.tokaimedpro.co.jp/"
UTM_HOME = "https://www.utm-m.co.jp/product_cat/micro_catheter/"
CAT_LINKS = {
    "TMP-CN-HF": [("東海 製品ページ", TMP_HOME)],
    "TMP-CN-ER": [("東海 製品ページ", TMP_HOME)],
    "TMP-CN-PXER": [("東海 製品ページ", TMP_HOME)],
    "TMP-CN-HFS": [("東海 カタログ", "https://products.tokaimedpro.co.jp/2172912")],
    "TMP-MV-S13": [("東海 カタログ", "https://products.tokaimedpro.co.jp/2158450"), ("東海 カタログ2", "https://products.tokaimedpro.co.jp/2172912")],
    "TMP-MV-S": [("東海 カタログ", "https://products.tokaimedpro.co.jp/2158450"), ("東海 カタログ2", "https://products.tokaimedpro.co.jp/2172912")],
    "TMP-MV-NT": [("東海 カタログ", "https://products.tokaimedpro.co.jp/2158450"), ("東海 カタログ2", "https://products.tokaimedpro.co.jp/2172912")],
    "UTM-CL-NSXHF": [("UTM 製品ページ", UTM_HOME)],
    "UTM-CL-UX19": [("UTM 製品ページ", UTM_HOME)],
    "PNB-LANTERN": [("Penumbra（海外）", "https://www.penumbrainc.com/pl/peripheral-device/lantern")],
    "SK-SL10": [("Stryker 日本", "https://www.stryker.com/jp/ja/neurovascular/products/excelsior--sl-10--microcatheter.html")],
    "SK-1018": [("Stryker 日本", "https://www.stryker.com/jp/ja/neurovascular/products/excelsior--1018--microcatheter.html"), ("Stryker 米国", "https://www.strykerneurovascular.com/products/access/excelsior-1018-microcatheters")],
    "SK-XT17": [("Stryker 日本", "https://www.stryker.com/jp/ja/neurovascular/products/excelsior--xt-17-microcatheter.html")],
    "BS-BT2M": [("ボストン 日本", "https://www.bostonscientific.com/jp-JP/products/catheter-micro/Breakthrough_2_Marker.html")],
}
CAT_HINT = {
    "UTM-CL-UX19": "仕様：UX19 カタログ（docs/ifu/utm_ux19_spec.pdf ＝ cat108）。販売名・承認番号：価格表 utm_ux19_catalog.pdf（cat107）の上部。版：デスクトップの「780251_21600BZZ00598000_A_01_11_キャリー.pdf」p1 左上",
    "UTM-CL-HF2628": "仕様：デスクトップの「carryleon【新】.pdf」（＝ utm_carryleon_new.pdf、Cat069）の High Flow の表。販売名・承認番号：価格表 utm_leon1.pdf（cat063）の上部。版：「…_キャリー.pdf」p1 左上",
    "UTM-SEL-15-1M": "仕様：デスクトップの「carryleon【新】.pdf」（Cat069）の Selective の表（品番 S1519…）。販売名・承認番号：価格表 utm_leon1.pdf／utm_leon2.pdf の上部。版：「…_キャリー.pdf」p1 左上",
    "UTM-SEL-15-2M": "仕様：デスクトップの「carryleon【新】.pdf」（Cat069）の Selective の表（品番 DMS1519…）。販売名・承認番号：価格表 utm_leon1.pdf／utm_leon2.pdf の上部。版：「…_キャリー.pdf」p1 左上",
    "UTM-SLIM-IN": "仕様：デスクトップの「carryslimleon.pdf」p2 下の左の表（LS1517165）。販売名・承認番号：価格表 utm_slim_leon.pdf（cat096）の上部。版：「…_キャリー.pdf」p1 左上",
    "UTM-SLIM-OUT": "仕様：デスクトップの「carryslimleon.pdf」p2 下の右の表（LS2425…）。135cm と販売名・承認番号：価格表 utm_slim_leon.pdf（cat096）。版：「…_キャリー.pdf」p1 左上",
    "PNB-LANTERN": "内径・外径・有効長：Penumbra の海外製品ページ（ユーザー提供ではなく Claude が取得）。最大ガイドワイヤ径・通せる親の最小内径・販売名・承認番号・版：PX400(B) の添付文書 p1",
    "SK-SL10": "外径：ストライカー日本語製品ページの仕様（1.7F/2.4F）。ほかの項目：添付文書 I3-05 p3 の参考情報の表（外径はこの表に無い）",
    "SK-XT17": "外径：添付文書 IO-04 p3 の寸法の表（先端部 1.7Fr／手元部 2.4Fr）、または日本語製品ページ",
    "SK-1018": "外径：ストライカー日本語製品ページの仕様（2.0F/2.6F）。ほかの項目：添付文書 I3-05 p3 の参考情報の表（外径はこの表に無い）",
}
# 販売名・承認番号を確かめるための添付文書（マイクロカテーテル）
CAT_IFU = {
    "21600BZZ00094000": "480367_21600BZZ00094000_J_01_07",
    "30400BZX00050000": "780251_30400BZX00050000_A_01_02",
    "22400BZX00295000": "650099_22400BZX00295000_B_01_04",
    "21700BZZ00471000": "531043_21700BZZ00471000_I_02_03",
}

def inch(v):
    if not v:
        return ""
    return f"{v}″（{float(v) * 25.4:.2f}mm）"

def coil_items(r):
    f = [
        ("size_condition", "内径の条件が当てはまるサイズ", "全サイズ共通（サイズによる違いなし）" if r["size_condition"] == "全サイズ" else r["size_condition"]),
        ("id_min_in", "内径の下限", inch(r["id_min_in"])),
        ("id_max_in", "内径の上限", inch(r["id_max_in"])),
        ("id_rule", "添付文書の書き方", RULE.get(r["id_rule"], r["id_rule"])),
    ]
    if r["surface"] == "hydrogel":
        f.append(("reposition_limit_min", "位置を直せる時間", f"{r['reposition_limit_min']}分"))
    f += [
        ("jp_trade_name", "販売名", r["jp_trade_name"]),
        ("approval_no", "承認番号", r["approval_no"]),
        ("source_date", "添付文書の改訂日・版", r["source_date"]),
    ]
    return f

def cat_items(r):
    fr = lambda v: f"{v}Fr" if v else ""
    return [
        ("id_distal_in", "先端の内径（判定に使う）", inch(r["id_distal_in"])),
        ("id_proximal_in", "手元の内径", inch(r["id_proximal_in"])),
        ("od_distal_fr", "先端の外径", fr(r["od_distal_fr"])),
        ("od_proximal_fr", "手元の外径", fr(r["od_proximal_fr"])),
        ("lengths_cm", "有効長", r["lengths_cm"].replace(";", "／") + ("cm" if r["lengths_cm"] else "")),
        ("max_gw_in", "最大ガイドワイヤ径", f"{r['max_gw_in']}″" if r["max_gw_in"] else ""),
        ("min_guide_id_in", "通せる親の最小内径", f"{r['min_guide_id_in']}″" if r["min_guide_id_in"] else ""),
        ("jp_trade_name", "販売名", r["jp_trade_name"]),
        ("approval_no", "承認番号", r["approval_no"]),
        ("source_date", "添付文書の改訂日・版", r["source_date"]),
    ]

SRC_TYPE = {"ifu_jp": "国内添付文書", "catalog_jp": "国内カタログ", "foreign": "海外資料"}

def main():
    data = []
    for r in rows("coils.csv"):
        refs = [s.strip() for s in r["source_ref"].split("＋")]
        links = [("添付文書（PMDA）", pmda(s)) for s in refs if pmda(s)]
        if r["series"] == "i-ED":
            links.append(("カネカ カタログ", "https://www.kaneka-med.jp/medicalstaff/products/1_intervention/1_cerebrovascular/1_embolic-coil/1_ied-coil/"))
        local = [s for s in refs if not s.startswith("pmda_")]
        data.append(dict(
            id=r["coil_id"], kind="coil", title=r["group"],
            maker=f"{r['distributor_jp']}（{r['manufacturer']}）" if r["manufacturer"] != r["distributor_jp"] else r["manufacturer"],
            src=SRC_TYPE.get(r["source_type"], r["source_type"]), ref=r["source_ref"],
            hint=COIL_HINT.get(r["coil_id"], ""), links=links,
            local=[f"PC の docs/ifu/{s}.pdf" for s in local],
            note=r["note"], verified=r["verified"] == "1",
            items=[dict(k=k, label=l, v=v, raw=r.get(k, "")) for k, l, v in coil_items(r)],
        ))
    for r in rows("catheters.csv"):
        links = list(CAT_LINKS.get(r["cat_id"], []))
        refs = [x.strip() for x in r["source_ref"].split("＋")]
        links += [("添付文書（PMDA）", pmda(x)) for x in refs if pmda(x)]
        if r["approval_no"] in CAT_IFU and not any(pmda(x) for x in refs):
            links.append(("添付文書（PMDA・販売名の確認用）", PMDA + CAT_IFU[r["approval_no"]]))
        local = []
        if "ユーザー提供" in r["source_ref"]:
            local.append("ユーザー提供の資料（PC の docs/ifu の utm_*.pdf）")
        data.append(dict(
            id=r["cat_id"], kind="cat", title=r["model"],
            maker=f"{r['distributor_jp']}（{r['manufacturer']}）" if r["manufacturer"] != r["distributor_jp"] else r["manufacturer"],
            src=SRC_TYPE.get(r["source_type"], r["source_type"]), ref=r["source_ref"],
            hint=CAT_HINT.get(r["cat_id"]) or ("カタログの仕様表（内径・外径・有効長・ガイドワイヤ）。どの添付文書かは、カタログに載っている販売名・承認番号で見分ける（添付文書には製品名が無いことが多い）" + ("。TMPマイクロカテーテルの製品名は東海の取扱説明書 No.1・No.2（docs/ifu/tokai_TMPmicro_ifu_202409.pdf の p1〜2）にも一覧あり" if r["approval_no"] == "21600BZZ00094000" else "") + ("。TMPマイクロカテーテルⅢの添付文書には品番 MXNS（先端1.6Fr）・MXNK（先端1.3Fr）の記載あり" if r["approval_no"] == "22700BZX00090000" else "")), links=links, local=local,
            note=r["note"], verified=r["verified"] == "1",
            items=[dict(k=k, label=l, v=v, raw=r.get(k, "")) for k, l, v in cat_items(r)],
        ))
    # サブエージェントの再確認結果（あれば）を項目に付ける
    ai = {}
    for name in ("ai_coils.json", "ai_cats.json"):
        p = OUT.with_name(name)
        if p.exists():
            for a in json.loads(p.read_text(encoding="utf-8")):
                ai[(a["row_id"], a["key"])] = a
    for d in data:
        for it in d["items"]:
            a = ai.get((d["id"], it["k"]))
            if a:
                # AI が見た後に CSV を直した項目は「修正済み」にする
                st = a.get("status")
                if st != "match" and (a.get("csv") or "") != it["raw"]:
                    st = "fixed"
                it["ai"] = dict(s=st, src=a.get("source_value") or "", p=a.get("page"),
                                file=a.get("file") or "", note=a.get("note") or "")
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = TPL.read_text(encoding="utf-8").replace("/*__DATA__*/[]", blob)
    OUT.write_text(html, encoding="utf-8")
    n = sum(len(d["items"]) for d in data)
    print(f"{len(data)} rows, {n} items -> {OUT}")

if __name__ == "__main__":
    main()
