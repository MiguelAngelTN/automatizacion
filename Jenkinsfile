// ===================================================================
// Jenkinsfile - Pipeline equivalente a .github/workflows/ci.yml
// Se entrega como alternativa de motor de CI (el enunciado acepta
// "Jenkinsfile" o ".github/workflows/ci.yml"). Ejecucion: mvn verify
// ===================================================================
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        JAVA_HOME = tool name: 'jdk17', type: 'jdk'
        MAVEN_OPTS = '-Dmaven.repo.local=.m2/repository'
        PROJECT_NAME = 'automatica-pruebas'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log --oneline -n 10'
            }
        }

        stage('Compilacion y pruebas unitarias (JUnit 5)') {
            steps {
                sh 'mvn -B clean test -Dgroups=unit'
            }
            post {
                always {
                    junit testResults: 'target/surefire-reports/*.xml', allowEmptyResults: true
                }
            }
        }

        stage('Pruebas BDD (Cucumber)') {
            steps {
                sh 'mvn -B verify -Dgroups=bdd -Djacoco.skip=true'
            }
            post {
                always {
                    junit testResults: 'target/cucumber-results.json', allowEmptyResults: true
                    publishHTML(target: [
                        reportDir : 'target/cucumber-report',
                        reportFiles : 'cucumber-report.html',
                        reportName : 'Reporte BDD Cucumber',
                        allowMissing : true,
                        alwaysLinkToLastBuild : true
                    ])
                    publishHTML(target: [
                        reportDir : 'target/allure-report',
                        reportFiles : 'index.html',
                        reportName : 'Reporte Allure',
                        allowMissing : true,
                        alwaysLinkToLastBuild : true
                    ])
                }
            }
        }

        stage('Metricas de cobertura (JaCoCo)') {
            steps {
                sh 'mvn -B verify -DskipTests'
                publishHTML(target: [
                    reportDir : 'target/site/jacoco',
                    reportFiles : 'index.html',
                    reportName : 'Cobertura JaCoCo',
                    allowMissing : true,
                    alwaysLinkToLastBuild : true
                ])
            }
        }

        stage('Prueba de performance (JMeter)') {
            steps {
                sh '''
                    mvn -B clean package -DskipTests
                    nohup java -cp target/classes \
                        com.empresa.pruebas.performance.ServidorPerformance 8080 > servidor.log 2>&1 &
                    echo $! > servidor.pid
                    sleep 5
                    jmeter -n -t performance/performance-login.jmx \
                        -l performance/resultados/login.jtl \
                        -e -o performance/reporte-html
                    kill $(cat servidor.pid) || true
                '''
                publishHTML(target: [
                    reportDir : 'performance/reporte-html',
                    reportFiles : 'index.html',
                    reportName : 'Reporte Performance JMeter',
                    allowMissing : true,
                    alwaysLinkToLastBuild : true
                ])
            }
        }

        stage('Dashboard de metricas y alertas') {
            steps {
                sh 'python3 scripts/generar-dashboard.py --salida dashboard/metricas.html'
                sh 'python3 scripts/verificar-umbrales.py --salida dashboard/estado-umbrales.json'
            }
            post {
                always {
                    publishHTML(target: [
                        reportDir : 'dashboard',
                        reportFiles : 'metricas.html',
                        reportName : 'Dashboard de Metricas',
                        allowMissing : true,
                        alwaysLinkToLastBuild : true
                    ])
                    archiveArtifacts artifacts: 'dashboard/*', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        failure {
            echo "FALLO: ${PROJECT_NAME} - se notifica al equipo via correo/Slack."
            // Alerta automatica ante fallos del pipeline
            sh 'echo "[ALERTA] Pipeline fallido en ${JOB_NAME} - ${BUILD_URL}"'
        }
        always {
            cleanWs(patterns: [[pattern: 'target', type: 'EXCLUDE']], deleteDirs: true)
        }
    }
}
