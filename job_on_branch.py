#!/usr/bin/python -O
# -*- coding: utf-8 -*-
from __future__ import print_function

import git
import re
from jenkinsapi.jenkins import Jenkins

import configuration as config


class JenkinsWorks:

    """
    Wrapper class that provides connection with Jenkins
    """

    def __init__(self):
        """
        JenkinsWorks constructor. Sets necessary variables
        """
        self.repo_path = config.repository_path
        self.jenkins_url = config.jenkins_url
        self.job_prefix = config.job_prefix
        self.job_suffix = config.job_suffix
        self.view_prefix = config.view_prefix
        self.view_suffix = config.view_suffix
        self.template_name = config.template_name
        self.existing_jobs = []
        self.existing_views = []
        self.branches = []
        self._get_api_instance()
        self._get_repo_origin()

    def _get_api_instance(self):
        """
        Get Jenkins API object
        """
        self.api = Jenkins(self.jenkins_url)
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
            if re.match(self.job_prefix + ".*" + self.job_suffix,
                        job_instance.name):
                self.existing_jobs.append(job_instance.name)
        return self.existing_jobs

    def get_existing_views(self):
        """
        Get existing Jenkins views that conform to the
        following convention: prefix + branch_name + suffix
        """
        for view_name in self.api.views.keys():
            if re.match(self.view_prefix + ".*" + self.view_suffix,
                        view_name):
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
        self.api.create_job(jobname=job_name, xml=xml)

    def delete_job(self, job_name):
        """
        Delete Jenkins job
        """
        print("Deleting job: %s" % job_name)
        self.api.delete_job(jobname=job_name)

    def create_view(self, view_name):
        """
        Create Jenkins view with specific view name
        """
        print("Creating view: %s" % view_name)
        view = self.api.views.create(view_name)
        return view

    def populate_view(self, view, job_name):
        """
        Add job to the Jenkins view
        """
        view.add_job(job_name)

    def delete_view(self, view_name):
        """
        Delete Jenkins view
        """
        print("Deleting view: %s" % view_name)
        del self.api.views[view_name]

    def update_jenkins_config(self):
        """
        Function that decides what Jenkins jobs and views
        should be created and what should be deleted
        """
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


def main():
    jenkins = JenkinsWorks()
    jenkins.get_existing_jobs_list()
    jenkins.get_existing_views()
    jenkins.get_branches()
    jenkins.update_jenkins_config()


if __name__ == '__main__':
    exit(main())
