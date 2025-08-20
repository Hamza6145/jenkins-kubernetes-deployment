pipeline {
    agent any

    environment {
        dockerimagename = "hamza6145/my-python-project-app:latest"
        registryCredential = 'dockerhub-credentials'
        dockerImage = ""
    }

    stages {
        stage('Checkout Source') {
            steps {
                git 'https://github.com/Hamza6145/jenkins-kubernetes-deployment.git'
            }
        }

        stage('Build Image') {
            steps {
                script {
                    dockerImage = docker.build(dockerimagename)
                }
            }
        }

        stage('Push Image') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', registryCredential) {
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy to Kubernetes (Minikube)') {
            steps {
                script {
                    sh 'kubectl apply -f k8s/deployment.yaml'
                    sh 'kubectl apply -f k8s/service.yaml'
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful!"
        }
        failure {
            echo "❌ Deployment failed!"
        }
    }
}
