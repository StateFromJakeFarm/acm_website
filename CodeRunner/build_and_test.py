import os
import filecmp
import subprocess

# Get info on this run from environment variables
source_file = os.environ['SUBMISSION_FILE']
time_limit = float(os.environ['TIME_LIMIT'])

# Get our compilation command (if need be)
ext = source_file.split('.')[-1]
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
my_out_file = 'my.out'
my_err_file = 'my.err'
i = 1
while os.path.exists('tests/t%02d.in' % i):
    in_file = 'tests/t%02d.in' % i
    ans_file = 'tests/t%02d.ans' % i

    cmd_list = run_cmd.split(' ')

    print('Testcase {}: '.format(i), end='')
    try:
        # Run program
        subprocess.run(cmd_list, stdin=open(in_file), stdout=open(my_out_file, 'w'),
            stderr=open(my_err_file, 'w'), timeout=time_limit)

        # Check output
        err = open(my_err_file).read()
        if len(err):
            print('Error:\n{}'.format(err))
        elif filecmp.cmp(my_out_file, ans_file):
            print('Passed')
        else:
            print('Failed')
    except subprocess.TimeoutExpired as e:
        print('Timeout')

    i += 1
