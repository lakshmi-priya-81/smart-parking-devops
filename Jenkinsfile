pipeline {
    agent any
    options { timestamps(); disableConcurrentBuilds() }
    environment {
        IMAGE_NAME = 'smart-parking-app'
        CONTAINER_NAME = 'smart-parking-app'
        HOST_PORT = '5001'
    }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Install dependencies') {
            steps { sh 'python3 -m pip install --user -r requirements.txt' }
        }
        stage('Automated tests') {
            steps { sh 'python3 -m pytest -v test_app.py' }
        }
        stage('Build Docker image') {
            steps { sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .' }
        }
        stage('Deploy container') {
            steps {
                sh '''docker rm -f ${CONTAINER_NAME} || true
                docker volume create parking_data
                docker run -d --name ${CONTAINER_NAME} --restart unless-stopped -p ${HOST_PORT}:5000 -v parking_data:/app/data ${IMAGE_NAME}:${BUILD_NUMBER}'''
            }
        }
        stage('Smoke test') {
            steps {
                sh '''python3 -c 'import time,urllib.request; time.sleep(4); print(urllib.request.urlopen("http://localhost:${HOST_PORT}/health", timeout=5).read().decode())' '''
            }
        }
    }
    post { always { echo 'Review Console Output and record actual test/build results.' } }
}
