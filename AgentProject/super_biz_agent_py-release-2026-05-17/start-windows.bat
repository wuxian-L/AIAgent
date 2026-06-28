@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ====================================
echo 鍚姩 SuperBizAgent 鏈嶅姟
echo ====================================
echo.

REM 妫€鏌?uv 鏄惁瀹夎锛堝彲閫夛紝濡傛灉娌℃湁浼氫娇鐢?pip锛?echo [1/6] 妫€鏌ュ寘绠＄悊鍣?..
where uv >nul 2>&1
if errorlevel 1 (
    echo [淇℃伅] uv 鏈畨瑁咃紝灏嗕娇鐢ㄤ紶缁?pip 鏂瑰紡
    echo [鎻愮ず] 瀹夎 uv 鍙彁鍗囬€熷害锛歱ip install uv
    set USE_UV=0
) else (
    echo [鎴愬姛] 妫€娴嬪埌 uv 鍖呯鐞嗗櫒
    set USE_UV=1
)
echo.

REM 纭繚 Python 鐗堟湰姝ｇ‘
echo [2/6] 閰嶇疆 Python 鐗堟湰...
if exist .python-version (
    set /p PYTHON_VERSION=<.python-version
    echo [淇℃伅] 褰撳墠閰嶇疆鐗堟湰: !PYTHON_VERSION!
    
    REM 妫€鏌ユ槸鍚︿负 3.10锛堜笉鍏煎锛?    echo !PYTHON_VERSION! | findstr /C:"3.10" >nul
    if not errorlevel 1 (
        echo [璀﹀憡] Python 3.10 涓嶅吋瀹癸紝鑷姩鏇存柊鍒?3.13...
        echo 3.13> .python-version
        echo [鎴愬姛] 宸叉洿鏂板埌 Python 3.13
    )
) else (
    echo [淇℃伅] 鍒涘缓 .python-version 鏂囦欢...
    echo 3.13> .python-version
)
echo.

REM 鍒涘缓鎴栧悓姝ヨ櫄鎷熺幆澧?echo [3/6] 鍒涘缓/鍚屾铏氭嫙鐜...
if exist .venv\Scripts\python.exe (
    echo [淇℃伅] 铏氭嫙鐜宸插瓨鍦紝妫€鏌ユ洿鏂?..
    
    REM 濡傛灉鏈?uv锛屽皾璇曚娇鐢?uv sync
    if "%USE_UV%"=="1" (
        uv sync 2>nul
        if errorlevel 1 (
            echo [璀﹀憡] uv sync 澶辫触锛屼娇鐢?pip 鏇存柊...
            .venv\Scripts\python.exe -m pip install -e . -q
        ) else (
            echo [鎴愬姛] 浣跨敤 uv 鍚屾瀹屾垚
        )
    ) else (
        echo [淇℃伅] 浣跨敤 pip 鏇存柊渚濊禆...
        .venv\Scripts\python.exe -m pip install -e . -q
    )
) else (
    echo [淇℃伅] 鍒涘缓鏂扮殑铏氭嫙鐜...
    
    REM 濡傛灉鏈?uv锛屽皾璇曚娇鐢?uv sync
    if "%USE_UV%"=="1" (
        echo [淇℃伅] 灏濊瘯浣跨敤 uv sync 鍒涘缓...
        uv sync 2>nul
        if not errorlevel 1 (
            echo [鎴愬姛] 浣跨敤 uv 鍒涘缓瀹屾垚
            goto :venv_created
        )
        echo [璀﹀憡] uv sync 澶辫触锛屽洖閫€鍒颁紶缁熸柟寮?..
    )
    
    REM 浣跨敤浼犵粺 Python venv 鍒涘缓
    echo [淇℃伅] 浣跨敤 python -m venv 鍒涘缓...
    python -m venv .venv
    if errorlevel 1 (
        echo [閿欒] 铏氭嫙鐜鍒涘缓澶辫触
        echo [鎻愮ず] 璇风‘淇濆凡瀹夎 Python 3.11+
        pause
        exit /b 1
    )
    
    REM 瀹夎渚濊禆
    echo [淇℃伅] 瀹夎椤圭洰渚濊禆锛堣繖鍙兘闇€瑕佸嚑鍒嗛挓锛?..
    .venv\Scripts\python.exe -m pip install --upgrade pip -q
    .venv\Scripts\python.exe -m pip install -e . -q
    if errorlevel 1 (
        echo [閿欒] 渚濊禆瀹夎澶辫触
        pause
        exit /b 1
    )
    echo [鎴愬姛] 铏氭嫙鐜鍒涘缓瀹屾垚
)

