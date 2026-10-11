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
app/static/               アイコン（tools/make_icons.py で作る）
tools/verify/             照合表（Artifact）の生成
.github/workflows/        GitHub Pages への自動公開
```

## ビルド
```
python app/build.py                 # Artifact 用（app/index.html、1ファイル）
python app/build.py --site _site    # 公開用（PWA 一式）
python -m http.server -d _site      # 手元で確認（http://localhost:8000）
```
公開用はスマホのホーム画面に追加でき、一度開けばオフラインでも使える。画面はネット優先で、つながるときは常に最新のデータを出す（4秒で応答が無ければ前回の写し）。CSV を直して push すると、キャッシュ名が変わって古い写しは消える。標準ライブラリだけで動く（アイコンの作り直しだけ Pillow が要る）。

## 判定
コイルの「適合するカテーテル内径」とカテーテルの先端内径を照らし合わせ、○（範囲内）／△（上限の記載なし・基準なし）／×（範囲外）を出す。詳細は `docs/codebook.md`。
