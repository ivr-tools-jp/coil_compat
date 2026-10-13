# コード表

データは `data/` の CSV 3つ。どれも1行1項目、文字コードは UTF-8（BOM 付き。Excel でそのまま開ける）。
内径・ガイドワイヤ径の単位はすべて **inch**。外径は **Fr**、長さは **cm**。

## coils.csv（コイル）
1行は「内径の条件が同じコイルのまとまり」。同じシリーズでもサイズで条件が変わる場合は行を分ける。

| 変数名 | 意味 | 値・コード |
|---|---|---|
| coil_id | 行の ID | メーカー略号-シリーズ-区分（例 AZ-CX18） |
| manufacturer | 製造元 | |
| distributor_jp | 国内の製造販売元・販売元 | |
| series | シリーズ名 | |
| group | 画面に出す名前 | |
| search_alias | 検索用の読み・別名 | カタカナで書く（ひらがなで探しても当たる）。複数は `;` 区切り。画面には出さない |
| size_condition | この行が当てはまるサイズ | 「全サイズ」「コイル径 2〜10mm」「一次コイル外径 0.010″」など |
| platform | コイルの系統 | 10 / 18 / 35。不明は空欄 |
| detachable | 離脱式か | 1＝離脱式、0＝プッシャブル |
| surface | 表面処理 | bare＝なし、fiber＝ファイバー付き、hydrogel＝ハイドロゲル |
| delivery_via | どのカテーテルで送るか | micro＝マイクロカテーテル、parent＝親カテーテル |
| id_min_in | カテーテル内径の下限 | inch。記載なしは空欄 |
| id_max_in | カテーテル内径の上限 | inch。記載なしは空欄 |
| id_rule | 添付文書の書き方 | 下表 |
| why_extra | △の理由に添える補足 | 1行。△のときだけ理由の後ろに括弧で出す。判定には使わない（例：海外資料の推奨） |
| reposition_limit_min | 位置を直せる時間（ハイドロゲル） | 分。記載なしは空欄 |
| detach_device | 離脱装置 | 表示のみ。判定には使わない |
| mfr_listed_catheters | メーカーが名前を挙げているカテーテル | 表示のみ。判定には使わない（「メーカー記載あり」の目印。2026-10-13 に「メーカー確認済み」から変更） |
| jp_trade_name | 国内の販売名 | 添付文書の表記 |
| approval_no | 承認番号 | |
| source_type | 出典の種類 | ifu_jp＝国内添付文書、catalog_jp＝国内カタログ・製品ページ、foreign＝海外資料 |
| source_ref | 出典ファイル・資料名 | `docs/sources.md` に URL |
| source_date | 添付文書の改訂年月・版 | 改訂の追跡用。カタログが出典の行（マイクロカテーテルなど）も、その製品の国内添付文書の版を入れる。未入手は「添付文書未入手」 |
| verified | 原本と照合済みか | 0＝未照合、1＝照合済み |
| checked_date | 原本と照合した日 | YYYY-MM-DD。画面上部の「添付文書と照合」には全行（コイル・カテーテル）のうち最も古い日を出す。直したら照合し直して更新する |
| note | 補足 | |

### id_rule（添付文書の書き方）
| コード | 意味 | 判定 |
|---|---|---|
| range | 下限と上限がある | 範囲内○／範囲外× |
| min_only | 下限だけ（上限の記載なし） | 下限未満×／下限以上で系統の上限以下○／それを超えたら△ |
| min_nomax | 下限だけ（「上限なし」と明記） | 下限未満×／下限以上○ |
| single | 1つの値だけ（例：「0.021inch のマイクロカテーテル」） | 値未満×／一致○／超えたら min_only と同じ扱い |
| none | 内径の記載なし | 常に△（「添付文書に内径の基準なし」） |

系統の上限は `platform_limits.csv` で決める。未設定の間は「上限未設定」として△にする。

## catheters.csv（マイクロカテーテル）
1行はモデル単位（品番の違いが長さ・先端形状だけなら1行にまとめる）。

| 変数名 | 意味 | 値・コード |
|---|---|---|
| cat_id | 行の ID | |
| manufacturer / distributor_jp | 製造元／国内の販売元 | |
| series / model | シリーズ名／モデル名 | |
| search_alias | 検索用の読み・別名 | coils.csv と同じ |
| part_no_examples | 品番の例 | |
| id_distal_in | 先端側の内径 | inch。**判定に使う値** |
| id_proximal_in | 手元側の内径 | inch。テーパーがなければ先端と同じ |
| od_distal_fr / od_proximal_fr | 先端側／手元側の外径 | Fr |
| lengths_cm | 有効長のラインナップ | cm、`;` 区切り |
| max_gw_in | 適合する最大ガイドワイヤ径 | inch |
| min_guide_id_in | 通せる親カテーテル（ガイディング）の最小内径 | inch。Triaxial で組むときの目安。記載なしは空欄 |
| jp_trade_name / approval_no | 国内の販売名／承認番号 | |
| source_type / source_ref / source_date / verified / checked_date / note | coils.csv と同じ | |

親カテーテルは登録しない。画面で内径を選ぶか直接入力する。

## platform_limits.csv（系統ごとの内径の上限）
| 変数名 | 意味 |
|---|---|
| platform | 10 / 18 / 35 |
| upper_id_in | これを超えたら△にする内径（inch）。空欄＝未設定 |
| decided_by / decided_date / note | 決めた人・日付・理由 |
