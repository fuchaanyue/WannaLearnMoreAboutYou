# WannaLearnMoreAboutYou

一个轻量级的 Django Web 应用，用于展示个人信息并保护隐私内容。

## 功能特点

- 首页问答验证功能
- 通过验证后显示反馈页面和微信二维码
- 微信二维码通过受保护的视图提供访问
- 所有敏感配置通过环境变量管理
- 可直接部署到 Render

## 项目结构

```
WannaLearnMoreAboutYou/
├── .env.example              # 环境变量示例文件
├── .gitignore                # Git 忽略文件配置
├── requirements.txt          # Python 依赖包
├── wannalearnmoreaboutyou/   # Django 项目目录
│   ├── __init__.py
│   ├── settings.py           # Django 设置文件
│   ├── urls.py              # 主路由配置
│   ├── wsgi.py              # WSGI 配置
│   └── manage.py            # Django 管理命令
├── quiz/                     # 应用目录
│   ├── __init__.py
│   ├── views.py             # 视图函数
│   ├── urls.py              # 应用路由配置
│   └── templates/           # 模板文件
│       └── quiz/
│           ├── index.html   # 首页模板
│           └── feedback.html # 反馈页模板
├── private_files/            # 私有文件目录（用户需自行放入微信二维码）
│   └── wechat_qr.png        # 微信二维码图片
└── README.md                # 项目说明文件
```

## 安装和运行

1. 克隆或下载项目代码

2. 创建虚拟环境并激活：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 复制 `.env.example` 到 `.env` 并根据需要修改环境变量：
   ```bash
   cp .env.example .env
   ```
   
   在 `.env` 文件中设置：
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   QUIZ_ANSWER=your-quiz-answer-here
   ```

5. 将您的微信二维码图片放入 `private_files/` 目录并命名为 `wechat_qr.png`

6. 运行开发服务器：
   ```bash
   cd WannaLearnMoreAboutYou
   python manage.py runserver
   ```

## 部署到 Render

1. 将代码推送到 GitHub 仓库

2. 在 Render 上创建新的 Web Service

3. 连接您的 GitHub 仓库

4. 配置环境变量：
   - SECRET_KEY
   - DEBUG (设置为 False)
   - ALLOWED_HOSTS (设置为您的 Render 应用域名)
   - QUIZ_ANSWER

5. 构建命令设置为：
   ```bash
   pip install -r requirements.txt
   ```

6. 启动命令设置为：
   ```bash
   gunicorn wannalearnmoreaboutyou.wsgi:application
   ```

## 使用说明

1. 访问首页，输入正确的答案（由 `QUIZ_ANSWER` 环境变量定义）
2. 答案正确后，将重定向到反馈页面
3. 在反馈页面可以看到微信二维码
4. 二维码只能通过验证后访问，直接访问 `/qrcode/` 将返回 403 错误

## 安全特性

- 微信二维码存储在私有目录中，无法通过直接 URL 访问
- 二维码只能通过受保护的视图访问，需要通过测验验证
- 所有敏感配置通过环境变量管理，避免硬编码
- 使用 Django sessions 管理用户状态