from ..generic import Enum

__all__ = ('REPO_TYPE', 'REPOS_TYPE')

REPO_TYPE = (  'git', 
               'g-common',
               'cvs' ,
               'subversion',
               'rsync',
               'tar',
               'bzr',
               'mercurial',
               'darcs',
             )

REPOS_TYPE = Enum(REPO_TYPE)
