# PDF カラフル変換ツール

モノクロのパンフレットを色鮮やかで高級感のある仕上がりに自動変換するWebアプリです。

## 機能

- ✅ PDFファイルのアップロード
- ✅ モノクロ→カラー自動変換
- ✅ 4種類のカラースキーム（ビジネス・エレガント・モダン・ナチュラル）
- ✅ グラフエリア自動検出・装飾
- ✅ 高級感フィルター適用
- ✅ 高解像度PNG出力

## インストール・実行

```bash
# 依存関係インストール
pip install -r requirements.txt

# アプリ起動
streamlit run app.py
```

## 使い方

1. ブラウザで http://localhost:8501 にアクセス
2. PDFファイルをアップロード
3. カラースキームを選択
4. 変換結果を確認・ダウンロード

## 技術仕様

- **フレームワーク**: Streamlit
- **PDF処理**: pdf2image
- **画像処理**: Pillow, OpenCV
- **完全オフライン**: 外部API不要