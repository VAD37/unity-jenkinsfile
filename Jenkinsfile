def BUILD_TARGET = BuildTarget()

def BuildTarget() {
    if (env.BRANCH_NAME.toLowerCase().contains("ios")) {
        return "ios"
    }
    else {
        return "android"
    }
}

// Share pipeline between Windows and OS X because they both do same thing except build code
pipeline {
    agent { label BUILD_TARGET }
    //For some case you want to build some headless server with unity linux that build/run on AWS for testing.
    //Make another parralel stages that run only on slave machine with Linux Tags.
    options {
        //disableConcurrentBuilds()  //each branch has 1 job running at a time
        skipDefaultCheckout(true) // skip git default checkout because it call git clean -xffd. It clean all ignore files included cached unity /library folder. use custom git clean flags for faster build.
        buildDiscarder(logRotator(numToKeepStr: '300', artifactNumToKeepStr: '5')) // Default keep last 180 logs and latest 30 build artifacts. Will be override from Jenkins Settings website
    }

    stages {
        stage('Checkout') {
            steps {                
                //Debug: you never know what is missing on slave machine
                sh 'printenv | sort'
                // prevent null project init on new branch
                sh 'git init'
                sh 'git clean -ffd'
                sh 'git config core.ignorecase false' // For Mac unity user or you have serialized case sensitive file
                sh 'git config --list'                
                // Jenkins git fetch and pull
                checkout scm // the alternative to jenkins git plugin is sshagent[] and call checkout/clean by yourself
            }
        }
        stage('Prepare venv') {
            steps {
                script {
                    sh 'printenv | sort'
                    if (isUnix()) {
                        env.ISUNIX = "TRUE" // cache isUnix() function to prevent blueocean show too many duplicate step (Checks if running on a Unix-like node) in python function below
                        sh 'python3 -m venv pyenv'
                        PYTHON_PATH =  sh(script: 'echo ${WORKSPACE}/pyenv/bin/', returnStdout: true).trim()
                    }
                    else {
                        env.ISUNIX = "FALSE"
                        powershell(script:"py -3 -m venv pyenv") // window not allow call python3.exe with venv. https://github.com/msys2/MINGW-packages/issues/5001
                        PYTHON_PATH =  sh(script: 'echo ${WORKSPACE}/pyenv/Scripts/', returnStdout: true).trim()
                    }
                    
                    // Find unity root projects.
                    // If have multiple projects. Change */Assets to */NoSpace_Name/Assets
                    env.UNITY_PROJECT_ROOT = sh(script: "find . -type d -path '*/Library' -prune -false -o -name 'Assets' -prune | sed -e 's/......\$//' " , returnStdout:true).trim()

                    echo env.UNITY_PROJECT_ROOT

                    // Sometime agent with older pip version can cause error due to non compatible plugin.
                    // try  {                        
                    //     Python("-m pip install --upgrade pip")
                    // } 
                    // catch (ignore) { } // update pip always return false when already lastest version

                    Python("-m pip install -r $env.UNITY_PROJECT_ROOT/ci/requirements.txt")
                }                
            }
        }
        stage('Setup Enviroment') {
            steps {
                script {
                    Python(" -u  $env.UNITY_PROJECT_ROOT/ci/ConfigEnvironment.py ")
                    def available = Python(" $env.UNITY_PROJECT_ROOT/ci/VerifyUnityInstallation.py")
                    if (available == 1) {
                        timeout(time: 120, unit: 'MINUTES') {
                            echo 'Start Installing Unity'
                            // TODO move this to gem U3d by dragon. UnityHub cli not working on OS X
                            error('TODO install Unity version android + macos')
                        }
                    }
                    ExecuteAllPythonScriptsInDirectory("AfterUnitySetup")
                }
            }
        }
        stage('Build Project') {
            steps {
                script {
                    ExecuteAllPythonScriptsInDirectory("BeforeBuild")

                    withCredentials([string(credentialsId: 'UNITY_USERNAME', variable: 'UNITY_USERNAME'),
                                    string(credentialsId: 'UNITY_PASSWORD', variable: 'UNITY_PASSWORD')]) {
                        timeout(time: 180, unit: 'MINUTES') {
                            if (!isUnix()) {
                                def buildStatus = powershell([script: "$env.UNITY_PROJECT_ROOT/ci/UnityBuild.ps1 -config '$env.UNITY_PROJECT_ROOT/config.cfg' -quit -batchmode -username ${UNITY_USERNAME} -password ${UNITY_PASSWORD} ", returnStatus:true, label:'Build unity on Windows'])
                                if (buildStatus != 0) {
                                    currentBuild.result = 'FAILED'
                                    error 'Build Failed by Unity. Check above log for more detail'
                                }                                
                            }
                            else {
                                def shellCmd = GetConfig("UNITY_BUILD_COMMAND").trim()
                                def unixBuildStatus = sh([script: "${shellCmd} -username ${UNITY_USERNAME} -password ${UNITY_PASSWORD} ", returnStatus:true, label:'Build unity on Unix'])
                                if (unixBuildStatus != 0) {
                                    currentBuild.result = 'FAILED'
                                    error 'Build Failed by Unity. Check above log for more detail'
                                }
                            }
                        }
                    }             
                }                
            }
            post {
                always {
                    archiveArtifacts artifacts: "buildlog.txt , build/Android/* ,  Library/LastBuild.buildreport " , allowEmptyArchive: true
                    script {
                        ExecuteAllPythonScriptsInDirectory("AfterBuild")                        
                    }
                }
                failure {
                    script {
                        ExecuteAllPythonScriptsInDirectory("AfterBuildFailure")
                    }
                }
				success {
                    script {
                        ExecuteAllPythonScriptsInDirectory("AfterBuildSuccess")
                    }
                }
            }
        }
        // Only send test version to Test Flight.
        // Android send apk to Tester or aab to Test version
        stage('Publish') {
            environment {
                LC_ALL="en_US.UTF-8"
                LANG="en_US.UTF-8"
                FIREBASE_CLI_TOKEN = credentials('FIREBASE_CLI_TOKEN')
            }
            steps {
                script {
                    // android publisher jenkins plugin
                    env.DATETIME_TAG = java.time.LocalDateTime.now()
                    if( "${BUILD_TARGET}" == "android" && env.BRANCH_NAME.toLowerCase().contains("production"))
                    {
                        try {
                            androidApkUpload googleCredentialsId: 'google_publisher_account_unimob_global',
                                filesPattern: '**/build/Android/*.aab',
                                trackName: 'internal',
                                rolloutPercentage: '100',
                                usePreviousExpansionFilesIfMissing: true,
                                recentChangeList: [[language: 'en-GB', text: "Update ${env.BUILD_NUMBER} ${env.DATETIME_TAG}"]]
                        } catch (err) {
                            echo err.getMessage()
                        }
                    }

                    if ("${BUILD_TARGET}" == "ios")
                    {
                        def xcode_dir = "build/iOS"
                        // dir function only take sub path so use special format if project not in root .git folder
                        if("$env.UNITY_PROJECT_ROOT" != '' && "$env.UNITY_PROJECT_ROOT" != '/' && "$env.UNITY_PROJECT_ROOT" != ' ') {
                            xcode_dir = "$env.UNITY_PROJECT_ROOT/build/iOS"
                        }

                        dir(xcode_dir) 
                        {
                            sh "printenv | sort"
                            sh "yes | cp -rf ../ci/FastLaneFiles/. ."
                            withCredentials([string(credentialsId: 'KEYCHAIN_PASSWORD', variable: 'KEYCHAIN_PASSWORD'),
                                            string(credentialsId: 'FASTLANE_PASSWORD', variable: 'FASTLANE_PASSWORD'),
                                            string(credentialsId: 'FASTLANE_USER', variable: 'FASTLANE_USER'),
                                            string(credentialsId: 'MATCH_PASSWORD', variable: 'MATCH_PASSWORD')]) 
                            {
                                sshagent (credentials: ['appstore_github'])
                                {
                                    // Enable below code if fastlane still cant find ssh key. It add all ssh in ~/.ssh key if jenkins have sudo power (you shouldnt give CI sudo. fastlane cant run in sudo shell)
                                    // sh "ssh-add -A"
                                    sh "printenv | sort"

                                    // For proper keychain setup with fastlane. Create new keychain user in macbook with custom password. login.keychain is the default keychain
                                    // That included all login for appstore, github, and certification use for fastlane.
                                    // sh "security list-keychains"
                                    sh(script:'security -v unlock-keychain -p "${KEYCHAIN_PASSWORD}" ~/Library/Keychains/login.keychain', label: 'Unlock Keychain')
                                    // sh "security list-keychains"

                                    def lane = "beta"
                                    if( env.BRANCH_NAME.toLowerCase().contains("production"))
                                        lane = "publish"

                                    sh(script:"fastlane ${lane} --verbose 2>&1 | tee ${workspace}/fastlane_log.txt ; ( exit \${PIPESTATUS[0]} )", label: 'Fastlane')
                                }
                            }
                        }
                    }
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: "build/iOS/*.ipa", fingerprint: true, allowEmptyArchive: true
                    script {
                        ExecuteAllPythonScriptsInDirectory("AfterPublishSuccess")
                    }
                }
                always {
                    archiveArtifacts artifacts: "fastlane_log.txt" , allowEmptyArchive: true
                }
                failure {
                    script {
                        ExecuteAllPythonScriptsInDirectory("AfterPublishFailure")
                    }
                }
            }
        }
    }
}

