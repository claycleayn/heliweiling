pipeline {
    agent any

    // 定义环境变量
    environment {
        IMAGE_NAME = "esports-flask-server"
        CONTAINER_NAME = "esports-cloud-api"
        PORT_MAPPING = "5000:5000"
    }

    stages {
        stage('1. 拉取最新代码 (Git Pull)') {
            steps {
                echo '>>> 正在从 Gitee/GitLab 获取最新提交的服务器代码...'
                // 实际环境中这里由 Jenkins 自动完成 git checkout
                checkout scm
            }
        }

        stage('2. 清理旧版本容器 (Stop & Remove)') {
            steps {
                echo '>>> 正在停止并删除旧版本的云端服务器容器...'
                sh '''
                    # 如果容器存在则停止并删除，允许失败(|| true)以免首次运行报错
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                '''
            }
        }

        stage('3. 构建新镜像 (Docker Build)') {
            steps {
                echo '>>> 正在根据最新代码重构 Docker 镜像...'
                sh 'docker build -t ${IMAGE_NAME}:latest .'
            }
        }

        stage('4. 一键部署与重启 (Docker Run)') {
            steps {
                echo '>>> 正在拉起全新版本的云端服务器...'
                // 挂载 server_logs 目录以保证日志和数据文件持久化
                sh '''
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${PORT_MAPPING} \
                        -v $(pwd)/server_logs:/app/server_logs \
                        ${IMAGE_NAME}:latest
                '''
                echo '✅ 云端服务器代码“一键”更新和重启完成！'
            }
        }
    }
}