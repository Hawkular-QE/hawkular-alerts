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

      when {
         environment name: 'MIQ_REQUESTS ', value: 'true'
        }
        steps {
              sh 'locust -f roles/perf_testing/events_miq.py --host $HAWKULAR_HOST --port $HAWKULAR_PORT -r $MIQ_CLIENTS_RATE -c $MIQ_CLIENTS --print-stats --no-web -n $NUM_REQUESTS  --only-summary'
        }

        when {
           environment name: 'MIQ_REQUESTS ', value: 'false'
          }
        steps {
              sh 'locust -f roles/perf_testing/events_miq.py --host $HAWKULAR_HOST --port $HAWKULAR_PORT -r $MIQ_CLIENTS_RATE -c $MIQ_CLIENTS --print-stats --no-web  --only-summary'
        }
      }
     }
    }
