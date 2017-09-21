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
    stage('Create Group Triggers`') {
      steps {
       sh 'python perf_testing/mock_group_trigger.py'
      }
    }

    stage('Grab Events') {
      steps {
            sh 'locust -f perf_testing/events_miq.py --host $HAWKULAR_HOST --port $HAWKULAR_PORT -r $MIQ_CLIENTS_RATE -c $MIQ_CLIENTS  --print-stats --no-web   --only-summary'
      }
    }
  }
}
