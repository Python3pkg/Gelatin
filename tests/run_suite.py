#!/usr/bin/env python3
# Copyright (c) 2010-2017 Samuel Abels
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import sys
import unittest
import glob
import fnmatch
import re
from inspect import isfunction, ismodule, isclass


def uppercase(match):
    return match.group(1).upper()

correlated = dict()


def correlate_class(theclass):
    """
    Checks the given testcase for missing test methods.
    """
    if not hasattr(theclass, 'CORRELATE'):
        return

    # Collect all functions in the class or module.
    for name, value in list(theclass.CORRELATE.__dict__.items()):
        if not isfunction(value):
            continue
        elif name == '__init__':
            name = 'Constructor'
        elif name.startswith('_'):
            continue

        # Format the function names.
        testname = re.sub(r'_(\w)',  uppercase, name)
        testname = re.sub(r'(\d\w)', uppercase, testname)
        testname = 'test' + re.sub(r'^(\w)', uppercase, testname)
        testmethod = theclass.__name__ + '.' + testname
        method = theclass.CORRELATE.__name__ + '.' + name
        both = testmethod + ' (' + method + ')'

        # Throw an error if the function does not have a test.
        if testname in dir(theclass):
            continue
        if ismodule(theclass.CORRELATE) and \
                value.__module__ != theclass.CORRELATE.__name__:
            continue  # function was imported.
        if both in correlated:
            continue
        correlated[both] = True
        if ismodule(theclass.CORRELATE):
            sys.stderr.write('!!!! WARNING: Untested function: ' + both + '\n')
        elif isclass(theclass.CORRELATE):
            sys.stderr.write('!!!! WARNING: Untested method: ' + both + '\n')


def correlate_module(module):
    """
    Checks all testcases in the module for missing test methods.
    """
    for name, item in list(module.__dict__.items()):
        if isclass(item):
            correlate_class(item)


def find(dirname, pattern):
    output = []
    for root, dirs, files in os.walk(dirname):
        for file in files:
            if fnmatch.fnmatchcase(file, pattern):
                output.append(os.path.join(root, file))
    return output


def load_suite(files):
    modules = [os.path.splitext(f)[0] for f in files]
    all_suites = []
    for name in modules:
        name = name.lstrip('.').lstrip('/').replace('/', '.')
        module = __import__(name, globals(), locals(), [''])
        all_suites.append(module.suite())
        correlate_module(module)
    if correlated:
        sys.stderr.write('Error: Untested methods found.\n')
        sys.exit(1)
    return unittest.TestSuite(all_suites)


def suite():
    pattern = os.path.join(os.path.dirname(__file__), '*Test.py')
    files = glob.glob(pattern)
    return load_suite([os.path.basename(f) for f in files])


def recursive_suite():
    return load_suite(find('.', '*Test.py'))

if __name__ == '__main__':
    # Parse CLI options.
    if len(sys.argv) == 1:
        verbosity = 2
    elif len(sys.argv) == 2:
        verbosity = int(sys.argv[1])
    else:
        print(('Syntax:', sys.argv[0], '[verbosity]'))
        print('Default verbosity is 2')
        sys.exit(1)

    # Run.
    unittest.TextTestRunner(verbosity=verbosity).run(recursive_suite())
