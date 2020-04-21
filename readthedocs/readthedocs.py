import json

import conf
import requests


class ReadtheDocs:
    def __init__(self, token=conf.readthedocs_token):
        self.headers = {"Authorization": "Token " + token}
        self.base_url = "https://readthedocs.org/api/v3/"

    def base(self):
        """Simple query just to check connection"""
        return requests.get(self.base_url)

    def extend_headers(self, ):
        self.headers['Content-Type'] = "application/json"

    def get_projects_for_user(self):
        all_projects = []
        url = self.base_url + 'projects'
        response = requests.get(url, headers=self.headers)
        result = response.json()
        all_projects.extend(result['results'])
        # check pagination
        while(result['next'] is not None):
            url = result['next']
            response = requests.get(url, headers=self.headers)
            result = response.json()
            all_projects.extend(result['results'])

        return all_projects

    def make_subproject(self, parent, child, alias):
        url = self.base_url + 'projects/' + parent + '/subprojects/'
        self.extend_headers()
        body = {
            "child": child,
            "alias": alias
        }
        payload = json.dumps(body)
        response = requests.post(url, data=payload, headers=self.headers)
        return response

    def update_project(self, slug, name, repo_url, language, programming_language):
        url = self.base_url + 'projects/' + slug +'/'
        self.extend_headers()
        body = {
            "name": name,
            "repository": {
                "url": repo_url,
                "type": "git"
            },
            "language": language,
            "programming_language": programming_language
        }
        payload = json.dumps(body)
        response = requests.patch(url, data=payload, headers=self.headers)
        return response

    def get_subprojects(self, parent):
        sub_projects = []
        url = self.base_url + 'projects/' + parent + '/subprojects/'
        self.extend_headers()
        response=requests.get(url=url, headers=self.headers)
        result=response.json()
        sub_projects.extend(result['results'])
        # check pagination
        while(result['next'] is not None):
            url = result['next']
            response = requests.get(url, headers=self.headers)
            result = response.json()
            sub_projects.extend(result['results'])
        return sub_projects


