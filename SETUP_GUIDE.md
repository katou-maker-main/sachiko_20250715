# PDFカラフル変換ツール - セットアップガイド

## チーム共有用セットアップ

### 前提条件
- Python 3.8以上がインストールされていること
- インターネット接続があること

### 1. ファイルの準備
以下のファイルをチームメンバーに共有してください：
```
pdf_colorizer/
├── app.py
├── requirements.txt
├── README.md
├── DEVELOPMENT_LOG.md
└── SETUP_GUIDE.md（このファイル）
```

### 2. セットアップ手順

#### Windows
```cmd
# 1. フォルダに移動
cd path\to\pdf_colorizer

# 2. 仮想環境作成（推奨）
python -m venv pdf_colorizer_env
pdf_colorizer_env\Scripts\activate

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. アプリ起動
streamlit run app.py
```

#### Mac/Linux
```bash
# 1. フォルダに移動
cd path/to/pdf_colorizer

# 2. 仮想環境作成（推奨）
python3 -m venv pdf_colorizer_env
source pdf_colorizer_env/bin/activate

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. アプリ起動
streamlit run app.py
```

### 3. ネットワーク共有（チーム内）

#### 起動コマンド（他の人もアクセス可能）
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

#### アクセス方法
- **本人**: http://localhost:8501
- **チームメンバー**: http://[起動者のIPアドレス]:8501

#### IPアドレス確認方法
**Windows**:
```cmd
ipconfig
```

**Mac/Linux**:
```bash
ifconfig
```

### 4. トラブルシューティング

#### よくあるエラー
1. **ModuleNotFoundError**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **ポートが使用中**
   ```bash
   streamlit run app.py --server.port 8502
   ```

3. **ファイアウォール**
   - Windows: Windows Defenderでポート8501を許可
   - Mac: システム環境設定でファイアウォール設定

#### 動作確認
- ブラウザで http://localhost:8501 にアクセス
- 「PDFカラフル変換ツール」画面が表示されればOK

### 5. 使用方法
1. PDFファイルをアップロード
2. カラースキームを選択
3. 「変換後」の画像を確認
4. 個別またはZIPで一括ダウンロード

### 6. 注意事項
- 大きなPDFファイル（10MB以上）は処理に時間がかかります
- 同時に複数人が使用する場合、サーバーの性能に注意
- 機密文書の取り扱いに注意してください

### 7. サポート
問題が発生した場合は開発者に連絡してください。
エラーメッセージと環境情報（OS、Pythonバージョン）を含めてください。