import base64
from os.path import abspath

import conf
import gitlab

from .GitLabRepo import GitLabRepo
import requests


class SKAGitLab(gitlab.Gitlab):
    def __init__(self):
        gitlab.Gitlab.__init__(self, 'https://gitlab.com',
                               private_token=conf.gitlab_token)

    def list_gitlab_repositories(self):
        gl = SKAGitLab()

        group = gl.groups.get(3180705)  # Group ID of ska-telescope

        projects = group.projects.list(
            all=True, order_by="name", sort="asc", include_subgroups=True)

        return projects

    def list_ska_users(self):
        gl = SKAGitLab()
        # developer.skatelescope.org project ID
        return gl.projects.get(9070656).members.all(all=True)

    def create_gitlab_repo(self, project_name, maintainer_ids, template):
        group_id = 3180705

        gl = SKAGitLab()

        params = {'name': project_name,
                  'namespace_id': group_id, 'visibility': "public"}
        if template:
            params['use_custom_template'] = True
            params['group_with_project_templates_id'] = 5901724
            params['template_name'] = template

        project = gl.projects.create(params)

        # Share project with SKA Reporters group:
        project.share(6051772, gitlab.REPORTER_ACCESS)

        # Share project with SKA Developers group:
        project.share(6051706, gitlab.DEVELOPER_ACCESS)

        # Add maintainer users
        if maintainer_ids[0] is not None:
            for user_id in maintainer_ids:
                try:
                    member = project.members.create(
                        {'user_id': user_id, 'access_level': gitlab.MAINTAINER_ACCESS})
                except Exception as e:
                    print(e)
                    print("User ID: " + str(user_id))
                    print("Project: " + str(project.id))

        if template:
            clone_ska_python_skeleton()

        result = project._attrs

        return result

    def clone_ska_python_skeleton(self):
        pass

    def make_readthedocs_mr(self, project_id):
        gl = SKAGitLab()
        branch_name = 'readthedocs-update-auto-created'
        project = gl.projects.get(project_id)
        # Prepare commit to a new branch
        data = {
            'branch': branch_name,
            'commit_message': 'add docs folder from ska-python-skeleton',
            'start_branch': 'master',
            'actions': []
        }

        files = ['docs/Makefile', 'docs/src/_static/css/custom.css', 'docs/src/_templates/footer.html', 'docs/src/_templates/layout.html', 'docs/src/package/guide.rst',
                 'docs/src/conf.py', 'docs/src/index.rst']
        binary_files = ['docs/src/_static/img/favicon.ico',
                        'docs/src/_static/img/logo.jpg', 'docs/src/_static/img/logo.svg']
        for file in files:
            file_exists = self.check_file(project_id=project_id, file=file)
            if file_exists:
                data['actions'].append({
                    'action': 'update',
                    'file_path': file,
                    'content': open('docs_template/' + file, 'r').read(),
                })
            else:
                data['actions'].append({
                    'action': 'create',
                    'file_path': file,
                    'content': open('docs_template/' + file, 'r').read(),
                })
        for file in binary_files:
            file_exists = self.check_file(project_id=project_id, file=file)
            if file_exists:
                data['actions'].append({
                    'action': 'update',
                    'file_path': file,
                    'content': base64.b64encode(open('docs_template/' + file, 'rb').read()),
                })
            else:
                data['actions'].append({
                    'action': 'create',
                    'file_path': file,
                    'content': base64.b64encode(open('docs_template/' + file, 'rb').read()),
                })
        project.commits.create(data)
        print("\tCommit successfull")
        # Create the MR
        description = """ This MR is auto-created by the system team to update your projects documentation.
        
Your project does not have the files(**docs/index.rst, docs/conf.py** or **docs/src/index.rst, docs/src/conf.py** or **docs/source/index.rst, docs/source/conf.py**) which are necessary for *readthedocs* to render your project documentation.

You can find more information on how to document your code on https://developer.skatelescope.org/en/latest/projects/document_project.html. *Note that your project is already imported to the Read the Docs.*

**Important:** There is a manual step that needs to be done before merging this request if you only have a readme file.
A symlink needs to be created for the README file of your project.
You can use the following commands:

```
cd docs/src
ln -s <path to your README>
```

You will use probably: `ln -s ../../README.md`

*Note:** This MR could override some of the existing files in your docs folder, please review if this is the case.

You can contact the system team if you have any questions.


"""
        maintainers = [f"@{member.username}" for member in project.members.list(
        ) if member.access_level >= 40]
        if not maintainers:
            print("Empty Maintainers... adding limonkufu")
            maintainers = ['@limonkufu']
        description = description + ",".join(maintainers)

        project.mergerequests.create(
            {
                'source_branch': branch_name,
                'target_branch': 'master',
                'title': 'WIP: ReadtheDocs Documentation Update (auto created)',
                'description': description,
                'remove_source_branch': True
            }
        )
        print("\tMR successfull")

    def check_docs(self, project_id):
        header = {"Authorization": "Bearer " + conf.gitlab_token}
        header['Content-Type'] = "application/json"

        url = "https://gitlab.com/api/v4/projects/"
        path = "/repository/files/docs%2F"
        path_list_src = ["src%2Findex.rst?ref=master",
                         "src%2Fconf.py?ref=master"]
        path_list = ["index.rst?ref=master", "conf.py?ref=master"]
        path_list_source = ["source%2Findex.rst?ref=master",
                            "source%2Fconf.py?ref=master"]

        path_exists = True
        for file in path_list:
            response = requests.get(
                url + str(project_id) + path + file, headers=header)
            # print(response.status_code)
            if response.status_code == 404:
                path_exists = False
        # print(path_exists)

        path_src_exists = True
        for file in path_list_src:
            response = requests.get(
                url + str(project_id) + path + file, headers=header)
            # print(response.status_code)
            if response.status_code == 404:
                path_src_exists = False
        # print(path_src_exists)

        path_source_exists = True
        for file in path_list_source:
            response = requests.get(
                url + str(project_id) + path + file, headers=header)
            # print(response.status_code)
            if response.status_code == 404:
                path_source_exists = False
        # print(path_source_exists)

        return path_exists or path_src_exists or path_source_exists

    def check_file(self, file, project_id):
        header = {"Authorization": "Bearer " + conf.gitlab_token}
        header['Content-Type'] = "application/json"

        url = "https://gitlab.com/api/v4/projects/"
        path = "/repository/files/"
        file = file.replace("/", "%2F")
        response = requests.get(
            url + str(project_id) + path + file + '?ref=master', headers=header)
        return response.status_code == 200
