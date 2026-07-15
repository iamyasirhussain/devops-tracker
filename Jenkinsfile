pipeline {
    // Run the whole pipeline inside a Python 3.12 container.
    // The HP box only has 3.10 — this makes the build independent of the host.
    agent {
        docker {
            image 'python:3.12-slim'
            // Run as root inside the container so pip can install freely.
            args '-u root'
        }
    }

    stages {
        stage('Install dependencies') {
            steps {
                sh 'pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                sh 'ruff check .'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest -v'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
    }
}
