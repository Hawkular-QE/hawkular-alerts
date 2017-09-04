pipeline {
  agent any
  stages {
    stage('Python Config') {
      steps {
        sh 'python -v'
      }
    }
    stage('Check Path and User') {
      steps {
        sh 'whoami'
        sh 'pwd'
      }
    }
    stage('Locust Execution') {
      steps {
        parallel(
          "Soak Test": {
            sh 'locust -f roles/perf_testing/events_miq.py --host $HAWKULAR_HOST --port $HAWKULAR_PORT -r $MIQ_CLIENTS_RATE -c $MIQ_CLIENTS --print-stats --no-web'

          },
          "Gather Logs from Hawkular Services Pods": {
            sh '''eval "$(ssh-agent -s)"

cd ../../

ssh-add cfme-mw-qe.pem

HAWKULAR_POD=$(ssh root@$HAWKULAR_HOST  docker ps -q | awk 'NR==1')

ssh root@$HAWKULAR_HOST docker logs $HAWKULAR_POD -f'''

          },
          "Gather Logs from Cassandra Pod": {
            sh '''eval "$(ssh-agent -s)"

cd ../../

ssh-add cfme-mw-qe.pem

CASSANDRA_POD=$(ssh root@$HAWKULAR_HOST  docker ps -q | awk 'NR==2')

ssh root@$HAWKULAR_HOST docker logs $CASSANDRA_POD -f'''

          }
        )
      }
    }
  }
}
