安装后端的依赖：
pip install -r requirements.txt

后端启动：
cd .\backend\ 
uvicorn app.main:app --reload --port 8080

前端启动：
cd .\frontend\
npm run serve
