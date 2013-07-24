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

'''Unit tests for the Dataset.py module'''

import unittest
from dataset import Dataset
import numpy as np
import datetime as dt

class TestDatasetAttributes(unittest.TestCase):
    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.value = flat_array.reshape(12, 5, 5)
        self.variable = 'prec'
        self.test_dataset = Dataset(self.lat, self.lon, self.time, 
                                    self.value, self.variable)

    def test_lats(self):
        self.assertItemsEqual(self.test_dataset.lats, self.lat)

    def test_lons(self):
        self.assertItemsEqual(self.test_dataset.lons, self.lon)

    def test_times(self):
        self.assertItemsEqual(self.test_dataset.times, self.time)

    def test_values(self):
        self.assertEqual(self.test_dataset.values.all(), self.value.all())

    def test_variable(self):
        self.assertEqual(self.test_dataset.variable, self.variable)


class TestDatasetFunctions(unittest.TestCase):
    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.value = flat_array.reshape(12, 5, 5)
        self.variable = 'prec'
        self.test_dataset = Dataset(self.lat, self.lon, self.time, 
                                     self.value, self.variable)

    def test_spatial_boundaries(self):
        self.assertEqual(
            self.test_dataset.spatial_boundaries(), 
            (min(self.lat), max(self.lat), min(self.lon), max(self.lon)))

    def test_time_range(self):
        self.assertEqual(
            self.test_dataset.time_range(), 
            (dt.datetime(2000, 1, 1), dt.datetime(2000, 12, 1)))

    def test_spatial_resolution(self):
        self.assertEqual(self.test_dataset.spatial_resolution(), (2, 2))

    def test_temporal_resolution(self):
        self.assertEqual(self.test_dataset.temporal_resolution(), 'monthly')


if __name__ == '__main__':
    unittest.main()