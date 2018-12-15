# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------
#  Copyright by KNIME AG, Zurich, Switzerland
#  Website: http://www.knime.com; Email: contact@knime.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License, Version 3, as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses>.
#
#  Additional permission under GNU GPL version 3 section 7:
#
#  KNIME interoperates with ECLIPSE solely via ECLIPSE's plug-in APIs.
#  Hence, KNIME and ECLIPSE are both independent programs and are not
#  derived from each other. Should, however, the interpretation of the
#  GNU GPL Version 3 ("License") under any applicable laws result in
#  KNIME and ECLIPSE being a combined program, KNIME AG herewith grants
#  you the additional permission to use and propagate KNIME together with
#  ECLIPSE with only the license terms in place for ECLIPSE applying to
#  ECLIPSE and the GNU GPL Version 3 applying for KNIME, provided the
#  license terms of ECLIPSE themselves allow for the respective use and
#  propagation of ECLIPSE together with KNIME.
#
#  Additional permission relating to nodes for KNIME that extend the Node
#  Extension (and in particular that are based on subclasses of NodeModel,
#  NodeDialog, and NodeView) and that only interoperate with KNIME through
#  standard APIs ("Nodes"):
#  Nodes are deemed to be separate and independent programs and to not be
#  covered works.  Notwithstanding anything to the contrary in the
#  License, the License does not apply to Nodes, you are not required to
#  license Nodes under the License, and you are granted a license to
#  prepare and propagate Nodes, in each case even if such Nodes are
#  propagated with or for interoperation with KNIME.  The owner of a Node
#  may freely choose the license terms applicable to such Node, including
#  when such Node is propagated with or for interoperation with KNIME.
# ------------------------------------------------------------------------

"""
@author Clemens von Schwerin, KNIME GmbH, Konstanz, Germany
@author Patrick Winter, KNIME GmbH, Konstanz, Germany
@author Marcel Wiedenmann, KNIME GmbH, Konstanz, Germany
@author Christian Dietz, KNIME GmbH, Konstanz, Germany
"""

import EnvironmentHelper

EnvironmentHelper.dummy_call()

from argparse import ArgumentParser
import sys

from distutils.version import LooseVersion

_default_min_pandas_version = '0.20.0'


