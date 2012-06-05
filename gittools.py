from datetime import datetime
from git import *
from errBot import PLUGIN_DIR
from utils import human_name_for_git_url
import os
import logging
import shutil

GIT_LOCAL_STORAGE = PLUGIN_DIR + os.sep + 'git_repos' + os.sep


def human_to_path(human_name):
    return GIT_LOCAL_STORAGE + human_name

def clone(url):
    human_name = human_name_for_git_url(url)
    g = Git()
    g.clone(url, human_to_path(human_name), bare=True)
    return human_name

def remove_repo(human_name):
    path = human_to_path(human_name)
    shutil.rmtree(path)

def fetch_all_heads(human_name):
    path = human_to_path(human_name)
    g = Git(path)
    logging.debug('fetch_all_heads from %s' % path)
    remote_heads_string = g.ls_remote('origin', heads=True)
    branches = [line.split('/')[-1] for line in remote_heads_string.split('\n')]
    repo = Repo(path)
    origin = repo.remotes.origin
    result = []
    for branch in branches:
        logging.debug('fetching = %s' % branch)
        result.extend(origin.fetch('%s:%s' % (branch, branch)))

    logging.debug('result = %s' % result)
    return result

def get_heads_revisions(human_name):
    path = human_to_path(human_name)
    repo = Repo(path)
    heads = repo.heads
    return [(h.name, h.commit.binsha) for h in heads]

def history_since_rev(human_name, previous_heads_revisions):
    repo = Repo(human_to_path(human_name))
    heads = repo.heads
    result = []
    for head_name, previous_commit in previous_heads_revisions:
        commit = heads[head_name].commit
        while commit.binsha != previous_commit:
            result.append(commit)
            logging.debug('%s' % commit.hexsha)
            commit = commit.parents[0]
    return result

# Represents a list of commits as a log as a list of strings
def git_log(commits):
    return ["%s %20s %20s -- %s" % (commit.hexsha[:6], commit.author.name, datetime.fromtimestamp(commit.committed_date).isoformat() ,commit.summary) for commit in commits]