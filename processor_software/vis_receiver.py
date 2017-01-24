# -*- coding: utf-8 -*-
"""Module to provide visibility receiver function.

This currently consists of the VisReceiver class which reads spead packets
and writes them to pickle files.
"""
import pickle
import spead2
import spead2.recv


class VisReceiver:
    """Receives visibility data using SPEAD."""

    def __init__(self, config, log):
        """Constructor.

        Creates SPEAD stream objects.
        The supplied configuration dictionary must contain all parameters
        needed for setting up the SPEAD streams and output files.

        See vis_receiver_config.json for an example.

        Args:
            config (dict): Dictionary containing JSON configuration file.
            log: Logger.
        """
        # Initialise class variables.
        self._config = config
        self._log = log
        self._streams = []

        # Construct streams.
        # bug_compat = spead2.BUG_COMPAT_PYSPEAD_0_5_2
        bug_compat = 0
        lower = config['memory_pool']['lower']
        upper = config['memory_pool']['upper']
        max_free = config['memory_pool']['max_free']
        initial = config['memory_pool']['initial']
        log.info('Creating streams...')
        for stream in config['streams']:
            log.debug('Creating stream on port {}'.format(stream['port']))
            s = spead2.recv.Stream(spead2.ThreadPool(), bug_compat)
            pool = spead2.MemoryPool(lower, upper, max_free, initial)
            s.set_memory_allocator(pool)
            s.add_udp_reader(stream['port'])
            self._streams.append(s)

    def run(self):
        """Start the visibility receiver to receive SPEAD heaps.

        Reads SPEAD heaps and writes them to pickle files.
        """
        # ms = {}
        self._log.info('Waiting to receive...')
        self._log.info("I am here i amd i wasnt to")
        for stream in self._streams:
            item_group = spead2.ItemGroup()

            # Loop over all heaps in the stream.
            for heap in stream:
                self._log.info("Received heap {}".format(heap.cnt))

                # Extract data from the heap into a dictionary.
                data = {}
                items = item_group.update(heap)
                for item in items.values():
                    data[item.name] = item.value

                # Skip if the heap does not contain visibilities.
                if 'complex_visibility' not in data:
                    continue

                # Get data dimensions.
                time_index = heap.cnt - 2  # Extra -1: first heap is empty.
                start_channel = data['channel_baseline_id'][0][0]
                num_channels = data['channel_baseline_count'][0][0]
                max_per_file = self._config['output']['max_times_per_file']

                # Find out which file this heap goes in.
                # Get the time and channel range for the file.
                file_start_time = (time_index // max_per_file) * max_per_file
                file_end_time = file_start_time + max_per_file - 1

                # Construct filename.
                base_name = 'vis_T%04d-%04d_C%04d-%04d' % (
                    file_start_time, file_end_time,
                    start_channel, start_channel + num_channels - 1)
                data['time_index'] = time_index

                # Write visibility data.
                with open(base_name + '.p', 'ab') as f:
                    pickle.dump(data, f, protocol=2)

                # Write to Measurement Set if required.
                # ms_name = base_name + '.ms'
                # if ms_name not in ms:
                #     if len(ms) > 5:
                #         ms.popitem()  # Don't open too many files at once.
                #     ms[ms_name] = _ms_create(
                #         ms_name, config, start_channel, num_channels) \
                #         if not os.path.isdir(ms_name) else _ms_open(ms_name)
                # _ms_write(ms[ms_name], file_start_time, start_channel, data)

            # Stop the stream when there are no more heaps.
            stream.stop()
