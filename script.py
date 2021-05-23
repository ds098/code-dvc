'''The code is all about , how to keep a track on large files ,
it can push the large files to cloud storage and create a reference of that in the github, 
and also can pull the files from that cloud storage, it extracts the information from 
config.json regarding the token, repo_name, feature_branch, templates_path, weight_file_path, user, push/pull/update and drive_id.'''
#importing libraries 
import os
import time
from github import Github 
import subprocess
import json

from github.Repository import Repository 

#Creating a log file for logs in write mode 
log=open('log.txt','w')

#opening the config.json file and loading it into a data variable as a dictionary to extract the information 
with open('config.json') as file:
    data=json.loads(file.read())
    try:                                             
        token=data['github_token']
        user=data['user']
        Reattempt_time = data['Reattempt_time']
        Reattempt_count = data['Reattempt_count']
        log.write('user and token information received')
    except:
        log.write('github token error, or user error')
        print('github token error')
        print()

#Requesting access for github by creating an object 
g=Github(f"{token}") 

#Returns a file in the current path with the the dvc tracked file          
def pull():
    with open('config.json') as file:
        data=json.loads(file.read())
        try:
            repo_name=data['repo_name']
            feature_branch = data['feature_branch']
            log.write('\nfeature_branch and repo_name information received')
        except:
            log.write('\nfeature_branch and repo_name not present in config file')
            print('error with config file, restart the process')
            return 
    f = os.getcwd()
    e = os.listdir(f'{f}')
    if feature_branch in e:
        print("your branch is already pulled")
        log.write('\nyour branch is already created')
    elif repo_name in e:
        directory = feature_branch
        parent_dir = os.getcwd()
        path = os.path.join(f'{parent_dir}', f'{directory}')
        os.makedirs(path)
        os.chdir(path)
        os.system(f'git clone --single-branch --branch {feature_branch} https://github.com/{user}/{repo_name}.git')
        os.chdir(f'{repo_name}')
        if (os.system(f'dvc pull -r myremote')) == 0:
            print("pulled")
            log.write('\nbranch pulled successfully')
        else:
            c = 1
            while(os.system('dvc pull -r myremote')):
                time.sleep(Reattempt_time) 
                Reattempt_count = Reattempt_count - 1
                if (Reattempt_count) == 0:
                    c = 0 
                    print("Your internet is off , please on the connection")
                    log.write("\nInternet is off")
                    break
    else:
        os.system(f'git clone --single-branch --branch {feature_branch} https://github.com/{user}/{repo_name}.git')
        os.chdir(f'{repo_name}')
        if (os.system(f'dvc pull -r myremote')) == 0:
            print("pulled")
            log.write('\nbranch pulled successfully')
        else:
            c = 1
            while(os.system('dvc pull -r myremote')):
                time.sleep(Reattempt_time) 
                Reattempt_count = Reattempt_count - 1
                if (Reattempt_count) == 0:
                    c = 0 
                    print("Your internet is off , please on the connection")
                    log.write("\nInternet is off")
                    break

#It creates a repository in the github account 
def create_repo():
    with open('config.json') as file:
        data=json.loads(file.read())
        try:
            repo_name=data['repo_name']
            templates_path=data['templates_path']
        except:
            log.write('repo name not found in config file')
            print('repo name not found in config file')
    try:
        user=g.get_user()
        repo=user.create_repo(repo_name)
    except:
        print("repo created")

#it updates the master branch with the template for the above created repository
def update_templates():
    with open('config.json') as file:
        data=json.loads(file.read())
        try:             
            templates_path=data['templates_path'] 
            repo_name = data['repo_name']   
            print('Updated master branch')
            log.write('\n updated master branch')    
        except:
            log.write('templates path and repo_name config not found')
        
#         templates_path = input()
    os.chdir(templates_path)
    # repo = g.get_user().get_repo('jingle')
    # repo.create_file('file.txt', "committing files", 'hi my name is nishant', branch="master")
    h = os.listdir(templates_path)
    matching = [True for i in h if ".git" in i]
    if True in matching:
        print("already git initialised")
        log.write('\n git is already initialised for this template, create another template')
    else:
        os.system('git init')
        os.system('git add *')
        os.system('git commit -m "templates added"')
        os.system(f'git remote add origin https://github.com/{user}/{repo_name}.git')
        os.system('git push -u origin master')

