#!/usr/bin/python -O
# -*- coding: utf-8 -*-
from __future__ import print_function

import git
import re
import argparse
import sys
from ConfigParser import SafeConfigParser
from jenkinsapi.jenkins import Jenkins


class JenkinsWorks:

    """
    Wrapper class that provides connection with Jenkins
    """

    def __init__(self, url, username, password,
                 repository_path, template_location, template_name,
                 job_prefix, job_suffix, view_prefix, view_suffix, preview):
        """
        JenkinsWorks constructor. Sets necessary variables
        """
        self.jenkins_url = url
        self.jenkins_username = username
        self.jenkins_password = password
        self.repo_path = repository_path
        self.template_name = template_name
        self.job_prefix = job_prefix
        self.job_suffix = job_suffix
        self.view_prefix = view_prefix
        self.view_suffix = view_suffix
        self.preview = preview
        self.existing_jobs = []
        self.existing_views = []
        self.branches = []
        self._get_api_instance()
        self._get_repo_origin()

    def _get_api_instance(self):
        """
        Get Jenkins API object
        """
        self.api = Jenkins(self.jenkins_url,
                           self.jenkins_username,
                           self.jenkins_password)
        return self.api

    def _get_repo_origin(self):
        """
        Get Git origin url
        """
        self.repo = git.Repo(self.repo_path)
        self.repo_url = self.repo.remotes.origin.url
        return self.repo_url

    def get_existing_jobs_list(self):
        """
        Get existing Jenkins job names that conform to the
        following convention: prefix + branch_name + suffix
        """
        for job in self.api.get_jobs():
            job_instance = self.api.get_job(job[0])
            if re.match(self.job_prefix + ".*" + self.job_suffix, job_instance.name):
                self.existing_jobs.append(job_instance.name)
        return self.existing_jobs

    def get_existing_views(self):
        """
        Get existing Jenkins views that conform to the
        following convention: prefix + branch_name + suffix
        """
        for view_name in self.api.views.keys():
            if re.match(self.view_prefix + ".*" + self.view_suffix, view_name):
                self.existing_views.append(view_name)
        return self.existing_views

    def get_branches(self):
        """
        Get all remote branches from Git
        """
        pattern = re.compile('[\w\d]+\trefs/heads/(.*)')
        output = self.repo.git.ls_remote("--heads").split("\n")
        for line in output:
            result = pattern.match(line)
            if result:
                self.branches.append(result.group(1))

        return self.branches

    def render_template(self, branch):
        """
        Render XML from the Jinja2 template
        """
        from jinja import FileSystemLoader
        from jinja.environment import Environment

        env = Environment()
        env.loader = FileSystemLoader('templates')
        template = env.get_template(self.template_name)
        rendered_xml = template.render(git_repo=self.repo_url,
                                       git_branch=branch)
        return rendered_xml

    def create_job(self, job_name, xml):
        """
        Create Jenkins job with specific job name and
        rendered from Jinja2 template XML
        """
        print("Creating job: %s" % job_name)
        if not self.preview:
            self.api.create_job(jobname=job_name,
                                xml=xml)

    def delete_job(self, job_name):
        """
        Delete Jenkins job
        """
        print("Deleting job: %s" % job_name)
        if not self.preview:
            self.api.delete_job(jobname=job_name)

    def create_view(self, view_name):
        """
        Create Jenkins view with specific view name
        """
        print("Creating view: %s" % view_name)
        if not self.preview:
            view = self.api.views.create(view_name)
            return view
        return view_name

    def populate_view(self, view, job_name):
        """
        Add job to the Jenkins view
        """
        print("Adding job %s to view %s" % (job_name, view.__str__()))
        if not self.preview:
            view.add_job(job_name)

    def delete_view(self, view_name):
        """
        Delete Jenkins view
        """
        print("Deleting view: %s" % view_name)
        if not self.preview:
            del self.api.views[view_name]

    def update_jenkins_config(self):
        """
        Function that decides what Jenkins jobs and views
        should be created and what should be deleted
        """
        if self.preview:
            print("Going to run in the PREVIEW mode")

        created_jobs = []
        created_views = []

        for branch in self.branches:
            job_name = self.job_prefix + branch + self.job_suffix
            view_name = self.view_prefix + branch

            if job_name not in self.existing_jobs:
                xml = self.render_template(branch)
                self.create_job(job_name, xml)

            if view_name not in self.existing_views:
                view = self.create_view(view_name)
                self.populate_view(view, job_name)

            created_jobs.append(job_name)
            created_views.append(view_name)

        for job in self.existing_jobs:
            if job not in created_jobs:
                self.delete_job(job)

        for view in self.existing_views:
            if view not in created_views:
                self.delete_view(view)


