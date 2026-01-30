• 仓库结构总览

  - 顶层布局（关键目录/文件）
      - tubetube/：后端与前端静态资源（核心代码）
      - config/：默认 YAML 配置样例（运行时会被覆盖/重写）
      - scripts/：离线脚本工具
      - start.sh / start_config.py：容器启动入口与 gunicorn 配置
      - Dockerfile / requirements.txt：运行环境与依赖
      - data/：默认数据输出目录（运行时写入）
  - 入口（运行方式）
      - 容器/生产：start.sh → gunicorn tubetube.tubetube:app -c start_config.py（监听 0.0.0.0:6543）
      - 直接运行：tubetube/tubetube.py 中 web_app.run_app()（监听 0.0.0.0:8500）
      - 工具脚本：scripts/process_vtt.py（独立 CLI，不是主服务入口）
  - 核心模块（职责）
      - tubetube/tubetube.py：Flask + Socket.IO 网页入口、事件路由；WebApp 继承 Settings 与 DownloadManager
      - tubetube/settings.py：配置路径解析、settings.yaml 读取与默认落盘、文件夹分类与创建
      - tubetube/yt_downloader.py：下载队列、线程池、yt‑dlp 参数构建、进度回传、取消/移除逻辑
      - tubetube/helpers.py：URL 解析、yt‑dlp 后处理器（剪裁描述）
      - tubetube/vtt_tool.py：VTT 字幕解析与清洗（供脚本使用）
      - tubetube/templates/index.html + tubetube/static/*.js + tubetube/static/style.css：前端 UI 与 Socket.IO
        通讯
  - 依赖关系（内部 + 外部）
      - 内部关系
          - tubetube/tubetube.py → tubetube/settings.py + tubetube/yt_downloader.py
          - tubetube/yt_downloader.py → tubetube/helpers.py + tubetube/
            settings.py（DownloadCancelledException）
          - scripts/process_vtt.py → tubetube/vtt_tool.py
      - 配置/数据流
          - Settings 优先使用 TUBETUBE_CONFIG_DIR / TUBETUBE_DATA_DIR，否则优先 /config、/data，再回退到仓库内
            config/、data/
          - DownloadManager 从 TUBETUBE_APP_CONFIG 或 config/app_config.yaml 读配置；环境变量覆盖
      - 关键第三方
          - 后端：flask, flask_socketio, gunicorn, gevent, gevent-websocket
          - 下载：yt_dlp[default]
          - 配置：pyyaml
          - 字幕处理（脚本可选）：opencc-python-reimplemented
          - 前端：Bootstrap + Socket.IO CDN（写在 index.html）

