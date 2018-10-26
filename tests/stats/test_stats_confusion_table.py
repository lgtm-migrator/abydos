# -*- coding: utf-8 -*-

# Copyright 2014-2018 by Christopher C. Little.
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

"""abydos.tests.stats.test_stats_confusion_table.

This module contains unit tests for abydos.stats._confusion_table
"""

from __future__ import division, unicode_literals

import unittest
from math import isnan, sqrt

from abydos.stats import ConfusionTable


UNIT_TABLE = ConfusionTable(1, 1, 1, 1)
NULL_TABLE = ConfusionTable(0, 0, 0, 0)
SCALE_TABLE = ConfusionTable(1, 2, 3, 4)
# https://en.wikipedia.org/wiki/Confusion_matrix#Table_of_confusion
CATSNDOGS_TABLE = ConfusionTable(5, 17, 2, 3)
# https://en.wikipedia.org/wiki/Sensitivity_and_specificity#Worked_example
WORKED_EG_TABLE = ConfusionTable(20, 1820, 180, 10)
VERY_POOR_TABLE = ConfusionTable(0, 0, 200, 200)

ALL_TABLES = (
    UNIT_TABLE,
    NULL_TABLE,
    SCALE_TABLE,
    CATSNDOGS_TABLE,
    WORKED_EG_TABLE,
    VERY_POOR_TABLE,
)

# def ct2arrays(ct):
#     y_pred = []
#     y_true = []
#     y_pred += [1]*ct.tpos
#     y_true += [1]*ct.tpos
#     y_pred += [0]*ct.tneg
#     y_true += [0]*ct.tneg
#     y_pred += [1]*ct.fpos
#     y_true += [0]*ct.fpos
#     y_pred += [0]*ct.fneg
#     y_true += [1]*ct.fneg
#     return y_pred, y_true


class ConstructorTestCases(unittest.TestCase):
    """Test abydos.stats._confusion_table.ConfusionTable constructors."""

    def test_constructors(self):
        """Test abydos.stats._confusion_table.ConfusionTable constructors."""
        self.assertEqual(ConfusionTable(), ConfusionTable())
        self.assertEqual(ConfusionTable(), ConfusionTable(0))
        self.assertEqual(ConfusionTable(), ConfusionTable(0, 0))
        self.assertEqual(ConfusionTable(), ConfusionTable(0, 0, 0))
        self.assertEqual(ConfusionTable(), ConfusionTable(0, 0, 0, 0))
        self.assertNotEquals(ConfusionTable(), ConfusionTable(1))
        self.assertNotEquals(ConfusionTable(), ConfusionTable(0, 1))
        self.assertNotEquals(ConfusionTable(), ConfusionTable(0, 0, 1))
        self.assertNotEquals(ConfusionTable(), ConfusionTable(0, 0, 0, 1))

        # test int constructor & __eq__ by value
        self.assertEqual(SCALE_TABLE, ConfusionTable(1, 2, 3, 4))
        # test tuple constructor
        self.assertEqual(SCALE_TABLE, ConfusionTable((1, 2, 3, 4)))
        self.assertEqual(SCALE_TABLE, ConfusionTable((1, 2, 3, 4), 5, 6, 7))
        # test list constructor
        self.assertEqual(SCALE_TABLE, ConfusionTable([1, 2, 3, 4]))
        self.assertEqual(SCALE_TABLE, ConfusionTable([1, 2, 3, 4], 5, 6, 7))
        # test dict constructor
        self.assertEqual(
            SCALE_TABLE, ConfusionTable({'tp': 1, 'tn': 2, 'fp': 3, 'fn': 4})
        )
        self.assertEqual(
            SCALE_TABLE,
            ConfusionTable({'tp': 1, 'tn': 2, 'fp': 3, 'fn': 4}, 5, 6, 7),
        )
        self.assertEqual(NULL_TABLE, ConfusionTable({}))
        self.assertEqual(
            NULL_TABLE, ConfusionTable({'pt': 1, 'nt': 2, 'pf': 3, 'nf': 4})
        )

        # test __eq__ by id()
        self.assertTrue(SCALE_TABLE == SCALE_TABLE)
        self.assertFalse(CATSNDOGS_TABLE == SCALE_TABLE)
        # test __eq__ by tuple
        self.assertTrue(SCALE_TABLE == (1, 2, 3, 4))
        self.assertFalse(CATSNDOGS_TABLE == (1, 2, 3, 4))
        # test __eq__ by list
        self.assertTrue(SCALE_TABLE == [1, 2, 3, 4])
        self.assertFalse(CATSNDOGS_TABLE == [1, 2, 3, 4])
        # test __eq__ by dict
        self.assertTrue(SCALE_TABLE == {'tp': 1, 'tn': 2, 'fp': 3, 'fn': 4})
        self.assertFalse(
            CATSNDOGS_TABLE == {'tp': 1, 'tn': 2, 'fp': 3, 'fn': 4}
        )
        # test __eq__ with non-ConfusionTable/tuple/list/dict
        self.assertFalse(SCALE_TABLE == 5)

        # test invalid tuple constructor
        self.assertRaises(AttributeError, ConfusionTable, (1, 2))


