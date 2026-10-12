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
                bat 'py -3 --version'
                bat 'py -3 -m py_compile app.py'
            }
        }

        stage('Check Docker') {
            steps {
                bat 'docker --version'
                bat 'docker info'
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