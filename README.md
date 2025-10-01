# WannaLearnMoreAboutYou

一个个性化的 Django Web 应用，通过问答验证解锁个人信息，提供安全的内容访问体验。

## 功能特点

- 个性化问候体验：通过首页获取用户姓名，后续页面个性化展示
- 多题问答验证系统：包含提示功能的渐进式问答挑战
- 隐私保护机制：通过验证后才能访问敏感内容（如微信二维码）
- 反馈收集系统：通过验证后可提交反馈信息
- 安全文件访问：微信二维码通过受保护的视图提供访问
- 多渠道数据存储：反馈信息通过邮件和腾讯云COS双重保存
- 环境变量配置：所有敏感配置通过环境变量管理
- 支持Render一键部署

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
│           ├── index.html               # 首页模板
│           ├── second_page.html         # 问候页面模板
│           ├── quiz.html                # 问答页面模板
│           ├── feedback.html            # 反馈页面模板
│           ├── thank_you.html           # 感谢页面模板
│           └── thank_you_after_feedback.html  # 反馈后感谢页面模板
├── private_files/            # 私有文件目录（本地开发使用）
│   └── wechat_qr.jpg        # 微信二维码图片
├── static/                  # 静态文件目录
│   └── images/              # 图片资源
└── README.md                # 项目说明文件
```

## 用户流程

1. **首页问候**：用户输入姓名，获得个性化问候
2. **邀请探索**：邀请用户参与问答挑战
3. **问答挑战**：用户需回答预设问题，每题提供多个提示
4. **反馈收集**：通过验证后，用户可提交反馈信息
5. **隐私展示**：提交反馈后，展示受保护的微信二维码

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
   
   # 测验答案配置（JSON格式）
   QUIZ_ANSWERS=["答案1", "答案2", "答案3"]
   
   # 可选：腾讯云COS配置
   TENCENT_COS_SECRET_ID=your-secret-id
   TENCENT_COS_SECRET_KEY=your-secret-key
   TENCENT_COS_REGION=your-region
   TENCENT_COS_BUCKET=your-bucket-name
   
   # 可选：邮件配置（用于接收反馈）
   EMAIL_HOST=smtp.qq.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-email-password
   DEFAULT_FROM_EMAIL=your-email@example.com
   ```

5. 将您的微信二维码图片放入 `private_files/` 目录并命名为 `wechat_qr.jpg`

6. 运行开发服务器：
   ```bash
   cd WannaLearnMoreAboutYou
   python manage.py runserver
   ```

## 部署到 Render

1. 将代码推送到 GitHub 仓库（注意：不要将私密文件推送到 GitHub）

2. 在 Render 上创建新的 Web Service

3. 连接您的 GitHub 仓库

4. 配置环境变量：
   - SECRET_KEY
   - DEBUG (设置为 False)
   - ALLOWED_HOSTS (设置为您的 Render 应用域名)
   - QUIZ_ANSWERS (设置为包含正确答案的JSON数组)

5. 添加私密文件：
   - 在 Render 控制面板的 "Files" 部分添加新文件
   - Name: `wechat_qr`
   - Mount Path: `/etc/secrets/wechat_qr`
   - File Content: 上传您的微信二维码图片

6. 构建命令设置为：
   ```bash
   pip install -r requirements.txt
   ```

7. 启动命令设置为：
   ```bash
   gunicorn wannalearnmoreaboutyou.wsgi:application
   ```

## 安全特性

- 微信二维码存储在私有目录中，无法通过直接 URL 访问
- 二维码只能通过受保护的视图访问，需要通过测验验证
- 所有敏感配置通过环境变量管理，避免硬编码
- 使用 Django sessions 管理用户状态
- GitHub 仓库中不包含任何私密文件
- 反馈数据通过邮件和云存储双重备份

## 技术栈

- Django 4.2
- Python 3.x
- HTML/CSS (极简黑白灰设计风格)
- JavaScript (少量交互功能)
- 腾讯云COS (可选数据存储)
- SMTP (可选邮件发送)