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

from __future__ import print_function

# This should be the first statement in each module (except for __future__ statements) that makes specific demands on
# the Python environment.
import EnvironmentHelper

EnvironmentHelper.dummy_call()

import sys
import traceback

# Debugging:

# Uncomment to enable debugging; you may want to enable breakpoints:
import debug_util
debug_util.init_debug(enable_breakpoints=True, enable_debug_log=True, debug_log_to_stderr=False)

# Start Python kernel:

if __name__ == "__main__":
    if EnvironmentHelper.is_python3():
        from python3.PythonKernel import PythonKernel
    else:
        from python2.PythonKernel import PythonKernel

    # Uncomment below statements and comment the ordinary start statements for profiling.
    # See https://docs.python.org/3/library/profile.html on how to interpret the result.
    # import cProfile
    # profilepath = os.path.join(os.path.expanduser('~'), 'profileres.txt')
    # cProfile.run('kernel = PythonKernel(); kernel.start()', filename=profilepath)

    with PythonKernel() as kernel:
        try:
            kernel.start()
        except BaseException as ex:
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
            raise
