"""Update repositories."""
import argparse
import os


GIT_FETCH_ALL = 'fetch --all --prune'
GIT_FETCH_TAG = 'fetch --prune origin "refs/tags/*:refs/tags/*"'
GIT_PULL = 'pull'
GIT_REF_GET = 'for-each-ref --format=\'delete %(refname)\' refs/original'
GIT_REF_UPDATE = 'update-ref --stdin'
GIT_EXPIRE = 'reflog expire --expire=now --all'
GIT_GC = 'gc --prune=now'


def _dec_ref(prev):
    return prev - 1 if prev > 0 else prev


def _gc_git(path):
    print('==collecting %s==' % path)
    git_exec = 'git -C %s' % path
    os.system('%s %s | %s %s' % (
        git_exec, GIT_REF_GET, git_exec, GIT_REF_UPDATE))
    os.system('%s %s' % (git_exec, GIT_EXPIRE))
    os.system('%s %s' % (git_exec, GIT_GC))


def _gc_svn(path):
    _ = path


def _update_git(path, do_gc=False):
    print('==updating %s==' % path)
    git_exec = 'git -C %s ' % path
    os.system(git_exec + GIT_FETCH_ALL)
    os.system(git_exec + GIT_FETCH_TAG)
    os.system(git_exec + GIT_PULL)
    _ = do_gc and _gc_git(path)


def _update_svn(path, do_gc=False):
    os.system('svn up %s' % path)
    _ = do_gc and _gc_svn(path)


def _iterate_dir(in_dir, depth, do_gc=False):
    if depth == 0:
        return
    for entry in os.listdir(in_dir):
        entry_path = os.path.join(in_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        if os.path.isdir(os.path.join(entry_path, '.git')):
            _update_git(entry_path, do_gc)
        elif os.path.isdir(os.path.join(entry_path, '.svn')):
            _update_svn(entry_path, do_gc)
        else:
            _iterate_dir(entry_path, _dec_ref(depth), do_gc)


def iterate_dir(in_dir, depth, do_gc=False):
    """Iterate the directory for repositories."""
    if not os.path.isdir(in_dir):
        print('%s is not a directory.' % in_dir)
        return
    _iterate_dir(in_dir, depth, do_gc)


def _parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'target', type=str,
        help='Target directory.'
    )
    parser.add_argument(
        '-gc', action='store_true',
        help='Do garbage collection as well.'
    )
    return parser.parse_args()


if __name__ == '__main__':
    FLXG = _parse_argument()
    iterate_dir(FLXG.target, -1, FLXG.gc)
