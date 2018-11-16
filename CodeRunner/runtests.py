import os
import filecmp
import subprocess

i = 1
while os.path.exists('tests/t%02d.in' % i):
    in_file = 'tests/t%02d.in' % i
    out_file = 'tests/t%02d.ans' % i

    cmd = './a.out < {} > myout.out'.format(in_file)
    subprocess.run(cmd, shell=True)

    print('Testcase {}: '.format(i), end='')
    if filecmp.cmp('myout.out', out_file):
        print('Passed')
    else:
        print('Failed')

    i += 1
