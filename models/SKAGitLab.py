import gitlab
from .GitLabRepo import GitLabRepo
import conf
import base64


class SKAGitLab(gitlab.Gitlab):
    def __init__(self):
        gitlab.Gitlab.__init__(self, 'https://gitlab.com',
                               private_token=conf.gitlab_token)

    def list_gitlab_repositories(self):
        gl = SKAGitLab()

        group = gl.groups.get(3180705)  # Group ID of ska-telescope

        projects = group.projects.list(all=True, order_by="name", sort="asc", include_subgroups=True)

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

    def make_readthedocs_mr(self):
        gl = SKAGitLab()
        branch_name = 'readthedocs-auto-created'
        project = gl.projects.get(18252924)

        # Prepare commit to a new branch
        data = {
            'branch': branch_name,
            'commit_message': 'add docs folder from ska-python-skeleton',
            'start_branch': 'master',
            'actions': [
                {
                    'action': 'create',
                    'file_path': 'docs/Makefile',
                    'content': open('docs_template/docs/Makefile', 'r').read(),
                },
                {
                    'action': 'create',
                    'file_path': 'docs/src/_static/css/custom.css',
                    'content': open('docs_template/docs/src/_static/css/custom.css', 'r').read(),
                },
                {
                    # Binary files need to be base64 encoded
                    'action': 'create',
                    'file_path': 'docs/src/_static/img/favicon.ico',
                    'content': base64.b64encode(open('docs_template/docs/src/_static/img/favicon.ico', 'rb').read()),
                    'encoding': 'base64',
                },
                {
                    # Binary files need to be base64 encoded
                    'action': 'create',
                    'file_path': 'docs/src/_static/img/logo.jpg',
                    'content': base64.b64encode(open('docs_template/docs/src/_static/img/logo.jpg', 'rb').read()),
                    'encoding': 'base64',
                },
                {
                    # Binary files need to be base64 encoded
                    'action': 'create',
                    'file_path': 'docs/src/_static/img/logo.svg',
                    'content': base64.b64encode(open('docs_template/docs/src/_static/img/logo.svg', 'rb').read()),
                    'encoding': 'base64',
                },
                {
                    'action': 'create',
                    'file_path': 'docs/src/_static/js/github.js',
                    'content': open('docs_template/docs/src/_static/js/github.js', 'r').read(),
                },
                {
                    'action': 'create',
                    'file_path': 'docs/src/_templates/footer.html',
                    'content': open('docs_template/docs/src/_templates/footer.html', 'r').read(),
                },
                {
                    'action': 'create',
                    'file_path': 'docs/src/_templates/layout.html',
                    'content': open('docs_template/docs/src/_templates/layout.html', 'r').read(),
                },
                {
                    'action': 'create',
                    'file_path': 'docs/src/package/guide.rst',
                    'content': open('docs_template/docs/src/package/guide.rst', 'r').read(),
                },
                {
                    'action': 'create',
                    'file_path': 'docs/src/conf.py',
                    'content': open('docs_template/docs/src/conf.py', 'r').read(),
                },
                {
                    'action': 'create',
                    'file_path': 'docs/src/index.rst',
                    'content': open('docs_template/docs/src/index.rst', 'r').read(),
                }
            ]
        }
        commit = project.commits.create(data)

        # Create the MR
        description = """ This MR is auto created to update your projects documentation.
        Your project does not have **docs** folder which is necessary for *readthedocs* to render the project documentation.
        
        
        You can find more information on how to document your code on https://developer.skatelescope.org/en/latest/index.html
        
        **Important:** There is a manual step that needs to be done before merging this request.
        A symlink needs to be created for the README file of your project.
        You can use the following command:
        
        `ln -s <path to your README>`
        
        You will use probably: `ln -s ../../README.md`
        """

        mr = project.mergerequests.create(
            {
                'source_branch': branch_name,
                'target_branch': 'master',
                'title': 'WIP: ReadtheDocs Documentation Update (auto created by the system team)',
                'description': description,
                'remove_source_branch': True
            }
        )

        # Mark the MR as todo
        mr.todo()
