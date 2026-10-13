# coil_compat

IVR で使うマイクロカテーテル／親カテーテルと塞栓用コイルの組み合わせが使えるかを、スマホでひと目で確認するツール（作成中）。

**注意：表示する内容は添付文書・カタログから作った参考情報です。使用前に必ず最新の添付文書を確認してください。**

## 構成
```
data/catheters.csv        マイクロカテーテル（内径など）
data/coils.csv            コイル（適合するカテーテル内径の範囲など）
data/platform_limits.csv  コイル系統ごとの内径の上限（ユーザーが決める）
docs/codebook.md          変数名・単位・コードの説明
docs/sources.md           出典一覧（URL・版）
docs/ifu/                 添付文書・カタログの写し（公開しない）
app/template.html         画面（CSV はビルド時に埋め込む）
app/build.py              ビルド
app/pwa/                  公開用の head・manifest・Service Worker の元
app/static/               アイコン（tools/make_icons.py）・フォント（fonts/、tools/make_fonts.py）
tools/verify/             照合表（Artifact）の生成
design/                   配色の検討（color_review.md）・旧試作
.github/workflows/        GitHub Pages への自動公開
```

## ビルド
```
python app/build.py                 # Artifact 用（app/index.html、1ファイル）
python app/build.py --site _site    # 公開用（PWA 一式）
python -m http.server -d _site      # 手元で確認（http://localhost:8000）
```
公開用はスマホのホーム画面に追加でき、一度開けばオフラインでも使える。画面・フォント・アイコンは手元の写しをすぐ出す（キャッシュ優先）。CSV や画面を直して push すると sw.js のキャッシュ名が変わり、利用者の画面の下に「新しいデータがあります」が出て、押すと切り替わる。ビルドは標準ライブラリだけで動く（アイコンの作り直しは Pillow、フォントの作り直しは fonttools・brotli が要る）。

データに新しい漢字が増えると、ビルドが「同梱フォントにない文字」と知らせる。そのときは元フォントを用意して `python tools/make_fonts.py 元フォントのフォルダ` を流し直す（手順はスクリプトの先頭）。フォントは SIL Open Font License（`app/static/fonts/OFL-*.txt`）。

共有リンクは `…/#a=cat&c=micro:<cat_id>&o=<coil_id>`（親カテーテルは `c=parent:0.041`）。試作だった beta.html はトップへ送るだけのページ。

## 判定
コイルの「適合するカテーテル内径」とカテーテルの先端内径を照らし合わせ、○（範囲内）／△（上限の記載なし・基準なし）／×（範囲外）を出す。詳細は `docs/codebook.md`。
