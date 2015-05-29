##jenkins_job_on_branch.py

Python script, that generates Jenkins job and view when new branch is pushed to Git.

Job XML is being generated from the Jinja2 template.
Sample job template requires the following plugins:
* Build Flow
* EnvInject
* Git Client

Configuration options can be defined in the `configuration.ini` file or via the command line.
Script support several options, that can be listed by passing `--help` option to the script.
Script can be run in the preview mode without actually modifiying anything by passing `--dry-run` or `--preview` to the command line.

##Usage:
```text
usage: job_on_branch.py [-h] [-c CONFIG_PATH] [-a JENKINS_URL]
                        [-u JENKINS_USERNAME] [-p JENKINS_PASSWORD]
                        [-r REPOSITORY_PATH] [-t TEMPLATE_NAME]
                        [--template-location TEMPLATE_LOCATION]
                        [--job-prefix JOB_PREFIX] [--job-suffix JOB_SUFFIX]
                        [--view-prefix VIEW_PREFIX]
                        [--view-suffix VIEW_SUFFIX] [--dry-run]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_PATH, --config CONFIG_PATH
                        Path to configuration
  -a JENKINS_URL, --address JENKINS_URL
                        Jenkins server URL
  -u JENKINS_USERNAME, --username JENKINS_USERNAME
                        Jenkins username
  -p JENKINS_PASSWORD, --password JENKINS_PASSWORD
                        Jenkins password
  -r REPOSITORY_PATH, --repository REPOSITORY_PATH
                        Git repository location
  -t TEMPLATE_NAME, --template-name TEMPLATE_NAME
                        Jenkins job template name
  --template-location TEMPLATE_LOCATION
                        Jenkins job template location
  --job-prefix JOB_PREFIX
                        Jenkins job prefix
  --job-suffix JOB_SUFFIX
                        Jenkins job suffix
  --view-prefix VIEW_PREFIX
                        Jenkins view prefix
  --view-suffix VIEW_SUFFIX
                        Jenkins view suffix
  --dry-run, --preview  Execute script in preview mode, without actually
                        modifying Jenkins configuration
```

##License and Authors

- Author:: Rostyslav Fridman (rostyslav.fridman@gmail.com)

```text
Copyright 2015, Rostyslav Fridman

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