:venv_created
echo [鎴愬姛] 铏氭嫙鐜灏辩华
echo.

REM 璁剧疆 Python 鍛戒护
set PYTHON_CMD=.venv\Scripts\python.exe

REM 鍚姩 Docker Compose
echo [4/6] 鍚姩 Milvus 鍚戦噺鏁版嵁搴?..
docker ps --format "{{.Names}}" | findstr "milvus-standalone" >nul 2>&1
if not errorlevel 1 (
    echo [淇℃伅] Milvus 瀹瑰櫒宸插湪杩愯
) else (
    docker compose -f vector-database.yml up -d
    if errorlevel 1 (
        echo [閿欒] Docker 鍚姩澶辫触锛岃纭繚 Docker Desktop 宸插惎鍔?        pause
        exit /b 1
    )
    echo [淇℃伅] 绛夊緟 Milvus 鍚姩锛?0绉掞級...
    timeout /t 10 /nobreak >nul
)
echo [鎴愬姛] Milvus 鏁版嵁搴撳氨缁?echo.

REM 鍚姩 CLS MCP 鏈嶅姟
echo [5/6] 鍚姩 CLS MCP 鏈嶅姟...
start "CLS MCP Server" /min %PYTHON_CMD% mcp_servers/cls_server.py
timeout /t 2 /nobreak >nul
echo [鎴愬姛] CLS MCP 鏈嶅姟宸插惎鍔?echo.

REM 鍚姩 Monitor MCP 鏈嶅姟
echo [6/6] 鍚姩 Monitor MCP 鏈嶅姟...
start "Monitor MCP Server" /min %PYTHON_CMD% mcp_servers/monitor_server.py
timeout /t 2 /nobreak >nul
echo [鎴愬姛] Monitor MCP 鏈嶅姟宸插惎鍔?echo.

REM 鍚姩 FastAPI 鏈嶅姟
echo [7/8] 鍚姩 FastAPI 鏈嶅姟...
start "SuperBizAgent API" %PYTHON_CMD% -m uvicorn app.main:app --host 0.0.0.0 --port 9900
echo [淇℃伅] 绛夊緟鏈嶅姟鍚姩锛?5绉掞級...
timeout /t 15 /nobreak >nul
echo.

REM 妫€鏌ユ湇鍔＄姸鎬佸苟涓婁紶鏂囨。
echo.
echo [淇℃伅] 妫€鏌ユ湇鍔＄姸鎬?..
curl -s http://localhost:9900/health >nul 2>&1
if errorlevel 1 (
    echo [璀﹀憡] 鏈嶅姟鍙兘杩樻湭瀹屽叏鍚姩锛岃绋嶇瓑鐗囧埢
) else (
    echo [鎴愬姛] FastAPI 鏈嶅姟杩愯姝ｅ父
    echo.
    
    REM 璋冪敤 API 涓婁紶 aiops-docs 鏂囨。鍒板悜閲忔暟鎹簱
    echo [8/8] 涓婁紶鏂囨。鍒板悜閲忔暟鎹簱...
    for %%f in (aiops-docs\*.md) do (
        echo   涓婁紶: %%~nxf
        curl -s -X POST http://localhost:9900/api/upload -F "file=@%%f" >nul 2>&1
    )
    echo [鎴愬姛] 鏂囨。涓婁紶瀹屾垚
)

echo.
echo ====================================
echo 鏈嶅姟鍚姩瀹屾垚锛?echo ====================================
echo Web 鐣岄潰: http://localhost:9900
echo API 鏂囨。: http://localhost:9900/docs
echo.
echo 鏌ョ湅鏃ュ織:
echo   - FastAPI: logs\app_*.log锛圠oguru 鏃ュ織锛屾寜澶╄疆杞級
echo   - CLS MCP: type mcp_cls.log
echo   - Monitor: type mcp_monitor.log
echo 鍋滄鏈嶅姟: stop-windows.bat
echo ====================================
pause
