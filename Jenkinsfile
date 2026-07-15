pipeline {
    // No default agent — each stage chooses its own.
    agent none

    environment {
        IMAGE = 'ghcr.io/iamyasirhussain/devops-tracker'
    }

    stages {
        stage('Lint & Test') {
            // Needs Python 3.12 — the host only has 3.10, so use a container.
            agent {
                docker {
                    image 'python:3.12-slim'
                    args '-u root'
                }
            }
            steps {
                sh 'pip install --no-cache-dir -r requirements.txt'
                sh 'ruff check .'
                sh 'pytest -v'
            }
        }

        stage('Build & Push image') {
            // Needs Docker, not Python — so run directly on the HP box.
            agent any
            steps {
                // withCredentials injects the secret ONLY inside this block,
                // and masks it in the logs.
                withCredentials([usernamePassword(
                    credentialsId: 'ghcr-creds',
                    usernameVariable: 'GHCR_USER',
                    passwordVariable: 'GHCR_TOKEN'
                )]) {
                    sh '''
                        echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
                        docker build -t $IMAGE:jenkins .
                        docker push $IMAGE:jenkins
                        docker logout ghcr.io
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
    }
}
