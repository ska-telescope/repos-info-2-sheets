import json
from os.path import normcase
import pprint
import time

from models import ReadtheDocsProject
from models.ReadtheDocsProject import ReadthedocsProject
from models.SKAGitLab import SKAGitLab

pp = pprint.PrettyPrinter(indent=4)

print("------------- Sub Projects-------------")
rtd_sub_projects = ReadtheDocsProject.list_of_developerportal_subprojects()
pp.pprint([proj.slug for proj in rtd_sub_projects])
print("------------- Sub Projects-------------")

print("------------ GITLAB REPOS -----------------")
gitlab = SKAGitLab()
gitlab_repositories = gitlab.list_gitlab_repositories()
pp.pprint([repo.path for repo in gitlab_repositories])
print("------------ GITLAB REPOS -----------------")

rtd_sub_projects_set = set([proj.slug for proj in rtd_sub_projects])
gitlab_repositories_set = set([repo.path for repo in gitlab_repositories])

print("------------ REPOS THAT MATCH -----------------")
match_set = rtd_sub_projects_set & gitlab_repositories_set
pp.pprint(match_set)
print("------------ REPOS THAT MATCH -----------------")

print("------------ REPOS THAT WILL BE DELETED -----------------")
rtd_sub_projects_diff = rtd_sub_projects_set - match_set
pp.pprint(rtd_sub_projects_diff)
print("------------ REPOS THAT WILL BE DELETED -----------------")

print("------------ REPOS THAT NEEDS TO BE ADDED -----------------")
gitlab_repositories_diff = gitlab_repositories_set - match_set
pp.pprint(gitlab_repositories_diff)
print("------------ REPOS THAT NEEDS TO BE ADDED -----------------")


# projects_to_update = {}
# for repo in gitlab_repositories:
#     time.sleep(2)
#     rtdp = ReadthedocsProject(name=repo.path_with_namespace.replace("/", "-"), repo_url=repo.web_url)
#     result = rtdp.create_project()
#     projects_to_update[rtdp.slug] = repo.path
#     print("\n\nProject created - " + rtdp.name + ": " + str(result))
#     if result != "Internal Server Error":
#         print("\tProject created with slug: " + rtdp.slug)
#         rtdp.name = repo.name
#         result_update = rtdp.update_project()
#         print("\tProject updated: " + str(result_update))

    
# for repo in gitlab_repositories:
#     projects_to_update[repo.path_with_namespace.replace("/", "-")] = repo.path   
# ReadtheDocsProject.make_subprojects(projects=projects_to_update)




# Step 1: Delete readthe docs project that do not have the same slugs as gitlab slugs:
#   rtd_sub_projects_diff (MANUAL)

# # Step 2: Update readthedocs projects to gitlab repo
# rtd_sub_projects_linking_github = [proj for proj in rtd_sub_projects if "github" in proj.repo_url]
# pp.pprint([f"{proj.slug} - {proj.maintainers}" for proj in rtd_sub_projects_linking_github])
# for proj in rtd_sub_projects_linking_github:
#     for repo in gitlab_repositories:
#         if repo.path == proj.slug:
#             proj.repo_url = repo.http_url_to_repo
#             print(f"Repo will be updated: {repo.path}")
#     proj.update_project()
#
# # Step 3: Add missing gitlab projects to readthedocs (gitlab_repositories_diff)
# for repo in gitlab_repositories:
#     if repo.path not in match_set:
#         time.sleep(1)
#         rtdp = ReadthedocsProject(name=repo.path, repo_url=repo.web_url, slug=repo.path)
#         print(f"Repo will be created: {rtdp.slug}")
#         result = rtdp.create_project()
#         print("Create:\n"+ str(result))
#         if(result != "Internal Server Error"):
#             rtdp.name = repo.name
#             result2 = rtdp.update_project()
    # print("Update:\n"+result2)
    #
    # Step 4: Add readthedocs docs folder to gitlab projects that don't have it
    # Step 4.1: Check if the repo has docs folder? Or check the build status from readthedocs
    #   To check if the repo has conf.py in docs folder: https://docs.gitlab.com/ee/api/repository_files.html
    #   because python-gitlab does not support this api endpoint
    #   To check the build status from readthedocs, we need the last build and and it "success" field.
    #   But this does not mean it was always successfull
    #   OR we could check if any of the versions has their "built" field as true meaning at least one version was successfull

    # Step 4.2: Add the docs folder and create a MR
    # repo.make_readthedocs_mr()

# # count = 0
# for repo in gitlab_repositories:
#     # count = count + 1
#     time.sleep(0.2)
#     print(f"{count}. {repo.name}:")
#     if not gitlab.check_docs(repo.id):
#         # if count >= 110:
#         print("\tMR!")
#         gitlab.make_readthedocs_mr(repo.id)
#     # else:
#     #     print(f"{repo.name}")
