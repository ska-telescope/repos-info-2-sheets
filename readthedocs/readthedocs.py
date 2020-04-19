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
            url = url + result['next'].split("/api/v3/projects",1)[1] # split the next link (/api/v3/projects/?limit....)
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


