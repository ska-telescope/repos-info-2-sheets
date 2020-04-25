import json
import requests

from readthedocs.readthedocs import ReadtheDocs
import time


class ReadthedocsProject:
    def __init__(self, name, repo_url, slug="", url="", language="en", programming_language="words"):
        self.slug = slug
        self.name = name
        self.url = url
        self.repo_url = repo_url
        self.is_subproject = False
        self.language = language
        self.programming_language = programming_language
        self.maintainers = []

    def get_subproject(self, subproject_of):
        if subproject_of is None:
            self.is_subproject = False
        else:
            if subproject_of['id'] == 216769:  # developer portal
                self.is_subproject = True

    def create_project(self, test_sub=False):
        """
        Create a Project on ReadtheDocs. Minimal list of fields to be included:
        {
        "name": "Test Project",
        "repository": {
            "url": "https://github.com/readthedocs/template",
            "type": "git"
        },
        "homepage": "http://template.readthedocs.io/",
        "programming_language": "py",
        "language": "es"
    }
        :return: Response Text
        """

        rtd = ReadtheDocs()

        # Construct the Payload
        body = {"name": self.name}
        repodetails = {"url": self.repo_url, "type": "git"}
        body["repository"] = repodetails
        body["programming_language"] = self.programming_language
        body["language"] = self.language

        payload = json.dumps(body)

        # Projects URL
        url = rtd.base_url + 'projects/'

        # specify JSON app type
        rtd.extend_headers()
        try:
            response = requests.request(
                "POST", url, data=payload, headers=rtd.headers)

            if response.status_code == 201:
                result = json.loads(response.text)
                self.slug = result['slug']
                self.url = result['repository']['url']
                self.language = result['language']['code']
                self.programming_language = result['programming_language']['code']

            else:
                result = response.reason
        except Exception as e:
            print(e)
            result = e

        if test_sub:
            parent = "devdeveloperskatelescopeorg"
        else:
            parent = "developerskatelescopeorg"

        # try:
        #     alias = str.replace(self.slug, "ska-telescope-", "")
        #     # rtd.make_subproject(parent=parent, child=self.slug, alias=alias) # make subproject
        # except Exception as e:
        #     print(e)
        #     result = e

        return result

    def update_project(self):
        rtd = ReadtheDocs()
        try:
            response = rtd.update_project(slug=self.slug, name=self.name, repo_url=self.repo_url,
                                          language=self.language, programming_language=self.programming_language)
            if response.status_code != 204:
                result = response.reason
            else:
                result = response.status_code
        except Exception as e:
            print(e)
            result = e
        return result

    def get_subprojects(self):
        rtd = ReadtheDocs()
        sub_projects = []
        try:
            results = rtd.get_subprojects(parent=self.slug)
            for res in results:
                rtd_project = ReadthedocsProject(res['name'], res['slug'], res['urls']['documentation'],
                                                 res['repository']['url'])
                rtd_project.get_subproject(res['subproject_of'])
                rtd_project.maintainers = [user['username'] for user in res['users']]
                # TODO: Check subproject of developer portal
                sub_projects.append(rtd_project)

        except Exception as e:
            print(e)
        return sub_projects


def list_of_readthedocs_projects(non_sub_only=False):
    readthedocs = ReadtheDocs()

    projects = []

    results = readthedocs.get_projects_for_user()

    for res in results:
        rtd_project = ReadthedocsProject(name=res['name'], repo_url=res['repository']['url'], slug=res['slug'],
                                         url=res['urls']['documentation'], language=res['language'][
            'code'], programming_language=res['programming_language']['code']
        )
        rtd_project.get_subproject(res['subproject_of'])
        rtd_project.maintainers = [user['username'] for user in res['users']]
        if non_sub_only:
            if not rtd_project.is_subproject:
                projects.append(rtd_project)
        else:
            projects.append(rtd_project)

    return projects


def list_of_developerportal_subprojects():
    rtd = ReadtheDocs()
    sub_projects = []
    try:
        results = rtd.get_subprojects(parent="developerskatelescopeorg")
        for res in results:
            res = res['child']
            rtd_project = ReadthedocsProject(name=res['name'], repo_url=res['repository']['url'], slug=res['slug'],
                                             url=res['urls']['documentation'], language=res['language'][
                                                 'code'], programming_language=res['programming_language']['code']
                                             )
            rtd_project.is_subproject = True
            rtd_project.maintainers = [user['username'] for user in res['users']]
            sub_projects.append(rtd_project)

    except Exception as e:
        print(e)
    return sub_projects


def make_subprojects(parent="developerskatelescopeorg", projects = {}):
    """ Make subprojects of each of the ReadtheDocs projects in the list projects

    @:param: projects: list of slugs of projects to be made subprojects
    @:param: parent: parent project
    """

    readthedocs = ReadtheDocs()
    for slug, alias in projects.items():
        time.sleep(2)
        print(f"{slug}->{alias}: {readthedocs.make_subproject(parent, slug, alias).status_code}")


def create_readthedocs_project(name_with_namespace, repository, prog_lang, lang, test_sub):

    readthedocs_project = ReadthedocsProject(
        name=name_with_namespace,
        repo_url=repository,
        language=lang, programming_language=prog_lang
    ).create_project(test_sub)

    return readthedocs_project


if __name__ == '__main__':
    # pp.pprint([proj.name for proj in list_of_projects(True)])
    # pp.pprint(readthedocs.get_projects_for_user)

    # make_subproject()
    rtdp = ReadthedocsProject("Test Project", programming_language="py",
                              repo_url="https://gitlab.com/ska-telescope/test-project.git")
    print(rtdp.create_project())
    make_subprojects(parent="devdeveloperskatelescopeorg",
                     project_slugs=['test-project'])

    # var = rtdp.explanation()
    # print(json.dumps(var))