class CastTestCases(unittest.TestCase):
    """Test abydos.stats._confusion_table.ConfusionTable cast methods."""

    def test_to_tuple(self):
        """Test abydos.stats._confusion_table.ConfusionTable.to_tuple."""
        self.assertIsInstance(SCALE_TABLE.to_tuple(), tuple)
        self.assertEqual(SCALE_TABLE.to_tuple(), (1, 2, 3, 4))
        self.assertEqual(list(SCALE_TABLE.to_tuple()), [1, 2, 3, 4])

    def test_to_dict(self):
        """Test abydos.stats._confusion_table.ConfusionTable.to_dict."""
        self.assertIsInstance(SCALE_TABLE.to_dict(), dict)
        self.assertEqual(
            SCALE_TABLE.to_dict(), {'tp': 1, 'tn': 2, 'fp': 3, 'fn': 4}
        )

    def test_str(self):
        """Test abydos.stats._confusion_table.ConfusionTable._str_."""
        self.assertIsInstance(str(SCALE_TABLE), str)
        self.assertEqual(str(SCALE_TABLE), 'tp:1, tn:2, fp:3, fn:4')


class PopulationTestCases(unittest.TestCase):
    """Test abydos.stats._confusion_table.ConfusionTable population methods."""

    def test_correct_pop(self):
        """Test abydos.stats._confusion_table.ConfusionTable.correct_pop."""
        self.assertEqual(UNIT_TABLE.correct_pop(), 2)
        self.assertEqual(NULL_TABLE.correct_pop(), 0)
        self.assertEqual(SCALE_TABLE.correct_pop(), 3)
        self.assertEqual(CATSNDOGS_TABLE.correct_pop(), 22)
        self.assertEqual(WORKED_EG_TABLE.correct_pop(), 1840)

    def test_error_pop(self):
        """Test abydos.stats._confusion_table.ConfusionTable.error_pop."""
        self.assertEqual(UNIT_TABLE.error_pop(), 2)
        self.assertEqual(NULL_TABLE.error_pop(), 0)
        self.assertEqual(SCALE_TABLE.error_pop(), 7)
        self.assertEqual(CATSNDOGS_TABLE.error_pop(), 5)
        self.assertEqual(WORKED_EG_TABLE.error_pop(), 190)

    def test_test_pos_pop(self):
        """Test abydos.stats._confusion_table.ConfusionTable.test_pos_pop."""
        self.assertEqual(UNIT_TABLE.test_pos_pop(), 2)
        self.assertEqual(NULL_TABLE.test_pos_pop(), 0)
        self.assertEqual(SCALE_TABLE.test_pos_pop(), 4)
        self.assertEqual(CATSNDOGS_TABLE.test_pos_pop(), 7)
        self.assertEqual(WORKED_EG_TABLE.test_pos_pop(), 200)

    def test_test_neg_pop(self):
        """Test abydos.stats._confusion_table.ConfusionTable.test_neg_pop."""
        self.assertEqual(UNIT_TABLE.test_neg_pop(), 2)
        self.assertEqual(NULL_TABLE.test_neg_pop(), 0)
        self.assertEqual(SCALE_TABLE.test_neg_pop(), 6)
        self.assertEqual(CATSNDOGS_TABLE.test_neg_pop(), 20)
        self.assertEqual(WORKED_EG_TABLE.test_neg_pop(), 1830)

    def test_cond_pos_pop(self):
        """Test abydos.stats._confusion_table.ConfusionTable.cond_pos_pop."""
        self.assertEqual(UNIT_TABLE.cond_pos_pop(), 2)
        self.assertEqual(NULL_TABLE.cond_pos_pop(), 0)
        self.assertEqual(SCALE_TABLE.cond_pos_pop(), 5)
        self.assertEqual(CATSNDOGS_TABLE.cond_pos_pop(), 8)
        self.assertEqual(WORKED_EG_TABLE.cond_pos_pop(), 30)

    def test_cond_neg_pop(self):
        """Test abydos.stats._confusion_table.ConfusionTable.cond_neg_pop."""
        self.assertEqual(UNIT_TABLE.cond_neg_pop(), 2)
        self.assertEqual(NULL_TABLE.cond_neg_pop(), 0)
        self.assertEqual(SCALE_TABLE.cond_neg_pop(), 5)
        self.assertEqual(CATSNDOGS_TABLE.cond_neg_pop(), 19)
        self.assertEqual(WORKED_EG_TABLE.cond_neg_pop(), 2000)

    def test_population(self):
        """Test abydos.stats._confusion_table.ConfusionTable.population."""
        self.assertEqual(UNIT_TABLE.population(), 4)
        self.assertEqual(NULL_TABLE.population(), 0)
        self.assertEqual(SCALE_TABLE.population(), 10)
        self.assertEqual(CATSNDOGS_TABLE.population(), 27)
        self.assertEqual(WORKED_EG_TABLE.population(), 2030)


