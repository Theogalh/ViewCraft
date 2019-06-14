def get_version():
    from subprocess import Popen, PIPE
    try:
        p = Popen(['git', 'describe', '--tags', '--abbrev=6'], stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        version = p.stdout.readlines()[0]
        version = version.strip().decode('utf8').split('-')[0]
        return version
    except:
        return '42'


if __name__ == '__main__':
    print(get_version())
