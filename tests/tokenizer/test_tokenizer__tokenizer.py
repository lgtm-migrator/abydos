# -*- coding: utf-8 -*-

# Copyright 2019 by Christopher C. Little.
# This file is part of Abydos.
#
# Abydos is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Abydos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Abydos. If not, see <http://www.gnu.org/licenses/>.

"""abydos.tests.tokenizer.test_tokenizer_tokenizer.

This module contains unit tests for abydos.tokenizer._Tokenizer
"""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import unittest
from collections import Counter

from abydos.tokenizer import _Tokenizer


class TokenizerTestCases(unittest.TestCase):
    """Test abydos.tokenizer._Tokenizer."""

    def test__tokenizer(self):
        """Test abydos.tokenizer._Tokenizer."""
        self.assertEqual(
            _Tokenizer().tokenize('').get_counter(), Counter({'': 1})
        )
        self.assertEqual(
            _Tokenizer().tokenize('a').get_counter(), Counter({'a': 1})
        )

        self.assertEqual(
            _Tokenizer().tokenize('NELSON').get_counter(),
            Counter({'NELSON': 1}),
        )
        self.assertEqual(
            _Tokenizer().tokenize('NEILSEN').get_counter(),
            Counter({'NEILSEN': 1}),
        )

        tweet = 'Good to be home for a night'
        self.assertEqual(
            _Tokenizer().tokenize(tweet).get_counter(),
            Counter({'Good to be home for a night': 1}),
        )


if __name__ == '__main__':
    unittest.main()