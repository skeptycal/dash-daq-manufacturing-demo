import random


class FactoryData(object):

    def __init__(self, process_names=None):

        if process_names is None:
            process_names = []

        self._process_names = process_names

    def get_data(self):
        return {
            pname: self._sample_data(pname) for pname in self._process_names
        }

    def _sample_data(self, process_name):

        base_value = random.random()
        
        data = {
            'cycle_time': 6 + base_value,
            'time_to_complete': 8 - base_value * 2,
            'safety_materials': 'red' if base_value < 0.01 else 'orange',
            'safety_manufacturing': 'orange' if base_value < 0.1 else 'green',
            'safety_packing': 'yellow' if base_value < 0.05 else 'orange',
            'precursor_level': 95 + (base_value - 0.5) * 5,
            'reagent_level': 50 + (base_value - 0.5) * 5,
            'catalyst_level': 73 + (base_value - 0.5) * 10,
            'packaging_level': 88 + (base_value - 0.5) * 10,
            'production_levels': (base_value - 0.01) * 5,
        }

        return data[process_name]
