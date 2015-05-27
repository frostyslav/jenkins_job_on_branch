jenkins_job_on_branch
=======================

Python script, that generates Jenkins job and view when new branch is pushed to Git.

Job XML is being generated from the Jinja2 template.
Sample job template requires the following plugins:
1. Build Flow
2. EnvInject
3. Git Client

Configuration options are defined in `configuration.py`

License and Authors
-------------------

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
