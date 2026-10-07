pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            reuseNode true
        }
    }

    options {
        disableConcurrentBuilds()
    }

    stages {
        stage('Install dependencies') {
            steps {
                sh 'python -m pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Compile application') {
            steps {
                sh 'python -m py_compile app.py tests/test_app.py'
            }
        }

        stage('Run tests') {
            steps {
                sh 'python -m pytest -q --junitxml=test-results.xml'
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