// Think of this like python stage that jenkins dont care about. Just execute.
def ExecuteAllPythonScriptsInDirectory(String subDirectory) {
    try {
        Python("-u $env.UNITY_PROJECT_ROOT/ci/RunAllPythonScript.py ${subDirectory}")
    } catch (err) {
        echo err.getMessage()
        unstable "Python script have errors. Mark stage as unstable"
    }
}

// Get and Set is the same as Load .groovy into global env
// This method is more convenient since config allow commucation between python and pipeline code. 
// Make it easy to replicate in local without running pipeline
def GetConfig(String configKey) {
    return sh(script:". $env.UNITY_PROJECT_ROOT/config.cfg && echo \$${configKey}", returnStdout:true)
}


def SetConfig(String configKey, String configValue) {
    sh """    
    sed -i "/${configKey} =/d" $env.UNITY_PROJECT_ROOT/config.cfg
    echo '${configKey}=${configValue}'  >> $env.UNITY_PROJECT_ROOT/config.cfg
    """
}


// Several plugins like WithPyenv is not working perfectly accross platform when using Virtual Env.
// Do the venv manually this way is much better.
def Python(String command) {
    if (env.ISUNIX == "TRUE") {
        sh script:". pyenv/bin/activate && python ${command}", label: "python ${command}"
    }
    else {
        powershell script:"pyenv\\Scripts\\Activate.ps1 ; python ${command}", label: "python ${command}"
    }
}