class PythonKernelTester(object):

    def __init__(self):
        self._messages = []

    def check_python(self, major_version, min_version=None, min_inclusive=True, max_version=None, max_inclusive=True):
        """
        Checks whether the version of this Python installation conforms to the specified major version and, optionally,
        version range (or just the minimum version). To test for a specific version, set max_version = min_version.

        :param major_version: The major version as a string consisting of a single character ('2' or '3').
        :param min_version: The minimum version as a dot separated version string. Defaults to None in which case there
        is no lower bound to which the version of the Python installation must conform.
        :param min_inclusive: True if the version of the Python installation may equal min_version, False otherwise.
        :param max_version: The maximum version as a dot separated version string. Defaults to None in which case there
        is no upper bound to which the version of the Python installation must conform.
        :param max_inclusive: True if the version of the Python installation may equal max_version, False otherwise.
        :return: The list of installation error messages that were recorded during this check, possibly empty.
        """
        major_version = LooseVersion(major_version)
        version = PythonKernelTester._get_python_version()
        installed_major_version = LooseVersion(str(LooseVersion(version).version[0]))

        messages = []
        if installed_major_version != major_version:
            message = 'Python is required to have a major version of ' + str(major_version)
            message += PythonKernelTester._get_version_constraint_message(min_version, min_inclusive, "minimum")
            message += PythonKernelTester._get_version_constraint_message(max_version, max_inclusive, "maximum")
            message += '.\nThe installed Python version is ' + str(version) + '.'
            messages.append(message)
        else:
            version_comparison = PythonKernelTester._compare_versions(version, min_version, min_inclusive,
                                                                      max_version, max_inclusive)
            if version_comparison != 0:
                message = 'Installed Python version is ' + str(version)
                message += PythonKernelTester._get_version_constraint_message(min_version, min_inclusive, "minimum")
                message += PythonKernelTester._get_version_constraint_message(max_version, max_inclusive, "maximum")
                message += '.'
                messages.append(message)

        self._add_to_messages(messages)
        return messages

    @staticmethod
    def _get_python_version():
        """
        :return: The version String of the this Python installation.
        """
        version = sys.version_info
        return str(version[0]) + '.' + str(version[1]) + '.' + str(version[2])

    def check_module(self, module_name, min_version=None, min_inclusive=True, max_version=None, max_inclusive=True,
                     class_names=None):
        """
        Checks whether the given module is installed and conforms to a specified version range, if applicable.
        Optionally also checks whether the module contains a given list of classes.

        :param module_name: The fully qualified name of the module.
        :param min_version: The minimum version as a dot separated version string. Defaults to None in which case there
        is no lower bound to which the version of the module must conform.
        :param min_inclusive: True if the version of the module may equal min_version, False otherwise.
        :param max_version: The maximum version as a dot separated version string. Defaults to None in which case there
        is no lower bound to which the version of the module must conform.
        :param max_inclusive: True if the version of the module may equal max_version, False otherwise.
        :param class_names: A list of names of classes to check for availability in the given module.
        :return: The list of installation error messages that were recorded during this check, possibly empty.
        """
        mod_availability = PythonKernelTester._get_module_availability(module_name, min_version,
                                                                       min_inclusive, max_version,
                                                                       max_inclusive)
        mod_available = mod_availability[0]
        mod_version_conforms = mod_availability[1]
        mod_version = mod_availability[2]

        messages = []
        if not mod_available:
            # Module is not installed at all.
            message = 'Library ' + module_name + ' is missing'
            message += PythonKernelTester._get_version_constraint_message(min_version, min_inclusive, "minimum")
            message += PythonKernelTester._get_version_constraint_message(max_version, max_inclusive, "maximum")
            message += '.'
            messages.append(message)
        elif not mod_version_conforms:
            # Module is installed but in a wrong version.
            if mod_version is not None:
                message = 'Library ' + module_name + ' is installed in version ' + str(mod_version)
            else:
                message = 'Library ' + module_name + ' is installed in an unknown version'
            message += PythonKernelTester._get_version_constraint_message(min_version, min_inclusive, "minimum")
            message += PythonKernelTester._get_version_constraint_message(max_version, max_inclusive, "maximum")
            message += '.'
            messages.append(message)
        elif class_names is not None:
            # Module itself is installed properly. Check classes.
            for class_name in class_names:
                if not PythonKernelTester._is_class_available(module_name, class_name):
                    messages.append(
                        'Required class ' + class_name + ' in library ' + module_name + ' is missing.')

        self._add_to_messages(messages)
        return messages

    @staticmethod
    def _get_module_availability(module_name, min_version=None, min_inclusive=True, max_version=None,
                                 max_inclusive=True):
        """
        Retrieves whether the given module is installed and conforms to the given version range. By default, only the
        availability of the given module is tested without taking its version into account. If min_version is specified,
        it is tested whether the version of the given module is equal to or greater than the given min. value. If
        max_version is specified, it is tested whether the version of the given module is equal to or less than the
        given max. value. (With respect to the inclusive option, respectively.)

        :return: A 3-tuple. The first field of the tuple is a Boolean that is True if the given module is installed and
        False otherwise. The second field is a Boolean that is True if the version of the given module either conforms
        to the given version range or if there is no version range specified. It is False otherwise. In particular, it
        is also False if the module is not installed, or if the version of the module cannot be determined while there
        is a version range specified. The third field of the tuple is the version string of the given module. It is None
        if the module is not installed or if the version of the module cannot be determined.
        """
        # Verbatim string, please leave formatted as it is.
        test_script = """
test_mod_available = False
test_mod_version = None
try:
    import {0}
    test_mod_available = True
    if hasattr({0}, '__version__'):
        test_mod_version = {0}.__version__
except:
    # We report unavailability by default.
    pass
        """.format(module_name)
        test_env = {}
        exec(test_script, {}, test_env)

        test_mod_available = test_env['test_mod_available']
        test_mod_version_conforms = False
        test_mod_version = test_env['test_mod_version']

        if test_mod_available:
            if (test_mod_version is not None and PythonKernelTester._compare_versions(test_mod_version, min_version,
                                                                                      min_inclusive, max_version,
                                                                                      max_inclusive) == 0) or (
                    min_version is None and max_version is None):
                test_mod_version_conforms = True

        return test_mod_available, test_mod_version_conforms, test_mod_version

    @staticmethod
    def _is_class_available(module_name, class_name):
        """
        Retrieves whether the class of the given name is available in the module of the given name.
        :return: True if the class is available, False otherwise.
        """
        # Verbatim string, please leave formatted as it is.
        test_script = """
test_class_available = False
try:
    from {0} import {1}
    test_class_available = True
except:
    # We report unavailability by default.
    pass
        """.format(module_name, class_name)
        test_env = {}
        exec(test_script, {}, test_env)

        return test_env['test_class_available']

    @staticmethod
    def _compare_versions(version, min_version=None, min_inclusive=True, max_version=None, max_inclusive=True):
        """
        :return: Returns a value smaller than zero if min_version is not None and version is less than min_version with
        respect to min_inclusive. Returns a value greater than zero if max_version is not None and version is greater
        than max_version with respect to max_inclusive. Returns zero otherwise.
        """
        version = LooseVersion(version)
        if min_version is not None:
            min_version = LooseVersion(min_version)
            if version < min_version:
                return -1
            if (not min_inclusive) and version == min_version:
                return -1
        if max_version is not None:
            max_version = LooseVersion(max_version)
            if version > max_version:
                return 1
            if (not max_inclusive) and version == max_version:
                return 1
        return 0

    @staticmethod
    def _get_version_constraint_message(version_bound, bound_inclusive, bound_name):
        if version_bound is not None:
            inclusion = 'inclusive' if bound_inclusive else 'exclusive'
            return ', required ' + bound_name + ' version is ' + str(version_bound) + ' (' + inclusion + ')'
        else:
            return ""

    def _add_to_messages(self, message):
        """
        Adds a single message or a list of messages to the list of messages that make up the result of the installation
        test.
        """
        if isinstance(message, list):
            self._messages.extend(message)
        else:
            self._messages.append(message)

    def get_report_lines(self):
        """
        Returns the error messages that were recorded by this installation tester.

        :return: The error report as a list of strings.
        """
        return list(self._messages)


