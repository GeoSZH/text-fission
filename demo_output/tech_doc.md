
        # Docker 容器化技术指南

        Docker 是一个开源的容器化平台，允许开发者将应用程序和其依赖项打包到轻量级、可移植的容器中。

        ## 核心概念

        ### 容器 (Container)
        容器是 Docker 镜像的运行实例。每个容器都是独立的，包含运行应用程序所需的所有文件、依赖项和配置。

        ### 镜像 (Image)
        Docker 镜像是一个只读模板，包含创建容器所需的指令。镜像可以基于其他镜像构建，也可以从头开始创建。

        ### Dockerfile
        Dockerfile 是一个文本文件，包含构建 Docker 镜像的指令。它定义了基础镜像、安装依赖项、复制文件、设置环境变量等步骤。

        ## 基本命令

        ### 构建镜像
        ```bash
        docker build -t myapp:latest .
        ```

        ### 运行容器
        ```bash
        docker run -d -p 8080:80 myapp:latest
        ```

        ### 查看容器状态
        ```bash
        docker ps
        docker ps -a
        ```

        ## 最佳实践

        1. **使用多阶段构建**：减少最终镜像大小
        2. **优化层缓存**：合理安排 Dockerfile 指令顺序
        3. **安全性考虑**：使用非 root 用户运行容器
        4. **资源限制**：设置内存和 CPU 限制
        