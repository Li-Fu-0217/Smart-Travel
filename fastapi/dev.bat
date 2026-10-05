@echo off
rem 智慧旅游智能助手系统 · Windows 一键启动（后端）
rem 检查 .venv 是否存在 -> 安装依赖 -> 启动 uvicorn
cd /d %~dp0

if not exist .venv (
    echo [dev] 创建虚拟环境 .venv ...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
echo [dev] 安装依赖 ...
pip install -r requirements.txt
echo [dev] 启动后端 http://127.0.0.1:8000 ...
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