# Default installation test:

class _DefaultPythonKernelTester(PythonKernelTester):

    def __init__(self):
        super(_DefaultPythonKernelTester, self).__init__()

    def check_python(self, major_version, min_version=None, min_inclusive=True, max_version=None,
                     max_inclusive=True):
        print('Python version: ' + PythonKernelTester._get_python_version())  # Expected by Java side.
        return super(_DefaultPythonKernelTester, self).check_python(major_version, min_version, min_inclusive,
                                                                    max_version,
                                                                    max_inclusive)

    def check_required_modules(self, additional_required_modules=None):
        # Python standard modules.
        # TODO: Does it really make sense to test those?!
        if EnvironmentHelper.is_python3():
            self.check_module('io')
        else:
            self.check_module('StringIO')
        self.check_module('datetime', class_names=['datetime'])
        self.check_module('math')
        self.check_module('socket')
        self.check_module('struct')
        self.check_module('base64')
        self.check_module('traceback')
        self.check_module('os')
        self.check_module('pickle')
        self.check_module('imp')
        self.check_module('types')
        # Non-standard modules.
        self.check_module('numpy')
        global _default_min_pandas_version
        min_pandas_version = _default_min_pandas_version
        self.check_module('pandas', min_version=min_pandas_version, class_names=['DataFrame'])
        # Additional modules.
        if additional_required_modules is not None:
            for module in additional_required_modules:
                self.check_module(module)


def _perform_default_installation_test():
    major_python_version, min_python_version, max_python_version, additional_required_modules = _parse_program_args()

    tester = _DefaultPythonKernelTester()
    tester.check_python(major_python_version, min_version=min_python_version, min_inclusive=True,
                        max_version=max_python_version,
                        max_inclusive=False)
    tester.check_required_modules(additional_required_modules)

    report = tester.get_report_lines()
    report = "\n".join(report)
    print(report)  # Expected by Java side.
    sys.stdout.flush()


def _parse_program_args():
    """
    Parses the program's command line arguments. They are expected to be of the form major_python_version
    [min_python_version][max_python_version][-m module1 ...]. min_python_version and max_python_version must be dot
    separated version strings (major.minor.micro).

    :return: A 4-tuple where the first item is the expected major Python version. The second item is the inclusive
    minimum Python version to which he version of the local Python installation must conform. The third item is the
    exclusive maximum Python version. The fourth item is the list of additional modules that must be present in the
    local Python installation. All arguments but the first one are optional.
    """
    parser = ArgumentParser()
    parser.add_argument('major_python_version')
    parser.add_argument('min_python_version', default=None, nargs='?')
    parser.add_argument('max_python_version', default=None, nargs='?')
    parser.add_argument('-m', nargs='*')

    parsed = parser.parse_args()
    return parsed.major_python_version, parsed.min_python_version, parsed.max_python_version, parsed.m


if __name__ == "__main__":
    _perform_default_installation_test()
