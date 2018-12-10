import os
import filecmp
import subprocess

source_file = os.environ['SUBMISSION_FILE']
ext = source_file.split('.')[-1]

# Get our compilation command (if need be)
compile_cmd = {
    'cpp': 'g++ {} -std=c++14 -o prog'.format(source_file),
    'cc': 'g++ {} -std=c++14 -o prog'.format(source_file),
    'c': 'gcc {} -std=c99 -o prog'.format(source_file)
}.get(ext)

run_cmd = None
if compile_cmd:
    # Try to compile
    try:
        subprocess.run(compile_cmd, shell=True, check=True)
        run_cmd = './prog'
    except subprocess.CalledProcessError as e:
        print('Build failed:\n' + e.stderr)
        exit(1)
else:
    # Find out which interpretter to use
    run_cmd = {
        'py': 'python3 {}'.format(source_file)
    }.get(ext)

if not compile_cmd and not run_cmd:
    print('Unrecognized file extension.')
    exit(1)

# Run tests
i = 1
while os.path.exists('tests/t%02d.in' % i):
    in_file = 'tests/t%02d.in' % i
    out_file = 'tests/t%02d.ans' % i

    cmd = '{} < {} > my.out'.format(run_cmd, in_file)

    print('Testcase {}: '.format(i), end='')
    try:
        subprocess.run(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        continue

    if filecmp.cmp('my.out', out_file):
        print('Passed')
    else:
        print('Failed')

    i += 1