class StatisticalRatioTestCases(unittest.TestCase):
    """Test abydos.stats._confusion_table.ConfusionTable ratio methods."""

    def test_precision(self):
        """Test abydos.stats._confusion_table.ConfusionTable.precision."""
        self.assertEqual(UNIT_TABLE.precision(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.precision()))
        self.assertAlmostEqual(SCALE_TABLE.precision(), 0.25)
        self.assertAlmostEqual(CATSNDOGS_TABLE.precision(), 5 / 7)
        self.assertAlmostEqual(WORKED_EG_TABLE.precision(), 0.1)

    def test_precision_gain(self):
        """Test abydos.stats._confusion_table.ConfusionTable.precision_gain."""
        self.assertEqual(UNIT_TABLE.precision_gain(), 1)
        self.assertTrue(isnan(NULL_TABLE.precision_gain()))
        self.assertAlmostEqual(SCALE_TABLE.precision_gain(), 0.25 / 0.5)
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.precision_gain(), (5 / 7) / (8 / 27)
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.precision_gain(), 0.1 / (30 / 2030)
        )

    def test_recall(self):
        """Test abydos.stats._confusion_table.ConfusionTable.recall."""
        self.assertEqual(UNIT_TABLE.recall(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.recall()))
        self.assertAlmostEqual(SCALE_TABLE.recall(), 0.2)
        self.assertAlmostEqual(CATSNDOGS_TABLE.recall(), 5 / 8)
        self.assertAlmostEqual(WORKED_EG_TABLE.recall(), 2 / 3)

    def test_specificity(self):
        """Test abydos.stats._confusion_table.ConfusionTable.specificity."""
        self.assertEqual(UNIT_TABLE.specificity(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.specificity()))
        self.assertAlmostEqual(SCALE_TABLE.specificity(), 0.4)
        self.assertAlmostEqual(CATSNDOGS_TABLE.specificity(), 17 / 19)
        self.assertAlmostEqual(WORKED_EG_TABLE.specificity(), 0.91)

    def test_npv(self):
        """Test abydos.stats._confusion_table.ConfusionTable.npv."""
        self.assertEqual(UNIT_TABLE.npv(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.npv()))
        self.assertAlmostEqual(SCALE_TABLE.npv(), 1 / 3)
        self.assertAlmostEqual(CATSNDOGS_TABLE.npv(), 17 / 20)
        self.assertAlmostEqual(WORKED_EG_TABLE.npv(), 182 / 183)

    def test_fallout(self):
        """Test abydos.stats._confusion_table.ConfusionTable.fallout."""
        self.assertEqual(UNIT_TABLE.fallout(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.fallout()))
        self.assertAlmostEqual(SCALE_TABLE.fallout(), 0.6)
        self.assertAlmostEqual(CATSNDOGS_TABLE.fallout(), 2 / 19)
        self.assertAlmostEqual(WORKED_EG_TABLE.fallout(), 0.09)

    def test_fdr(self):
        """Test abydos.stats._confusion_table.ConfusionTable.fdr."""
        self.assertEqual(UNIT_TABLE.fdr(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.fdr()))
        self.assertAlmostEqual(SCALE_TABLE.fdr(), 0.75)
        self.assertAlmostEqual(CATSNDOGS_TABLE.fdr(), 2 / 7)
        self.assertAlmostEqual(WORKED_EG_TABLE.fdr(), 0.9)

    def test_accuracy(self):
        """Test abydos.stats._confusion_table.ConfusionTable.accuracy."""
        self.assertEqual(UNIT_TABLE.accuracy(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.accuracy()))
        self.assertAlmostEqual(SCALE_TABLE.accuracy(), 3 / 10)
        self.assertAlmostEqual(CATSNDOGS_TABLE.accuracy(), 22 / 27)
        self.assertAlmostEqual(WORKED_EG_TABLE.accuracy(), 184 / 203)

    def test_accuracy_gain(self):
        """Test abydos.stats._confusion_table.ConfusionTable.accuracy_gain."""
        self.assertEqual(UNIT_TABLE.accuracy_gain(), 1)
        self.assertTrue(isnan(NULL_TABLE.accuracy_gain()))
        self.assertAlmostEqual(
            SCALE_TABLE.accuracy_gain(),
            (3 / 10) / ((5 / 10) ** 2 + (5 / 10) ** 2),
        )
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.accuracy_gain(),
            (22 / 27) / ((8 / 27) ** 2 + (19 / 27) ** 2),
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.accuracy_gain(),
            (184 / 203) / ((30 / 2030) ** 2 + (2000 / 2030) ** 2),
        )

    def test_balanced_accuracy(self):
        """Test abydos.stats._confusion_table.ConfusionTable.balanced_accuracy."""  # noqa: E501
        self.assertEqual(UNIT_TABLE.balanced_accuracy(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.balanced_accuracy()))
        self.assertAlmostEqual(SCALE_TABLE.balanced_accuracy(), 0.3)
        self.assertAlmostEqual(CATSNDOGS_TABLE.balanced_accuracy(), 231 / 304)
        self.assertAlmostEqual(WORKED_EG_TABLE.balanced_accuracy(), 473 / 600)

    def test_informedness(self):
        """Test abydos.stats._confusion_table.ConfusionTable.informedness."""
        self.assertEqual(UNIT_TABLE.informedness(), 0)
        self.assertTrue(isnan(NULL_TABLE.informedness()))
        self.assertAlmostEqual(SCALE_TABLE.informedness(), -0.4)
        self.assertAlmostEqual(CATSNDOGS_TABLE.informedness(), 79 / 152)
        self.assertAlmostEqual(WORKED_EG_TABLE.informedness(), 2 / 3 - 0.09)

    def test_markedness(self):
        """Test abydos.stats._confusion_table.ConfusionTable.markedness."""
        self.assertEqual(UNIT_TABLE.markedness(), 0)
        self.assertTrue(isnan(NULL_TABLE.markedness()))
        self.assertAlmostEqual(SCALE_TABLE.markedness(), -5 / 12)
        self.assertAlmostEqual(CATSNDOGS_TABLE.markedness(), 79 / 140)
        self.assertAlmostEqual(WORKED_EG_TABLE.markedness(), 173 / 1830)


