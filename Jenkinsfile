pipeline {
  agent any

  options {
    colors('xterm')
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }

  environment {
    DOCKER_REGISTRY_URL = 'ghcr.io' 
    DOCKER_USERNAME = credentials('etd-container-registry-username')
    DOCKER_PASSWORD = credentials('etd-container-registry-password')

    IMAGE_NAME = 'ghcr.io/ano-etd/airflow'
  }

  stages {
    stage('Download latest requirements artifact') {
      steps {
        copyArtifacts(
          projectName: 'АНО ЕТД/airflow-dags/master',
          filter: 'requirements.txt',
          selector: lastSuccessful(),
          target: '.',
          flatten: true
        )
      }
    }

    stage('Create requirements verification script') {
      steps {
        script {
          def verificationScript = '''
import sys
import pkg_resources

def verify_requirements(requirements_file):
    try:
        with open(requirements_file, 'r') as f:
            # Filter out comments and empty lines to avoid parsing errors
            lines = [line.strip() for line in f 
                     if line.strip() and not line.strip().startswith('#')]
            
        # This will raise exceptions if requirements are missing or conflicting
        pkg_resources.require(lines)
        
        print(f"SUCCESS: All requirements in {requirements_file} are satisfied.")
        sys.exit(0)
        
    except pkg_resources.DistributionNotFound as e:
        print(f"FAILURE: Package missing: {e}")
        sys.exit(1)
    except pkg_resources.VersionConflict as e:
        print(f"FAILURE: Version conflict: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to parse or verify requirements: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_requirements.py <requirements.txt>")
        sys.exit(1)
    verify_requirements(sys.argv[1])
          '''

          writeFile file: 'verify_requirements.py',
                    text: verificationScript
        }
      }
    }

    stage('Check dependencies diff') {
      agent {
        docker {
          image 'ghcr.io/ano-etd/airflow:latest'
          args '-u root'
          alwaysPull true
        }
      }
      steps {
        script {
          def exitCode = sh(
            script: 'python3 verify_requirements.py requirements.txt',
            returnStatus: true
          )

          env.REQ_DIFF_FOUND = (exitCode != 0).toString()

          echo "Comparison finished. Differences found: ${env.REQ_DIFF_FOUND}"
        }
      }
    }

    stage('Build new airflow image') {
      when { expression { return env.REQ_DIFF_FOUND == 'true' } }
      steps {
        script {
          def shortSha = env.GIT_COMMIT.take(7)

          echo "Requirements changed. Building new image with tag: ${shortSha}"

          sh 'echo $DOCKER_PASSWORD | docker login ${DOCKER_REGISTRY_URL} -u $DOCKER_USERNAME --password-stdin'

          sh "docker build -t ${IMAGE_NAME}:${shortSha} -t ${IMAGE_NAME}:latest ."

          sh "docker push ${IMAGE_NAME}:${shortSha}"
          sh "docker push ${IMAGE_NAME}:latest"
        }
      }
      post {
        success {
          archiveArtifacts artifacts: 'requirements.txt',
                           fingerprint: true
        }
      }
    }

    stage('Trigger gitops build job') {
      when { expression { return env.REQ_DIFF_FOUND == 'true' } }
      steps {
        script {
          echo "Triggering GitOps job with SHA tag: ${env.NEW_IMAGE_TAG}"

          build job: 'АНО ЕТД/gitops/master',
                parameters: [
                  string(name: 'AIRFLOW_IMAGE_TAG', value: env.NEW_IMAGE_TAG)  
                ],
                wait: false
        }
      }
    }
  }
}
