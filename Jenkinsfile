pipeline {
  agent any
  stages {
    stage('Python Config') {
      steps {
        sh 'python -v'
      }
    }
    stage('Openshift Hawkular Alerts') {
      openshiftScale(namespace: 'alerts', deploymentConfig: 'alerts',replicaCount: '10')
    }
    stage('Check Path and User') {
      steps {
        sh 'whoami'
        sh 'pwd'
      }
    }
    stage('Create Group Triggers`') {
      steps {
        sh 'python perf_testing/mock_group_trigger.py'
      }
    }
    stage('Grab Events') {
      steps {
        parallel(
          "Grab Events": {
            sh 'locust -f perf_testing/events_miq.py --host $HAWKULAR_HOST --port $HAWKULAR_PORT -r $MIQ_CLIENTS_RATE -c $MIQ_CLIENTS  --print-stats --no-web   --only-summary'

          },
          "Send Data as Hawkular Agent": {
            sh 'locust -f perf_testing/mock_agent.py -c 100 -r 0.01 --no-web --host ${HAWKULAR_HOST}'

          }
        )
      }
    }
  }
}