def parse_args():
    """
    Parse arguments from configuration file and command line
    """
    # The next block is done so the configuration file location can be passed
    # as a command-line parameter and it's content parsed and passed as default
    # values for the argparse
    configfile = None
    for idx, val in enumerate(sys.argv):
        if val == "-c" or val == "--config":
            configfile = sys.argv[idx + 1]
            break

    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument("-c", "--config",
                               dest="config_path",
                               type=str,
                               help="Path to configuration",
                               default="configuration.ini")
    if configfile:
        parent_args = parent_parser.parse_args(["-c", configfile])
    else:
        parent_args = parent_parser.parse_args([])

    config_parser = SafeConfigParser()
    config_parser.read(parent_args.config_path)

    parser = argparse.ArgumentParser(parents=[parent_parser])

    parser.add_argument("-a", "--address",
                        dest="jenkins_url",
                        type=str,
                        help="Jenkins server URL",
                        default=config_parser.get('jenkins', 'url'))
    parser.add_argument("-u", "--username",
                        dest="jenkins_username",
                        type=str,
                        help="Jenkins username",
                        default=config_parser.get('jenkins', 'username'))
    parser.add_argument("-p", "--password",
                        dest="jenkins_password",
                        type=str,
                        help="Jenkins password",
                        default=config_parser.get('jenkins', 'password'))
    parser.add_argument("-r", "--repository",
                        dest="repository_path",
                        type=str,
                        help="Git repository location",
                        default=config_parser.get('repository', 'path'))
    parser.add_argument("-t", "--template-name",
                        dest="template_name",
                        type=str,
                        help="Jenkins job template name",
                        default=config_parser.get('template', 'name'))
    parser.add_argument("--template-location",
                        dest="template_location",
                        type=str,
                        help="Jenkins job template location",
                        default=config_parser.get('template', 'location'))
    parser.add_argument("--job-prefix",
                        dest="job_prefix",
                        type=str,
                        help="Jenkins job prefix",
                        default=config_parser.get('job', 'prefix'))
    parser.add_argument("--job-suffix",
                        dest="job_suffix",
                        type=str,
                        help="Jenkins job suffix",
                        default=config_parser.get('job', 'suffix'))
    parser.add_argument("--view-prefix",
                        dest="view_prefix",
                        type=str,
                        help="Jenkins view prefix",
                        default=config_parser.get('view', 'prefix'))
    parser.add_argument("--view-suffix",
                        dest="view_suffix",
                        type=str,
                        help="Jenkins view suffix",
                        default=config_parser.get('view', 'suffix'))
    parser.add_argument("--dry-run", "--preview",
                        action="store_true",
                        dest="preview",
                        help="Execute script in preview mode, without actually modifying Jenkins configuration")

    args = parser.parse_args()
    return args

def main():
    """
    Execute useful code
    """

    args = parse_args()

    jenkins = JenkinsWorks(args.jenkins_url,
                           args.jenkins_username,
                           args.jenkins_password,
                           args.repository_path,
                           args.template_location,
                           args.template_name,
                           args.job_prefix,
                           args.job_suffix,
                           args.view_prefix,
                           args.view_suffix,
                           args.preview)
    jenkins.get_existing_jobs_list()
    jenkins.get_existing_views()
    jenkins.get_branches()
    jenkins.update_jenkins_config()

if __name__ == '__main__':
    main()
