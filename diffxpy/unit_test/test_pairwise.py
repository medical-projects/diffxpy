import unittest

import numpy as np
import pandas as pd
import scipy.stats as stats

from batchglm.api.models.nb_glm import Simulator, Estimator, InputData
import diffxpy as de


class TestPairwise(unittest.TestCase):

    def test_null_distribution_ztest(self, n_cells: int = 1000, n_genes: int = 1000):
        """
        Test if de.test_wald_loc() generates a uniform p-value distribution
        if it is given data simulated based on the null model. Returns the p-value
        of the two-side Kolmgorov-Smirnov test for equality of the observed 
        p-value distriubution and a uniform distribution.

        :param n_cells: Number of cells to simulate (number of observations per test).
        :param n_genes: Number of genes to simulate (number of tests).
        """

        sim = Simulator(num_observations=n_cells, num_features=n_genes)
        sim.generate_sample_description(num_batches=0, num_confounders=0)
        sim.generate()

        random_sample_description = pd.DataFrame({
            "condition": np.random.randint(2, size=sim.num_observations)
        })

        test = de.test_pairwise(
            data=sim.X,
            grouping="condition",
            test="z-test",
            noise_model="nb",
            sample_description=random_sample_description,
        )

        # Compare p-value distribution under null model against uniform distribution.
        pval_h0 = stats.kstest(test.pval[~np.eye(test.pval.shape[0]).astype(bool)].flatten(), 'uniform').pvalue

        print('KS-test pvalue for null model match of test_wald_loc(): %f' % pval_h0)

        assert pval_h0 > 0.05, "KS-Test failed: pval_h0 is <= 0.05!"

        return pval_h0

    def test_ztest_de(self, n_cells: int = 1000, n_genes: int = 1000):
        """
        Test if de.test_lrt() generates a uniform p-value distribution
        if it is given data simulated based on the null model. Returns the p-value
        of the two-side Kolmgorov-Smirnov test for equality of the observed
        p-value distriubution and a uniform distribution.

        :param n_cells: Number of cells to simulate (number of observations per test).
        :param n_genes: Number of genes to simulate (number of tests).
        """

        num_non_de = n_genes // 2
        sim = Simulator(num_observations=n_cells, num_features=n_genes)
        sim.generate_sample_description(num_batches=0, num_confounders=2)
        # simulate: coefficients ~ log(N(1, 0.5)).
        # re-sample if N(1, 0.5) <= 0
        sim.generate_params(rand_fn=lambda shape: 1 + stats.truncnorm.rvs(-1 / 0.5, np.infty, scale=0.5, size=shape))
        sim.params["a"][1, :num_non_de] = 0
        sim.params["b"][1, :num_non_de] = 0
        sim.params["isDE"] = ("features",), np.arange(n_genes) >= num_non_de
        sim.generate_data()

        sample_description = sim.sample_description

        test = de.test_pairwise(
            data=sim.X,
            grouping="condition",
            test="z-test",
            noise_model="nb",
            sample_description=sample_description,
        )
        summary = test.summary()

        print('fraction of non-DE genes with q-value < 0.05: %.1f%%' %
              (100 * np.mean(
                  np.sum(test.qval[~np.eye(test.pval.shape[0]).astype(bool), :num_non_de] < 0.05) /
                  num_non_de
              )))
        print('fraction of DE genes with q-value < 0.05: %.1f%%' %
              (100 * np.mean(
                  np.sum(test.qval[~np.eye(test.pval.shape[0]).astype(bool), num_non_de:] < 0.05) /
                  (n_genes - num_non_de)
              )))

        return test.qval

    def test_null_distribution_lrt(self, n_cells: int = 1000, n_genes: int = 1000):
        """
        Test if de.test_wald_loc() generates a uniform p-value distribution
        if it is given data simulated based on the null model. Returns the p-value
        of the two-side Kolmgorov-Smirnov test for equality of the observed
        p-value distriubution and a uniform distribution.

        :param n_cells: Number of cells to simulate (number of observations per test).
        :param n_genes: Number of genes to simulate (number of tests).
        """

        sim = Simulator(num_observations=n_cells, num_features=n_genes)
        sim.generate_sample_description(num_batches=0, num_confounders=0)
        sim.generate()

        random_sample_description = pd.DataFrame({
            "condition": np.random.randint(2, size=sim.num_observations)
        })

        test = de.test_pairwise(
            data=sim.X,
            grouping="condition",
            test="lrt",
            noise_model="nb",
            sample_description=random_sample_description,
        )

        # Compare p-value distribution under null model against uniform distribution.
        pval_h0 = stats.kstest(test.pval[~np.eye(test.pval.shape[0]).astype(bool)].flatten(), 'uniform').pvalue

        print('KS-test pvalue for null model match of test_wald_loc(): %f' % pval_h0)

        assert pval_h0 > 0.05, "KS-Test failed: pval_h0 is <= 0.05!"

        return pval_h0

    def test_null_distribution_ttest(self, n_cells: int = 1000, n_genes: int = 1000):
        """
        Test if de.test_wald_loc() generates a uniform p-value distribution
        if it is given data simulated based on the null model. Returns the p-value
        of the two-side Kolmgorov-Smirnov test for equality of the observed
        p-value distriubution and a uniform distribution.

        :param n_cells: Number of cells to simulate (number of observations per test).
        :param n_genes: Number of genes to simulate (number of tests).
        """

        sim = Simulator(num_observations=n_cells, num_features=n_genes)
        sim.generate_sample_description(num_batches=0, num_confounders=0)
        sim.generate()

        random_sample_description = pd.DataFrame({
            "condition": np.random.randint(2, size=sim.num_observations)
        })

        test = de.test_pairwise(
            data=sim.X,
            grouping="condition",
            test="t-test",
            sample_description=random_sample_description,
        )

        # Compare p-value distribution under null model against uniform distribution.
        pval_h0 = stats.kstest(test.pval[~np.eye(test.pval.shape[0]).astype(bool)].flatten(), 'uniform').pvalue

        print('KS-test pvalue for null model match of test_wald_loc(): %f' % pval_h0)

        assert pval_h0 > 0.05, "KS-Test failed: pval_h0 is <= 0.05!"

        return pval_h0

    def test_null_distribution_wilcoxon(self, n_cells: int = 1000, n_genes: int = 1000):
        """
        Test if de.test_wald_loc() generates a uniform p-value distribution
        if it is given data simulated based on the null model. Returns the p-value
        of the two-side Kolmgorov-Smirnov test for equality of the observed
        p-value distriubution and a uniform distribution.

        :param n_cells: Number of cells to simulate (number of observations per test).
        :param n_genes: Number of genes to simulate (number of tests).
        """

        sim = Simulator(num_observations=n_cells, num_features=n_genes)
        sim.generate_sample_description(num_batches=0, num_confounders=0)
        sim.generate()

        random_sample_description = pd.DataFrame({
            "condition": np.random.randint(2, size=sim.num_observations)
        })

        test = de.test_pairwise(
            data=sim.X,
            grouping="condition",
            test="wilcoxon",
            sample_description=random_sample_description,
        )

        # Compare p-value distribution under null model against uniform distribution.
        pval_h0 = stats.kstest(test.pval[~np.eye(test.pval.shape[0]).astype(bool)].flatten(), 'uniform').pvalue

        print('KS-test pvalue for null model match of test_wald_loc(): %f' % pval_h0)

        assert pval_h0 > 0.05, "KS-Test failed: pval_h0 is <= 0.05!"

        return pval_h0


if __name__ == '__main__':
    unittest.main()
