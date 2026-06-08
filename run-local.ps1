# ============================================================
#  ローカル検証用：本番(Render)に一切影響しない設定でアプリを起動します
#  使い方：PowerShellでこのファイルがあるフォルダに移動して
#          .\run-local.ps1
#  そのあとブラウザで http://localhost:8000 を開く
#  ログインしたいときは     http://localhost:8000/dev-login  を開く
#  止めるときは Ctrl + C
# ============================================================

# ローカル専用のデータ置き場（本番DBとは完全に別。git管理外）
$env:DB_DIR        = Join-Path $PSScriptRoot "localdata"
$env:UPLOAD_DIR    = Join-Path $PSScriptRoot "localdata\uploads"

# テストログインを許可（本番では絶対に設定しない）
$env:ALLOW_DEV_LOGIN = "1"

# ローカル用のダミー設定
$env:SESSION_SECRET  = "local-dev-secret"
$env:BASE_URL        = "http://localhost:8000"
$env:DEBUG_ERRORS    = "1"

# データフォルダを用意
New-Item -ItemType Directory -Force -Path $env:DB_DIR     | Out-Null
New-Item -ItemType Directory -Force -Path $env:UPLOAD_DIR | Out-Null

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " ローカル起動中... 下のURLをブラウザで開いてください" -ForegroundColor Cyan
Write-Host "   トップ      : http://localhost:8000" -ForegroundColor Yellow
Write-Host "   テストログイン: http://localhost:8000/dev-login" -ForegroundColor Yellow
Write-Host " 止めるには Ctrl + C" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# venv の python で uvicorn を起動（--reload でファイル保存すると自動再読込）
& (Join-Path $PSScriptRoot ".venv\Scripts\python.exe") -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