class PrMeansTestCases(unittest.TestCase):
    """Test abydos.stats._confusion_table.ConfusionTable PR methods."""

    prre = tuple(((i.precision(), i.recall()) for i in ALL_TABLES))

    def test_pr_amean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_amean."""
        self.assertEqual(UNIT_TABLE.pr_amean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_amean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_amean(), 0.225)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_amean(), 0.6696428571428572)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_amean(), 0.3833333333333333)
        self.assertAlmostEqual(VERY_POOR_TABLE.pr_amean(), 0.0)

    def test_pr_gmean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_gmean."""
        self.assertEqual(UNIT_TABLE.pr_gmean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_gmean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_gmean(), 0.22360679774997899)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_gmean(), 0.66815310478106094)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_gmean(), 0.25819888974716115)
        self.assertAlmostEqual(VERY_POOR_TABLE.pr_gmean(), 0.0)

    def test_pr_hmean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_hmean."""
        self.assertEqual(UNIT_TABLE.pr_hmean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_hmean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_hmean(), 0.22222222222222221)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_hmean(), 0.66666666666666663)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_hmean(), 0.17391304347826086)
        self.assertAlmostEqual(VERY_POOR_TABLE.pr_hmean(), 0.0)

    def test_pr_qmean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_qmean."""
        self.assertEqual(
            UNIT_TABLE.pr_qmean(), sqrt(sum(i ** 2 for i in self.prre[0]) / 2)
        )
        self.assertTrue(isnan(NULL_TABLE.pr_qmean()))
        self.assertAlmostEqual(
            SCALE_TABLE.pr_qmean(), sqrt(sum(i ** 2 for i in self.prre[2]) / 2)
        )
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.pr_qmean(),
            sqrt(sum(i ** 2 for i in self.prre[3]) / 2),
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_qmean(),
            sqrt(sum(i ** 2 for i in self.prre[4]) / 2),
        )
        self.assertAlmostEqual(VERY_POOR_TABLE.pr_qmean(), 0.0)

    def test_pr_cmean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_cmean."""
        self.assertEqual(UNIT_TABLE.pr_cmean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_cmean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_cmean(), 41 / 180)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_cmean(), 113 / 168)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_cmean(), 409 / 690)

    def test_pr_lmean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_lmean."""
        self.assertEqual(UNIT_TABLE.pr_lmean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_lmean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_lmean(), 0.2240710058862275)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_lmean(), 0.6686496151266621)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_lmean(), 0.2986983802717959)
        self.assertAlmostEqual(VERY_POOR_TABLE.pr_lmean(), 0.0)

    def test_pr_imean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_imean."""
        self.assertEqual(UNIT_TABLE.pr_imean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_imean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_imean(), 0.224535791730617)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_imean(), 0.6691463467789889)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_imean(), 0.34277561539033635)
        self.assertTrue(isnan(VERY_POOR_TABLE.pr_imean()))

    def test_pr_seiffert_mean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_seiffert_mean."""  # noqa: E501
        self.assertTrue(isnan(UNIT_TABLE.pr_seiffert_mean()))
        self.assertTrue(isnan(NULL_TABLE.pr_seiffert_mean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_seiffert_mean(), 0.2245354073)
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.pr_seiffert_mean(), 0.6691461993
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_seiffert_mean(), 0.3406355792
        )
        self.assertTrue(isnan(VERY_POOR_TABLE.pr_seiffert_mean()))

    def test_pr_lehmer_mean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_lehmer_mean."""
        self.assertEqual(UNIT_TABLE.pr_lehmer_mean(3), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_lehmer_mean(3)))
        self.assertAlmostEqual(SCALE_TABLE.pr_lehmer_mean(3), 189 / 820)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_lehmer_mean(3), 4275 / 6328)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_lehmer_mean(3), 8027 / 12270)

        self.assertEqual(UNIT_TABLE.pr_lehmer_mean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_lehmer_mean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_lehmer_mean(), 41 / 180)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_lehmer_mean(), 113 / 168)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_lehmer_mean(), 409 / 690)

        self.assertEqual(UNIT_TABLE.pr_lehmer_mean(2), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_lehmer_mean(2)))
        self.assertAlmostEqual(SCALE_TABLE.pr_lehmer_mean(2), 41 / 180)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_lehmer_mean(2), 113 / 168)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_lehmer_mean(2), 409 / 690)

        # check equivalences to other specific means
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_lehmer_mean(0), WORKED_EG_TABLE.pr_hmean()
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_lehmer_mean(0.5), WORKED_EG_TABLE.pr_gmean()
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_lehmer_mean(1), WORKED_EG_TABLE.pr_amean()
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_lehmer_mean(2), WORKED_EG_TABLE.pr_cmean()
        )

    def test_pr_heronian_mean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_heronian_mean."""  # noqa: E501
        self.assertEqual(UNIT_TABLE.pr_heronian_mean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_heronian_mean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_heronian_mean(), 0.2245355992)
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.pr_heronian_mean(), 0.6691462730
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_heronian_mean(), 0.3416218521
        )
        self.assertEqual(VERY_POOR_TABLE.pr_heronian_mean(), 0)

    def test_pr_hoelder_mean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_hoelder_mean."""  # noqa: E501
        self.assertEqual(UNIT_TABLE.pr_hoelder_mean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_hoelder_mean()))
        self.assertAlmostEqual(
            SCALE_TABLE.pr_hoelder_mean(), 0.22638462845343543
        )
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.pr_hoelder_mean(), 0.6711293026059334
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_hoelder_mean(), 0.4766783215358364
        )

        self.assertEqual(UNIT_TABLE.pr_hoelder_mean(0), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_hoelder_mean(0)))
        self.assertAlmostEqual(
            SCALE_TABLE.pr_hoelder_mean(0), 0.22360679774997899
        )
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.pr_hoelder_mean(0), 0.66815310478106094
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_hoelder_mean(0), 0.25819888974716115
        )

        self.assertEqual(UNIT_TABLE.pr_hoelder_mean(1), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_hoelder_mean(1)))
        self.assertAlmostEqual(SCALE_TABLE.pr_hoelder_mean(1), 9 / 40)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_hoelder_mean(1), 75 / 112)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_hoelder_mean(1), 23 / 60)

        self.assertEqual(UNIT_TABLE.pr_hoelder_mean(2), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_hoelder_mean(2)))
        self.assertAlmostEqual(
            SCALE_TABLE.pr_hoelder_mean(2), 0.22638462845343543
        )
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.pr_hoelder_mean(2), 0.6711293026059334
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_hoelder_mean(2), 0.4766783215358364
        )

        self.assertEqual(UNIT_TABLE.pr_hoelder_mean(3), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_hoelder_mean(3)))
        self.assertAlmostEqual(
            SCALE_TABLE.pr_hoelder_mean(3), 0.2277441728906747
        )
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.pr_hoelder_mean(3), 0.6726059172248808
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_hoelder_mean(3), 0.5297282909519099
        )

        # check equivalences to other specific means
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_hoelder_mean(-1), WORKED_EG_TABLE.pr_hmean()
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_hoelder_mean(0), WORKED_EG_TABLE.pr_gmean()
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_hoelder_mean(1), WORKED_EG_TABLE.pr_amean()
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.pr_hoelder_mean(2), WORKED_EG_TABLE.pr_qmean()
        )

    def test_pr_agmean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_agmean.

        Test values computed via http://arithmeticgeometricmean.blogspot.de/
        """
        self.assertEqual(UNIT_TABLE.pr_agmean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_agmean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_agmean(), 0.2243028580287603)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_agmean(), 0.6688977735879823)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_agmean(), 0.3176780357448827)
        self.assertAlmostEqual(VERY_POOR_TABLE.pr_agmean(), 0.0)

    def test_pr_ghmean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_ghmean."""
        self.assertEqual(UNIT_TABLE.pr_ghmean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_ghmean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_ghmean(), 0.2229128974)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_ghmean(), 0.6674092650)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_ghmean(), 0.2098560781)
        self.assertAlmostEqual(VERY_POOR_TABLE.pr_ghmean(), 0.0)

    def test_pr_aghmean(self):
        """Test abydos.stats._confusion_table.ConfusionTable.pr_aghmean."""
        self.assertEqual(UNIT_TABLE.pr_aghmean(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.pr_aghmean()))
        self.assertAlmostEqual(SCALE_TABLE.pr_aghmean(), 0.2236067977)
        self.assertAlmostEqual(CATSNDOGS_TABLE.pr_aghmean(), 0.6681531047)
        self.assertAlmostEqual(WORKED_EG_TABLE.pr_aghmean(), 0.2581988897)
        self.assertAlmostEqual(VERY_POOR_TABLE.pr_aghmean(), 0.0)


class StatisticalMeasureTestCases(unittest.TestCase):
    """Test abydos.stats._confusion_table.ConfusionTable stats functions."""

    prre = tuple(((i.precision(), i.recall()) for i in ALL_TABLES))

    def test_fbeta_score(self):
        """Test abydos.stats._confusion_table.ConfusionTable.fbeta_score."""
        self.assertEqual(UNIT_TABLE.fbeta_score(1), 0.5)
        self.assertTrue(isnan(NULL_TABLE.fbeta_score(1)))
        self.assertAlmostEqual(SCALE_TABLE.fbeta_score(1), 2 / 9)
        self.assertAlmostEqual(CATSNDOGS_TABLE.fbeta_score(1), 2 / 3)
        self.assertAlmostEqual(WORKED_EG_TABLE.fbeta_score(1), 4 / 23)
        self.assertRaises(AttributeError, UNIT_TABLE.fbeta_score, -1)

    def test_f2_score(self):
        """Test abydos.stats._confusion_table.ConfusionTable.f2_score."""
        self.assertEqual(UNIT_TABLE.f2_score(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.f2_score()))
        self.assertAlmostEqual(SCALE_TABLE.f2_score(), 5 / 24)
        self.assertAlmostEqual(CATSNDOGS_TABLE.f2_score(), 25 / 39)
        self.assertAlmostEqual(WORKED_EG_TABLE.f2_score(), 5 / 16)

    def test_fhalf_score(self):
        """Test abydos.stats._confusion_table.ConfusionTable.fhalf_score."""
        self.assertEqual(UNIT_TABLE.fhalf_score(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.fhalf_score()))
        self.assertAlmostEqual(SCALE_TABLE.fhalf_score(), 5 / 21)
        self.assertAlmostEqual(CATSNDOGS_TABLE.fhalf_score(), 25 / 36)
        self.assertAlmostEqual(WORKED_EG_TABLE.fhalf_score(), 10 / 83)

    def test_e_score(self):
        """Test abydos.stats._confusion_table.ConfusionTable.e_score."""
        self.assertEqual(UNIT_TABLE.e_score(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.e_score()))
        self.assertAlmostEqual(SCALE_TABLE.e_score(), 7 / 9)
        self.assertAlmostEqual(CATSNDOGS_TABLE.e_score(), 1 / 3)
        self.assertAlmostEqual(WORKED_EG_TABLE.e_score(), 19 / 23)

    def test_f1_score(self):
        """Test abydos.stats._confusion_table.ConfusionTable.f1_score."""
        self.assertEqual(UNIT_TABLE.f1_score(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.f1_score()))
        self.assertAlmostEqual(SCALE_TABLE.f1_score(), 2 / 9)
        self.assertAlmostEqual(CATSNDOGS_TABLE.f1_score(), 2 / 3)
        self.assertAlmostEqual(WORKED_EG_TABLE.f1_score(), 4 / 23)

    def test_f_measure(self):
        """Test abydos.stats._confusion_table.ConfusionTable.f_measure."""
        self.assertEqual(UNIT_TABLE.f_measure(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.f_measure()))
        self.assertAlmostEqual(SCALE_TABLE.f_measure(), 2 / 9)
        self.assertAlmostEqual(CATSNDOGS_TABLE.f_measure(), 2 / 3)
        self.assertAlmostEqual(WORKED_EG_TABLE.f_measure(), 4 / 23)

    def test_g_measure(self):
        """Test abydos.stats._confusion_table.ConfusionTable.g_measure."""
        self.assertEqual(UNIT_TABLE.g_measure(), 0.5)
        self.assertTrue(isnan(NULL_TABLE.g_measure()))
        self.assertAlmostEqual(SCALE_TABLE.g_measure(), 0.22360679774997899)
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.g_measure(), 0.66815310478106094
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.g_measure(), 0.25819888974716115
        )

    def test_mcc(self):
        """Test abydos.stats._confusion_table.ConfusionTable.mcc."""
        self.assertEqual(UNIT_TABLE.mcc(), 0)
        self.assertTrue(isnan(NULL_TABLE.mcc()))
        self.assertAlmostEqual(SCALE_TABLE.mcc(), -10 / sqrt(600))
        self.assertAlmostEqual(CATSNDOGS_TABLE.mcc(), 79 / sqrt(21280))
        self.assertAlmostEqual(
            WORKED_EG_TABLE.mcc(), 34600 / sqrt(21960000000)
        )

    def test_significance(self):
        """Test abydos.stats._confusion_table.ConfusionTable.significance."""
        self.assertEqual(UNIT_TABLE.significance(), 0)
        self.assertTrue(isnan(NULL_TABLE.significance()))
        self.assertAlmostEqual(SCALE_TABLE.significance(), 5 / 3)
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.significance(), 79 ** 2 / 21280 * 27
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.significance(), 34600 ** 2 / 21960000000 * 2030
        )

    def test_kappa_statistic(self):
        """Test abydos.stats._confusion_table.ConfusionTable.kappa_statistic."""  # noqa: E501

        def _quick_kappa(acc, racc):
            return (acc - racc) / (1 - racc)

        self.assertEqual(UNIT_TABLE.kappa_statistic(), 0)
        self.assertTrue(isnan(NULL_TABLE.kappa_statistic()))
        self.assertAlmostEqual(
            SCALE_TABLE.kappa_statistic(), _quick_kappa((3 / 10), (1 / 2))
        )
        self.assertAlmostEqual(
            CATSNDOGS_TABLE.kappa_statistic(),
            _quick_kappa((22 / 27), (436 / 27 ** 2)),
        )
        self.assertAlmostEqual(
            WORKED_EG_TABLE.kappa_statistic(),
            _quick_kappa((184 / 203), (((2000 * 1830) + 6000) / 2030 ** 2)),
        )


if __name__ == '__main__':
    unittest.main()
