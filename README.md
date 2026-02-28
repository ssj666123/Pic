[README.md](https://github.com/user-attachments/files/25617938/README.md)
## Python 推荐服务（本项目配套）

### 1) 安装依赖

在 `python-recommender` 目录执行：

```bash
pip install -r requirements.txt
```

### 2) 启动服务

```bash
python app.py
```

默认监听：

- `POST http://127.0.0.1:5000/recommend`
- `GET  http://127.0.0.1:5000/health`

### 3) Java 端如何调用

Java 后端默认会调用 `http://127.0.0.1:5000/recommend`。

你也可以设置环境变量修改地址：

```bash
set PY_RECOMMENDER_URL=http://127.0.0.1:5000/recommend
```

