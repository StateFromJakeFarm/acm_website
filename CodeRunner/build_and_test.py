import os
import filecmp
import subprocess

# Get info on this run from environment variables
source_file = os.environ['SUBMISSION_FILE']
time_limit = float(os.environ['TIME_LIMIT'])

# Compile/interpret commands for supported languages
compile_cmds_dict = {
    'cpp': 'g++ {} -std=c++14 -o prog',
    'cc': 'g++ {} -std=c++14 -o prog',
    'c': 'gcc {} -std=c99 -o prog',
}
interpreter_cmds_dict = {
    'py': 'python3 {}'
}

# Get compilation command (if need be)
ext = source_file.split('.')[-1]
compile_cmd = compile_cmds_dict.get(ext)

run_cmd = None
if compile_cmd:
    # Try to compile
    compile_cmd = compile_cmd.format(source_file)
    try:
        subprocess.run(compile_cmd, shell=True, check=True)
        run_cmd = './prog'
    except subprocess.CalledProcessError as e:
        print('Error: Build failed')
        exit(1)
else:
    # Find out which interpretter to use
    run_cmd = interpreter_cmds_dict.get(ext)

if not compile_cmd:
    if not run_cmd:
        print('Error: Unrecognized file extension')
        exit(1)
    else:
        # Format interpretter run command
        run_cmd = run_cmd.format(source_file)

# Run tests
my_out_file = 'my.out'
my_err_file = 'my.err'
cmd_list = run_cmd.split(' ')
i = 1 # Loop over each testfile
while os.path.exists('tests/t%02d.in' % i):
    in_file = 'tests/t%02d.in' % i
    ans_file = 'tests/t%02d.ans' % i

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
