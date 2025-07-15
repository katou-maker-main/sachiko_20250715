@echo off
echo PDFカラフル変換ツール - サーバー起動
echo ================================

echo 依存関係をチェック中...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlitがインストールされていません。インストール中...
    pip install -r requirements.txt
)

echo.
echo サーバーを起動しています...
echo チームメンバーは以下のURLでアクセスできます:
echo http://localhost:8501 (本人用)

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set ip=%%a
    set ip=!ip: =!
    echo http://!ip!:8501 (チーム用)
    goto :found
)
:found

echo.
echo 終了するにはCtrl+Cを押してください
echo ================================
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

pause