#It creates the branch for an already existing repository and 
# track, push the large files into the cloud and the reference into the git repository specific branch     
def create_branch():
#         repo_name=input()
    with open('config.json') as file:
        data=json.loads(file.read())
        try:
            weight_file_path = data['weight_file_path']
            repo_name=data['repo_name']
            Reattempt_time = data['Reattempt_time']
            Reattempt_count = data['Reattempt_count']
        except:
            log.write('\n repo name in log file not found')
            print('repo_name not found in log file')
    with open('config.json') as file:
        try:
            feature_branch=data['feature_branch']
            id = data['drive_id']        
        except:
            log.write('\n feature_branch not found in config file')
    c = id
    os.chdir(weight_file_path)
    d = os.listdir(weight_file_path)
    matching = [True for i in d if ".dvc" in i]
    if True in matching:
        print("path is already dvc initialised, choose some else path")
        log.write('\n path is already dvc initialised, choose some else path')
    else:
        os.system('git init')
        os.system('dvc init')
        os.system('git add readme.md readme.json')
        os.system('dvc add zip.zip')
        os.system('git add .gitignore zip.zip.dvc')
        if (os.system(f'dvc remote add myremote gdrive://{c}')) == 0:
            log.write('\ndvc remote added')
        else:
            log.write('\nerror with dvc remote, check it')
            print('error with dvc remote, check it')
        os.system('git add .dvc/config')
        if (os.system('dvc push -r myremote')) == 0:
            os.system('git commit -m "v2"')
            os.system(f'git branch -M {feature_branch}')
            if (os.system(f'git remote add origin https://github.com/{user}/{repo_name}.git')) == 0:
                    log.write('\n continue...')
            else:
                log.write('\norigin not added, might be an issue with repo name in config file, check repo')
                print('origin not added, might be an issue with repo name in config file, check repo')
            os.system(f'git push -u origin {feature_branch}')
            print("created successfully")
            log.write("\n branch created")
        else:
            c = 1
            while(os.system('dvc push -r myremote')):
                time.sleep(Reattempt_time) 
                Reattempt_count = Reattempt_count - 1
                if (Reattempt_count) == 0:
                    c = 0 
                    print("Your internet is off , please on the connection")
                    log.write("\nInternet is off")
                    break
            if c == 1:
                os.system('git commit -m "v2"')
                os.system(f'git branch -M {feature_branch}')
                if (os.system(f'git remote add origin https://github.com/{user}/{repo_name}.git')) == 0:
                    log.write('\n continue...')
                else:
                    log.write('\norigin not added, might be an issue with repo name in config file, check repo')
                    print('origin not added, might be an issue with repo name in config file, check repo')
                os.system(f'git push -u origin {feature_branch}')
                print("created successfully")
                log.write("\n branch created")

#It creates a Repository with a master branch having readme.json and readme.md
def create():
    s = os.getcwd()
    create_repo()
    update_templates()
    os.chdir(f'{s}')

#It'll update the changes ,if any , done by the user in the dvc tracked file 
def update():
    with open('config.json') as file:
        data = json.loads(file.read())
        weight_file_path = data['weight_file_path']
    os.chdir(f'{weight_file_path}')
    os.system('dvc add zip.zip')
    os.system('git add zip.zip.dvc')
    os.system('git commit -m "File updated"')
    os.system('dvc push -r myremote')
    os.system('git push')

     
#def push():  
    # print('wanna push/update master branch or feature_branch. Input master/feature')
    # entry=input()
    # if entry.lower()=='master':
    #     update_templates()
    #     print('master branch updated successfully')
    # elif entry.lower()=='feature_branch':
    #     create_branch()
    #     print('feature branch created successfully')
    # else:
    #     print('invalid input . Please provide the input amongst the listed options only')
    #     push()
        



# with open('config.json') as file:
#     data=json.loads(file.read())
#     user=data['user']
#     repo_name = data['repo_name']
# repo = g.get_repo(f"{user}/{repo_name}")
# content = repo.get_contents("")
# content = [i.name for i in content]
# print(content)


#It'll check whether the repository is there in the given github account or not , if there , then it would 
# push the files in the respective 
if __name__== "__main__":
    with open('config.json') as file:
        data = json.loads(file.read())
        try:
            repo_name=data['repo_name']
            command=data['command']
            feature_branch = data['feature_branch']
        except:
            log.write('\nrepo name or user in log file not found')
            print('repo_name not found in config file')
    Repository=g.get_user().get_repos()
    Repository=[i.name for i in list(Repository)]
    # repo = g.get_repo(f"{user}/{repo_name}")
    # content = repo.get_contents("")
    # content = [i.name for i in content]
    if command.lower()=='push':
        if repo_name in Repository:
            create_branch()
        else:
            create()
            create_branch()
    elif command.lower()=='pull':
        if repo_name in Repository:
            pull()
    else:
        update()


      

        # if repo_name in Repository:
        #     pull()
        # else:
        #     print("Repo name is wrong ")
        #     log.write("\n please feed the correct repo name")

        




# entry=input().lower()    
# if entry=="pull":
#     log.write("pull requested /n")
#     pull()
#     print('contents pulled successfully')
# elif entry=='push':
#     log.write('push requested /n')
#     push()
# elif entry=='create':
#     log.write('creation requested /n')
#     create()
#     print('repo created successfully')
#     update_templates()
#     print('templates updated successfully')
# else:
#     log.write('invalid input recieved')
#     print('INVALID INPUT, run the script again and provide correct input amongst the three')    
    