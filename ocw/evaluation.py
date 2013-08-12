# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

'''
Classes: 
    Evaluation - Container for running an evaluation
'''

import logging
from metrics import Metric
from dataset import Dataset
import dataset_processor as DSP

class Evaluation:
    '''Container for running an evaluation

    An *Evaluation* is the running of one or more metrics on one or more 
    target datasets and a (possibly optional) reference dataset. Evaluation
    can handle two types of metrics, ``unary`` and ``binary``. The validity
    of an Evaluation is dependent upon the number and type of metrics as well
    as the number of datasets.

    A ``unary`` metric is a metric that runs over a single dataset. If you add
    a ``unary`` metric to the Evaluation you are only required to add a 
    reference dataset or a target dataset. If there are multiple datasets
    in the evaluation then the ``unary`` metric is run over all of them.

    A ``binary`` metric is a metric that runs over a reference dataset and
    target dataset. If you add a ``binary`` metric you are required to add a
    reference dataset and at least one target dataset. The ``binary`` metrics
    are run over ever (reference dataset, target dataset) pair in the
    Evaluation.

    An Evaluation must have at least one metric to be valid. 
    '''

    def __init__(self, reference, targets, metrics, subregions=None):
        '''Default Evaluation constructor.

        :param reference: The reference Dataset for the evaluation.
        :type reference: Dataset
        :param targets: A list of one or more target datasets for the 
                evaluation.
        :type targets: List of Datasets
        :param metrics: A list of one or more Metric instances to run 
                in the evaluation.
        :type metrics: List of Metrics
        :param subregions: (Optional) Subregion information to use in the
                evaluation. A subregion is specified by a bounds of the form
                [latMin, lonMin, latMax, lonMax].
        :type subregions: List of bounds 

        :raises: ValueError 
        '''
        #: The reference dataset.
        self.ref_dataset = reference
        #: The target dataset(s) which should each be compared with 
        #: the reference dataset when the evaluation is run.
        self.target_datasets = []
        self.add_datasets(targets)

        #: The list of "binary" metrics (A metric which takes two Datasets) 
        #: that the Evaluation should use.
        self.metrics = []
        #: The list of "unary" metrics (A metric which takes one Dataset) that
        #: the Evaluation should use.
        self.unary_metrics = []

        # Metrics need to be added to specific lists depending on whether they
        # are "binary" or "unary" metrics.
        self.add_metrics(metrics)

        #: An optional list of subregion bounds to use when running the
        #: evaluation. 
        self.subregions = subregions

        #: A list containing the results of running regular metric evaluations. 
        #: The shape of results is ``(num_metrics, num_target_datasets)`` if
        #: the user doesn't specify subregion information. Otherwise the shape
        #: is ``(num_metrics, num_target_datasets, num_subregions)``.
        self.results = []
        #: A list containing the results of running the unary metric 
        #: evaluations. The shape of unary_results is 
        #: ``(num_metrics, num_targets)`` where ``num_targets = 
        #: num_target_ds + (1 if ref_dataset != None else 0``
        self.unary_results = []

    def add_dataset(self, target_dataset):
        '''Add a Dataset to the Evaluation.

        A target Dataset is compared against the reference dataset when the 
        Evaluation is run with one or more metrics.

        :param target_dataset: The target Dataset to add to the Evaluation.
        :type target_dataset: Dataset

        :raises ValueError: If a dataset to add isn't an instance of Dataset.
        '''
        if not isinstance(target_dataset, Dataset):
            error = (
                "Cannot add a dataset that isn't an instance of Dataset. "
                "Please consult the documentation for additional help."
            )
            logging.error(error)
            raise TypeError(error)

        self.target_datasets.append(target_dataset)

    def add_datasets(self, target_datasets):
        '''Add multiple Datasets to the Evaluation.

        :param target_datasets: The list of datasets that should be added to 
            the Evaluation.
        :type target_datasets: List of Dataset objects

        :raises ValueError: If a dataset to add isn't an instance of Dataset.
        '''
        for target in target_datasets:
            self.add_dataset(target)

    def add_metric(self, metric):
        '''Add a metric to the Evaluation.

        A metric is an instance of a class which inherits from metrics.Metric.

        :param metric: The metric instance to add to the Evaluation.
        :type metric: Metric

        :raises ValueError: If the metric to add isn't a class that inherits
                from metrics.Metric.
        '''
        if not isinstance(metric, Metric):
            error = (
                "Cannot add a metric that doesn't inherit from Metric. "
                "Please consult the documentation for additional help."
            )
            logging.error(error)
            raise TypeError(error)

        if metric.is_unary:
            self.unary_metrics.append(metric)
        else:
            self.metrics.append(metric)

    def add_metrics(self, metrics):
        '''Add multiple metrics to the Evaluation.

        A metric is an instance of a class which inherits from metrics.Metric.

        :param metrics: The list of metric instances to add to the Evaluation.
        :type metrics: List of Metrics

        :raises ValueError: If a metric to add isn't a class that inherits
                from metrics.Metric.
        '''
        for metric in metrics:
            self.add_metric(metric)


    def run(self):
        '''Run the evaluation.'''
        if not self._evaluation_is_valid():
            error = "The evaluation is invalid. Check the docs for help."
            logging.warning(error)
            return

        if _should_run_regular_metrics():
            if self.subregions:
                self.results = _run_subregion_evaluation()
            else:
                self.results = _run_no_subregion_evaluation()

        if _should_run_unary_metrics():
            self.unary_results = _run_unary_metric_evaluation()

    def _evaluation_is_valid(self):
        '''Check if the evaluation is well-formed.
        
        * If there are no metrics or no datasets it's invalid.
        * If there is a unary metric there must be a reference dataset or at
            least one target dataset.
        * If there is a regular metric there must be a reference dataset and
            at least one target dataset.
        '''
        run_reg = _should_run_regular_metrics()
        run_unary = _should_run_unary_metrics()
        reg_valid = self.ref_dataset != None and len(self.target_datasets) > 0
        unary_valid = self.ref_dataset != None or len(self.target_datasets) > 0

        if run_reg and run_unary:
            return reg_valid and unary_valid
        elif run_reg:
            return reg_valid
        elif run_unary:
            return unary_valid
        else:
            return false

    def _should_run_regular_metrics():
        return len(self.metrics) > 0

    def _should_run_unary_metrics():
        return len(self.unary_metrics) > 0

    def _run_subregion_evaluation():
        results = []
        for target in self.target_datasets:
            results.append([])
            for metric in self.metrics:
                results[-1].append([])
                for subregion in self.subregions:
                    # Subset the reference and target dataset with the 
                    # subregion information.
                    new_ref, new_tar = DSP.subset(subregion,
                                                  [self.ref_dataset, target])
                    run_result = [metric.run(new_ref, new_tar)]
                    results[-1][-1].append(run_result)
        return results

    def _run_no_subregion_evaluation():
        results = []
        for target in self.target_datasets:
            results.append([])
            for metric in self.metrics:
                run_result = [metric.run(self.ref_dataset, target)]
                results[-1].append(run_result)
        return results

    def _run_unary_metric_evaluation():
        unary_results = []
        for metric in self.unary_metrics:
            unary_results.append([])
            # Unary metrics should be run over the reference Dataset also
            if self.ref_dataset:
                unary_results[-1].append(metric.run(ref_dataset))

            for target in self.target_datasets:
                unary_results[-1].append(metric.run(target))