pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    stages {
        stage('Clean checkout') {
            steps {
                deleteDir()
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh 'python3 -m venv .venv'
                sh '.venv/bin/python -m pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Compile application') {
            steps {
                sh '.venv/bin/python -m py_compile app.py tests/test_app.py'
            }
        }

        stage('Run tests') {
            steps {
                sh '.venv/bin/python -m pytest -q --junitxml=test-results.xml'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'test-results.xml'
        }
        success {
            echo 'Jenkins BUILD completed successfully.'
        }
        failure {
            echo 'Jenkins BUILD failed. Review the stage output.'
        }
    }
}
