# 后端镜像（build context = 仓库根，dockerfile 指向本文件）
FROM python:3.12-slim

WORKDIR /app

# 依赖层（先拷贝 requirements，利用构建缓存）
COPY fastapi/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 代码 + 建库脚本 + schema
COPY fastapi/app ./app
COPY fastapi/scripts ./scripts
COPY sql /sql
COPY fastapi/data/knowledge_seed ./data/knowledge_seed

EXPOSE 8000

# 入口：先等 MySQL 就绪并建库（改写 system.sql 库名），再起 uvicorn
CMD ["sh", "scripts/entrypoint.sh"]
