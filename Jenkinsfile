pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate Python') {
    steps {
        bat '"C:\\Users\\Lakshmi\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" --version'
        bat '"C:\\Users\\Lakshmi\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m py_compile app.py'
    }
}

        stage('Check Docker') {
    steps {
        bat '"C:\\Users\\Lakshmi\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" --version'
        bat '"C:\\Users\\Lakshmi\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe" info'
    }
}

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t smart-parking-app:latest .'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Smart Parking project built successfully!'
        }
        failure {
            echo 'BUILD FAILED: Check the first red error in the Jenkins Console Output.'
        }
    }
}