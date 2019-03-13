# Simple SPEAD UDP Receiver in C

This directory contains C code for a visibility receiver capable of receiving UDP-based SPEAD streams containing the item identifiers specified in the current version of the SDP-CSP interface control document. The data received can be optionally written out to storage.

## Network Performance

The receiver has been tested using the 7-node Docker Swarm cluster on the P3-ALaSKA system, and is capable of sustainably receiving data at a rate of (at least) 2.9 GB/s (23.2 Gb/s) using the 25 GbE network. This test used 432 separate SPEAD streams to simulate the expected use case of 1-channel-per-stream, and to achieve this rate, it was necessary to use at least 4 receiver threads: A single-threaded receiver was capable of receiving only around 970 MB/s. This receiver works well on the 16-core-per-socket ALaSKA system using 4, 8 or 16 receiver threads, but using more than 4 threads does not seem to be advantageous. Average CPU usage with 4 receiver threads (without writing data) was 10%, as reported on the Grafana dashboard, and with 16 receiver threads was 13%.

With 432 streams and a buffer size of 8 samples per stream, the size of the in-memory buffer was 15.4 GB. Multiple buffers are used to allow for concurrent receiving and writing of data to storage: A buffer will be locked for writing if no data packets have been written to it for more than 1 second, and it will not be considered for re-use by receive until the write has completed.

In order to reach the node's input data rate of 2.9 GB/s, it was necessary to use all the other 6 nodes of the Swarm cluster to send 72 streams (about 485 MB/s) each. Although the start time of the sender nodes was synchronised to within 0.1 seconds, after running for about two hours, the senders become sufficiently out-of-sync for data to start having to be discarded. This is indicated by warnings written to the log, such as the following:

```
2019-02-14T17:36:58.278751000Z | Re-assigned buffer 1
2019-02-14T17:36:58.279110000Z | WARNING: Incomplete buffer (19231039740/19289456640, 99.7%)
2019-02-14T17:36:58.279501000Z | Received 1000.633 MB in 0.373 sec (2679.94 MB/s), memcpy was 0.29%
2019-02-14T17:36:58.279909000Z | WARNING: Dumped 52513686 bytes
2019-02-14T17:37:03.470323000Z | Received 1001.688 MB in 0.336 sec (2982.59 MB/s), memcpy was 0.29%
2019-02-14T17:37:03.470851000Z | WARNING: Dumped 5903214 bytes
```

It may be possible to create a faster sender to alleviate this problem in the future.

## Storage Performance

To write the received data to storage, an output directory must be specified on the command line.

The receiver has been tested successfully using the BeeGFS filesystem mount points available on the Swarm cluster, backed by both NVMe and SSD storage, on `/mnt/storage-nvme` and `/mnt/storage-ssd`. Using multiple threads to write each buffer, the storage performance from a single container is very good; 8 writer threads seems close to optimal with ~143 MB files and a ~18 MB block size, where each thread writes 4 channels at once. (Using 16 threads for the write caused small amounts of data to be dropped by the receiver, presumably because of contention.)

All threads used by the application were pinned to the first CPU socket (the first 32 out of 64 reported cores) using the `CPU_SET` and `sched_setaffinity()` functions provided by the Linux scheduler, to ensure that memory allocations and acceses would be local to the socket.

During a test lasting around 26 minutes, a total of ~4.2 TiB of data was successfully received and written out to storage on `/mnt/storage-ssd` without losing a single byte. The measured write rate was consistently around 10 GB/s using 8 writer threads (although that may have been the bandwidth to external buffers on other nodes, as the total capacity here is reported as 67 TB). The `/mnt/storage-nvme` partition, which has a 12 TB capacity, performed similarly well at ~6.8 GB/s using 8 writer threads.

## Testing

To run the test on P3-ALaSKA, it is sufficient to deploy the Compose file found in the parent directory.
*Before running the test, check that the IP address of the receiver node (all `destination_host` values) is still correct!* (It may need to be updated if the Swarm cluster has been rebuilt.) Also check that the mount point bound into the container is valid.

The Docker image used for the receiver should be at least `skasip/vis_recv_c:1.3.1`.

To deploy all services (6 senders and 1 receiver; execute this command just past the minute or half-minute mark, as the senders will start based on the current time. Around 20 seconds should be long enough for everything to start up):

```bash
docker stack deploy -c docker-compose-p3-c-multi-sender.yml i
```

To inspect the logs from the receiver:

```bash
docker service logs -t i_recv
```

To end the test:

```bash
docker stack rm i
```

To remove files written to `/mnt/storage-ssd/ingest` storage after the test completes:

```bash
docker run --rm -it --mount "type=bind,src=/mnt/storage-ssd/ingest,dst=/app/output" ubuntu /bin/bash -c "rm /app/output/ingest*"
```

or if using `/mnt/storage-nvme/ingest`:

```bash
docker run --rm -it --mount "type=bind,src=/mnt/storage-nvme/ingest,dst=/app/output" ubuntu /bin/bash -c "rm /app/output/ingest*"
```

## Sample Output

Screenshots of the Grafana dashboard panels are shown below. Node 1 was designated as the receiver node, while the other 6 nodes were used to send data.

![Sender node rate](https://drive.google.com/uc?id=10EIX-UxSq-536SOAJy99-dEjiM-q5TCh "")

![Receiver node rate](https://drive.google.com/uc?id=1vOqTaQP-46e-p-3YQB0ybZQAK9DSOLgF "")

![CPU and memory usage](https://drive.google.com/uc?id=1tyA4fQriveDQPZ326lMp1WY54t5bcqHl "")

Some sample output from `docker service logs i_recv` is shown below:

```
2019-03-11T21:05:40.445730000Z | Running RECV_VERSION 1.3.1
2019-03-11T21:05:58.686942000Z |  + Number of system CPU cores  : 64
2019-03-11T21:05:58.687519000Z |  + Number of SPEAD streams     : 432
2019-03-11T21:05:58.687851000Z |  + Number of receiver threads  : 4
2019-03-11T21:05:58.688184000Z |  + Number of writer threads    : 8
2019-03-11T21:05:58.688520000Z |  + Number of times in buffer   : 8
2019-03-11T21:05:58.688840000Z |  + Maximum number of buffers   : 3
2019-03-11T21:05:58.689143000Z |  + UDP port range              : 41000-41431
2019-03-11T21:05:58.689428000Z |  + Number of channels per file : 4
2019-03-11T21:05:58.689750000Z |  + Output root                 : /app/output/ingest_run_20190311-210540
2019-03-11T21:05:58.690066000Z | Received 0.000 MB in 1.000 sec (0.00 MB/s), memcpy was 0.00%
<snip>
2019-03-11T21:06:05.140319000Z | Allocating 15431.565 MB buffer.
2019-03-11T21:06:05.140742000Z | Created buffer 0
2019-03-11T21:06:05.141094000Z | Received 1000.803 MB in 0.957 sec (1046.16 MB/s), memcpy was 0.18%
2019-03-11T21:06:05.141488000Z | Received 1001.367 MB in 0.333 sec (3008.84 MB/s), memcpy was 0.47%
2019-03-11T21:06:05.141929000Z | Received 1003.564 MB in 0.347 sec (2893.10 MB/s), memcpy was 0.46%
2019-03-11T21:06:05.142277000Z | Received 1002.445 MB in 0.349 sec (2872.47 MB/s), memcpy was 0.46%
2019-03-11T21:06:05.142670000Z | Received 1002.101 MB in 0.336 sec (2986.78 MB/s), memcpy was 0.47%
2019-03-11T21:06:05.143030000Z | Received 1001.223 MB in 0.354 sec (2828.29 MB/s), memcpy was 0.44%
2019-03-11T21:06:05.143384000Z | Received 1000.652 MB in 0.333 sec (3003.64 MB/s), memcpy was 0.47%
2019-03-11T21:06:05.143764000Z | Received 1002.572 MB in 0.361 sec (2779.35 MB/s), memcpy was 0.44%
2019-03-11T21:06:05.144153000Z | Received 1003.242 MB in 0.348 sec (2884.76 MB/s), memcpy was 0.48%
2019-03-11T21:06:05.144517000Z | Received 1002.831 MB in 0.350 sec (2865.74 MB/s), memcpy was 0.48%
2019-03-11T21:06:05.144878000Z | Received 1003.242 MB in 0.344 sec (2916.97 MB/s), memcpy was 0.48%
2019-03-11T21:06:05.145240000Z | Received 1000.500 MB in 0.350 sec (2856.06 MB/s), memcpy was 0.48%
2019-03-11T21:06:05.145630000Z | Received 1003.242 MB in 0.350 sec (2862.97 MB/s), memcpy was 0.48%
2019-03-11T21:06:09.645052000Z | Received 1002.099 MB in 0.341 sec (2938.62 MB/s), memcpy was 0.48%
2019-03-11T21:06:09.645765000Z | Received 1003.242 MB in 0.346 sec (2900.18 MB/s), memcpy was 0.48%
2019-03-11T21:06:09.646141000Z | Allocating 15431.565 MB buffer.
2019-03-11T21:06:09.646639000Z | Created buffer 1
2019-03-11T21:06:09.647028000Z | Received 1001.295 MB in 0.339 sec (2954.18 MB/s), memcpy was 0.47%
2019-03-11T21:06:09.647379000Z | Received 1003.242 MB in 0.359 sec (2794.04 MB/s), memcpy was 0.46%
2019-03-11T21:06:09.647759000Z | Received 1002.635 MB in 0.349 sec (2872.73 MB/s), memcpy was 0.47%
2019-03-11T21:06:09.648130000Z | Locked buffer 0 for writing
2019-03-11T21:06:09.648529000Z | Writing buffer 0 from CPU 21...
2019-03-11T21:06:09.648914000Z | Received 1003.242 MB in 0.363 sec (2764.13 MB/s), memcpy was 0.48%
2019-03-11T21:06:09.649309000Z | Received 1002.876 MB in 0.347 sec (2891.00 MB/s), memcpy was 0.48%
2019-03-11T21:06:09.649661000Z | Received 1003.242 MB in 0.359 sec (2797.56 MB/s), memcpy was 0.47%
2019-03-11T21:06:09.650034000Z | Received 1002.876 MB in 0.357 sec (2805.69 MB/s), memcpy was 0.48%
2019-03-11T21:06:09.650367000Z | Writing buffer 0 with 8 threads took 1.41 sec (10940.53 MB/s)
2019-03-11T21:06:09.650766000Z | Received 1002.798 MB in 0.336 sec (2982.47 MB/s), memcpy was 0.48%
2019-03-11T21:06:09.651154000Z | Received 1003.320 MB in 0.327 sec (3069.28 MB/s), memcpy was 0.48%
2019-03-11T21:06:09.651522000Z | Received 1000.880 MB in 0.330 sec (3028.69 MB/s), memcpy was 0.48%
2019-03-11T21:06:09.651894000Z | Received 1000.710 MB in 0.340 sec (2946.54 MB/s), memcpy was 0.47%
2019-03-11T21:06:14.120782000Z | Received 1002.591 MB in 0.353 sec (2836.63 MB/s), memcpy was 0.46%
2019-03-11T21:06:14.121688000Z | Received 1000.052 MB in 0.349 sec (2869.01 MB/s), memcpy was 0.48%
2019-03-11T21:06:14.122183000Z | Received 1000.676 MB in 0.350 sec (2855.22 MB/s), memcpy was 0.48%
2019-03-11T21:06:14.122642000Z | Received 1002.941 MB in 0.366 sec (2742.40 MB/s), memcpy was 0.46%
2019-03-11T21:06:14.123064000Z | Re-assigned buffer 0
2019-03-11T21:06:14.123540000Z | Received 1001.331 MB in 0.322 sec (3108.19 MB/s), memcpy was 0.44%
2019-03-11T21:06:14.123949000Z | Received 1000.777 MB in 0.328 sec (3055.80 MB/s), memcpy was 0.17%
2019-03-11T21:06:14.124366000Z | Received 1000.563 MB in 0.363 sec (2757.22 MB/s), memcpy was 0.15%
2019-03-11T21:06:14.124806000Z | Locked buffer 1 for writing
2019-03-11T21:06:14.125231000Z | Writing buffer 1 from CPU 23...
2019-03-11T21:06:14.125658000Z | Received 1001.081 MB in 0.328 sec (3051.96 MB/s), memcpy was 0.17%
2019-03-11T21:06:14.126038000Z | Received 1000.866 MB in 0.363 sec (2755.56 MB/s), memcpy was 0.14%
2019-03-11T21:06:14.126420000Z | Received 1001.125 MB in 0.328 sec (3054.52 MB/s), memcpy was 0.15%
2019-03-11T21:06:14.126795000Z | Received 1000.366 MB in 0.362 sec (2760.62 MB/s), memcpy was 0.14%
2019-03-11T21:06:14.127149000Z | Writing buffer 1 with 8 threads took 1.37 sec (11238.20 MB/s)
2019-03-11T21:06:14.127575000Z | Received 1000.929 MB in 0.328 sec (3054.58 MB/s), memcpy was 0.16%
2019-03-11T21:06:14.127955000Z | Received 1001.036 MB in 0.362 sec (2768.77 MB/s), memcpy was 0.14%
2019-03-11T21:06:18.925344000Z | Received 1000.313 MB in 0.328 sec (3053.47 MB/s), memcpy was 0.17%
2019-03-11T21:06:18.926133000Z | Received 1000.134 MB in 0.362 sec (2759.65 MB/s), memcpy was 0.15%
2019-03-11T21:06:18.926542000Z | Received 1000.277 MB in 0.328 sec (3051.36 MB/s), memcpy was 0.17%
2019-03-11T21:06:18.926952000Z | Received 1000.036 MB in 0.362 sec (2762.50 MB/s), memcpy was 0.14%
2019-03-11T21:06:18.927347000Z | Received 1000.250 MB in 0.327 sec (3055.31 MB/s), memcpy was 0.16%
2019-03-11T21:06:18.927725000Z | Received 1001.643 MB in 0.362 sec (2763.65 MB/s), memcpy was 0.15%
2019-03-11T21:06:18.928073000Z | Received 1001.590 MB in 0.328 sec (3054.38 MB/s), memcpy was 0.16%
2019-03-11T21:06:18.928508000Z | Re-assigned buffer 1
2019-03-11T21:06:18.928886000Z | Received 1002.947 MB in 0.365 sec (2748.51 MB/s), memcpy was 0.33%
2019-03-11T21:06:18.929251000Z | Received 1003.083 MB in 0.443 sec (2264.89 MB/s), memcpy was 0.42%
2019-03-11T21:06:18.929685000Z | Locked buffer 0 for writing
2019-03-11T21:06:18.929955000Z | Writing buffer 0 from CPU 29...
2019-03-11T21:06:18.930237000Z | Received 1003.232 MB in 0.609 sec (1646.38 MB/s), memcpy was 0.40%
2019-03-11T21:06:18.930558000Z | Received 1002.059 MB in 0.398 sec (2519.62 MB/s), memcpy was 0.40%
2019-03-11T21:06:18.930887000Z | Received 1000.201 MB in 0.330 sec (3032.97 MB/s), memcpy was 0.42%
2019-03-11T21:06:18.931155000Z | Received 1000.979 MB in 0.322 sec (3111.47 MB/s), memcpy was 0.43%
2019-03-11T21:06:18.931480000Z | Writing buffer 0 with 8 threads took 1.42 sec (10835.72 MB/s)
2019-03-11T21:06:23.830925000Z | Received 1001.280 MB in 0.268 sec (3735.02 MB/s), memcpy was 0.38%
2019-03-11T21:06:23.831670000Z | Received 1003.582 MB in 0.276 sec (3634.44 MB/s), memcpy was 0.37%
2019-03-11T21:06:23.832103000Z | Received 1002.536 MB in 0.213 sec (4704.60 MB/s), memcpy was 0.23%
2019-03-11T21:06:23.832542000Z | Received 1000.090 MB in 0.270 sec (3709.08 MB/s), memcpy was 0.19%
2019-03-11T21:06:23.832931000Z | Received 1000.419 MB in 0.329 sec (3042.40 MB/s), memcpy was 0.15%
2019-03-11T21:06:23.833329000Z | Received 1000.473 MB in 0.362 sec (2765.59 MB/s), memcpy was 0.14%
2019-03-11T21:06:23.833804000Z | Received 1000.500 MB in 0.328 sec (3052.23 MB/s), memcpy was 0.16%
2019-03-11T21:06:23.834189000Z | Received 1000.178 MB in 0.362 sec (2766.40 MB/s), memcpy was 0.15%
2019-03-11T21:06:23.834624000Z | Received 1000.875 MB in 0.328 sec (3053.18 MB/s), memcpy was 0.16%
2019-03-11T21:06:23.834971000Z | Re-assigned buffer 0
2019-03-11T21:06:23.835330000Z | Received 1003.412 MB in 0.367 sec (2734.60 MB/s), memcpy was 0.14%
2019-03-11T21:06:23.835767000Z | Received 1000.241 MB in 0.325 sec (3074.71 MB/s), memcpy was 0.15%
2019-03-11T21:06:23.836150000Z | Received 1001.045 MB in 0.363 sec (2760.63 MB/s), memcpy was 0.13%
2019-03-11T21:06:23.836584000Z | Locked buffer 1 for writing
2019-03-11T21:06:23.836988000Z | Writing buffer 1 from CPU 1...
2019-03-11T21:06:23.837373000Z | Received 1003.430 MB in 0.338 sec (2969.93 MB/s), memcpy was 0.16%
2019-03-11T21:06:23.837836000Z | Received 1002.519 MB in 0.365 sec (2744.07 MB/s), memcpy was 0.20%
2019-03-11T21:06:23.838237000Z | Received 1001.250 MB in 0.317 sec (3160.27 MB/s), memcpy was 0.21%
2019-03-11T21:06:28.336416000Z | Received 1001.581 MB in 0.364 sec (2753.43 MB/s), memcpy was 0.18%
2019-03-11T21:06:28.337163000Z | Received 1001.241 MB in 0.328 sec (3051.38 MB/s), memcpy was 0.20%
2019-03-11T21:06:28.337594000Z | Received 1001.366 MB in 0.363 sec (2759.39 MB/s), memcpy was 0.19%
2019-03-11T21:06:28.338027000Z | Received 1000.375 MB in 0.327 sec (3055.49 MB/s), memcpy was 0.21%
2019-03-11T21:06:28.338425000Z | Writing buffer 1 with 8 threads took 2.46 sec (6280.82 MB/s)
2019-03-11T21:06:28.338831000Z | Received 1000.214 MB in 0.363 sec (2755.15 MB/s), memcpy was 0.17%
2019-03-11T21:06:28.339241000Z | Received 1003.323 MB in 0.332 sec (3024.98 MB/s), memcpy was 0.16%
2019-03-11T21:06:28.339670000Z | Received 1000.169 MB in 0.360 sec (2780.07 MB/s), memcpy was 0.14%
2019-03-11T21:06:28.340029000Z | Received 1000.065 MB in 0.333 sec (3002.79 MB/s), memcpy was 0.16%
2019-03-11T21:06:28.340405000Z | Received 1000.480 MB in 0.357 sec (2800.72 MB/s), memcpy was 0.15%
2019-03-11T21:06:28.340829000Z | Re-assigned buffer 1
2019-03-11T21:06:28.341207000Z | Received 1000.903 MB in 0.339 sec (2953.95 MB/s), memcpy was 0.16%
2019-03-11T21:06:28.341641000Z | Received 1001.499 MB in 0.352 sec (2842.25 MB/s), memcpy was 0.16%
2019-03-11T21:06:28.341994000Z | Received 1000.435 MB in 0.350 sec (2859.28 MB/s), memcpy was 0.16%
2019-03-11T21:06:28.342355000Z | Received 1000.261 MB in 0.341 sec (2930.32 MB/s), memcpy was 0.15%
2019-03-11T21:06:28.342769000Z | Locked buffer 0 for writing
2019-03-11T21:06:28.343093000Z | Writing buffer 0 from CPU 5...
2019-03-11T21:06:33.374574000Z | Received 1001.191 MB in 0.360 sec (2784.36 MB/s), memcpy was 0.19%
2019-03-11T21:06:33.375277000Z | Received 1000.112 MB in 0.333 sec (3002.27 MB/s), memcpy was 0.20%
2019-03-11T21:06:33.375756000Z | Received 1001.881 MB in 0.362 sec (2771.12 MB/s), memcpy was 0.19%
2019-03-11T21:06:33.376169000Z | Received 1000.709 MB in 0.328 sec (3051.31 MB/s), memcpy was 0.22%
2019-03-11T21:06:33.376655000Z | Received 1002.001 MB in 0.363 sec (2756.55 MB/s), memcpy was 0.19%
2019-03-11T21:06:33.377063000Z | Writing buffer 0 with 8 threads took 1.99 sec (7750.98 MB/s)
2019-03-11T21:06:33.377419000Z | Received 1000.589 MB in 0.326 sec (3064.70 MB/s), memcpy was 0.20%
2019-03-11T21:06:33.377835000Z | Received 1001.054 MB in 0.362 sec (2768.04 MB/s), memcpy was 0.17%
2019-03-11T21:06:33.378211000Z | Received 1000.706 MB in 0.328 sec (3055.18 MB/s), memcpy was 0.18%
2019-03-11T21:06:33.378598000Z | Received 1001.232 MB in 0.363 sec (2759.11 MB/s), memcpy was 0.20%
2019-03-11T21:06:33.379032000Z | Received 1000.313 MB in 0.333 sec (3002.37 MB/s), memcpy was 0.29%
2019-03-11T21:06:33.379393000Z | Received 1001.992 MB in 0.530 sec (1889.48 MB/s), memcpy was 0.44%
2019-03-11T21:06:33.379777000Z | Received 1003.242 MB in 0.564 sec (1780.37 MB/s), memcpy was 0.39%
2019-03-11T21:06:33.380170000Z | Re-assigned buffer 0
2019-03-11T21:06:33.380513000Z | Received 1002.876 MB in 0.377 sec (2661.30 MB/s), memcpy was 0.36%
2019-03-11T21:06:33.380920000Z | Received 1003.242 MB in 0.231 sec (4342.80 MB/s), memcpy was 0.26%
2019-03-11T21:06:39.157164000Z | Received 1002.876 MB in 0.238 sec (4207.55 MB/s), memcpy was 0.26%
2019-03-11T21:06:39.157862000Z | Received 1003.242 MB in 0.250 sec (4019.10 MB/s), memcpy was 0.27%
2019-03-11T21:06:39.158334000Z | Locked buffer 1 for writing
2019-03-11T21:06:39.158762000Z | Writing buffer 1 from CPU 13...
2019-03-11T21:06:39.159136000Z | Received 1002.876 MB in 0.360 sec (2783.40 MB/s), memcpy was 0.38%
2019-03-11T21:06:39.159556000Z | Received 1003.242 MB in 0.328 sec (3056.06 MB/s), memcpy was 0.42%
2019-03-11T21:06:39.159918000Z | Received 1002.876 MB in 0.338 sec (2967.43 MB/s), memcpy was 0.42%
2019-03-11T21:06:39.160294000Z | Received 1002.879 MB in 0.335 sec (2989.53 MB/s), memcpy was 0.42%
2019-03-11T21:06:39.160715000Z | Writing buffer 1 with 8 threads took 1.45 sec (10656.79 MB/s)
2019-03-11T21:06:39.161072000Z | Received 1003.240 MB in 0.584 sec (1717.56 MB/s), memcpy was 0.38%
2019-03-11T21:06:39.161469000Z | Received 1001.940 MB in 0.535 sec (1872.93 MB/s), memcpy was 0.38%
2019-03-11T21:06:39.161862000Z | Received 1000.320 MB in 0.520 sec (1922.01 MB/s), memcpy was 0.41%
2019-03-11T21:06:39.162234000Z | Received 1001.754 MB in 0.532 sec (1882.84 MB/s), memcpy was 0.39%
2019-03-11T21:06:39.162619000Z | Received 1000.506 MB in 0.524 sec (1909.73 MB/s), memcpy was 0.40%
2019-03-11T21:06:39.163005000Z | Received 1003.549 MB in 0.597 sec (1682.29 MB/s), memcpy was 0.40%
2019-03-11T21:06:39.163383000Z | Received 1002.569 MB in 0.536 sec (1869.97 MB/s), memcpy was 0.39%
2019-03-11T21:06:39.163780000Z | Re-assigned buffer 1
2019-03-11T21:06:42.550894000Z | Received 1002.878 MB in 0.343 sec (2927.51 MB/s), memcpy was 0.40%
2019-03-11T21:06:42.551557000Z | Received 1003.240 MB in 0.213 sec (4721.10 MB/s), memcpy was 0.23%
2019-03-11T21:06:42.551996000Z | Received 1002.876 MB in 0.208 sec (4824.79 MB/s), memcpy was 0.23%
2019-03-11T21:06:42.552399000Z | Received 1003.242 MB in 0.216 sec (4634.84 MB/s), memcpy was 0.22%
2019-03-11T21:06:42.552796000Z | Received 1002.876 MB in 0.225 sec (4462.76 MB/s), memcpy was 0.22%
2019-03-11T21:06:42.553173000Z | Locked buffer 0 for writing
2019-03-11T21:06:42.553561000Z | Writing buffer 0 from CPU 17...
2019-03-11T21:06:42.553967000Z | Received 1003.242 MB in 0.200 sec (5019.64 MB/s), memcpy was 0.24%
2019-03-11T21:06:42.554362000Z | Received 1002.876 MB in 0.220 sec (4551.78 MB/s), memcpy was 0.23%
2019-03-11T21:06:42.554766000Z | Received 1003.242 MB in 0.220 sec (4558.93 MB/s), memcpy was 0.24%
2019-03-11T21:06:42.555166000Z | Received 1002.876 MB in 0.225 sec (4466.51 MB/s), memcpy was 0.24%
2019-03-11T21:06:42.555547000Z | Received 1003.242 MB in 0.225 sec (4459.75 MB/s), memcpy was 0.25%
2019-03-11T21:06:42.555922000Z | Received 1002.876 MB in 0.230 sec (4359.28 MB/s), memcpy was 0.24%
2019-03-11T21:06:42.556292000Z | Received 1003.242 MB in 0.218 sec (4599.43 MB/s), memcpy was 0.24%
2019-03-11T21:06:42.556649000Z | Writing buffer 0 with 8 threads took 1.40 sec (10985.94 MB/s)
2019-03-11T21:06:42.557085000Z | Received 1002.143 MB in 0.303 sec (3305.80 MB/s), memcpy was 0.17%
2019-03-11T21:06:42.557457000Z | Received 1001.268 MB in 0.328 sec (3053.86 MB/s), memcpy was 0.16%
2019-03-11T21:06:47.052776000Z | Received 1000.536 MB in 0.363 sec (2756.69 MB/s), memcpy was 0.14%
2019-03-11T21:06:47.053592000Z | Received 1000.011 MB in 0.328 sec (3045.04 MB/s), memcpy was 0.16%
2019-03-11T21:06:47.054106000Z | Re-assigned buffer 0
2019-03-11T21:06:47.054506000Z | Received 1000.641 MB in 0.362 sec (2762.30 MB/s), memcpy was 0.16%
2019-03-11T21:06:47.054889000Z | Received 1000.275 MB in 0.332 sec (3016.50 MB/s), memcpy was 0.17%
2019-03-11T21:06:47.055309000Z | Received 1000.136 MB in 0.358 sec (2797.52 MB/s), memcpy was 0.15%
2019-03-11T21:06:47.055710000Z | Locked buffer 1 for writing
2019-03-11T21:06:47.056078000Z | Writing buffer 1 from CPU 17...
2019-03-11T21:06:47.056488000Z | Received 1000.220 MB in 0.336 sec (2974.95 MB/s), memcpy was 0.16%
2019-03-11T21:06:47.056852000Z | Received 1000.298 MB in 0.354 sec (2827.71 MB/s), memcpy was 0.15%
2019-03-11T21:06:47.057223000Z | Received 1000.435 MB in 0.344 sec (2904.95 MB/s), memcpy was 0.15%
2019-03-11T21:06:47.057631000Z | Received 1001.137 MB in 0.346 sec (2893.20 MB/s), memcpy was 0.15%
2019-03-11T21:06:47.057981000Z | Writing buffer 1 with 8 threads took 1.39 sec (11078.70 MB/s)
2019-03-11T21:06:47.058343000Z | Received 1000.441 MB in 0.350 sec (2855.60 MB/s), memcpy was 0.14%
2019-03-11T21:06:47.058877000Z | Received 1000.908 MB in 0.340 sec (2945.83 MB/s), memcpy was 0.15%
2019-03-11T21:06:47.059219000Z | Received 1001.016 MB in 0.354 sec (2827.98 MB/s), memcpy was 0.14%
2019-03-11T21:06:47.059621000Z | Received 1001.476 MB in 0.336 sec (2977.56 MB/s), memcpy was 0.14%
2019-03-11T21:06:51.527551000Z | Received 1000.006 MB in 0.361 sec (2768.15 MB/s), memcpy was 0.14%
2019-03-11T21:06:51.528256000Z | Received 1000.387 MB in 0.330 sec (3030.99 MB/s), memcpy was 0.15%
2019-03-11T21:06:51.528702000Z | Received 1000.398 MB in 0.363 sec (2752.34 MB/s), memcpy was 0.14%
2019-03-11T21:06:51.529097000Z | Received 1000.593 MB in 0.328 sec (3050.51 MB/s), memcpy was 0.15%
2019-03-11T21:06:51.529554000Z | Re-assigned buffer 1
2019-03-11T21:06:51.529950000Z | Received 1001.643 MB in 0.368 sec (2718.92 MB/s), memcpy was 0.22%
2019-03-11T21:06:51.530314000Z | Received 1001.715 MB in 0.332 sec (3012.88 MB/s), memcpy was 0.41%
2019-03-11T21:06:51.530763000Z | Received 1001.581 MB in 0.354 sec (2832.84 MB/s), memcpy was 0.37%
2019-03-11T21:06:51.531184000Z | Locked buffer 0 for writing
2019-03-11T21:06:51.531591000Z | Writing buffer 0 from CPU 17...
2019-03-11T21:06:51.531976000Z | Received 1000.929 MB in 0.328 sec (3054.00 MB/s), memcpy was 0.40%
2019-03-11T21:06:51.532355000Z | Received 1001.063 MB in 0.362 sec (2764.17 MB/s), memcpy was 0.39%
2019-03-11T21:06:51.532748000Z | Received 1001.241 MB in 0.337 sec (2968.15 MB/s), memcpy was 0.42%
2019-03-11T21:06:51.533128000Z | Received 1000.643 MB in 0.356 sec (2808.47 MB/s), memcpy was 0.35%
2019-03-11T21:06:51.533533000Z | Received 1001.384 MB in 0.325 sec (3085.36 MB/s), memcpy was 0.40%
2019-03-11T21:06:51.533892000Z | Writing buffer 0 with 8 threads took 1.55 sec (9926.91 MB/s)
2019-03-11T21:06:51.534262000Z | Received 1000.429 MB in 0.362 sec (2761.88 MB/s), memcpy was 0.24%
2019-03-11T21:06:56.331618000Z | Received 1001.342 MB in 0.328 sec (3050.07 MB/s), memcpy was 0.22%
2019-03-11T21:06:56.332302000Z | Received 1000.283 MB in 0.362 sec (2761.06 MB/s), memcpy was 0.18%
2019-03-11T21:06:56.332748000Z | Received 1001.501 MB in 0.333 sec (3010.73 MB/s), memcpy was 0.16%
2019-03-11T21:06:56.333146000Z | Received 1001.589 MB in 0.359 sec (2791.19 MB/s), memcpy was 0.15%
2019-03-11T21:06:56.333558000Z | Received 1001.127 MB in 0.335 sec (2992.07 MB/s), memcpy was 0.16%
2019-03-11T21:06:56.333996000Z | Received 1001.061 MB in 0.356 sec (2813.84 MB/s), memcpy was 0.16%
2019-03-11T21:06:56.334359000Z | Re-assigned buffer 0
2019-03-11T21:06:56.334735000Z | Received 1000.461 MB in 0.338 sec (2959.01 MB/s), memcpy was 0.15%
2019-03-11T21:06:56.335067000Z | Received 1000.861 MB in 0.352 sec (2843.56 MB/s), memcpy was 0.15%
2019-03-11T21:06:56.335431000Z | Received 1000.162 MB in 0.348 sec (2870.93 MB/s), memcpy was 0.16%
2019-03-11T21:06:56.335786000Z | Received 1000.615 MB in 0.342 sec (2927.56 MB/s), memcpy was 0.16%
2019-03-11T21:06:56.336174000Z | Locked buffer 1 for writing
2019-03-11T21:06:56.336590000Z | Writing buffer 1 from CPU 17...
2019-03-11T21:06:56.336915000Z | Received 1000.640 MB in 0.351 sec (2854.69 MB/s), memcpy was 0.17%
2019-03-11T21:06:56.337295000Z | Received 1003.156 MB in 0.344 sec (2919.89 MB/s), memcpy was 0.17%
2019-03-11T21:06:56.337649000Z | Received 1000.723 MB in 0.348 sec (2875.13 MB/s), memcpy was 0.18%
2019-03-11T21:06:56.337904000Z | Received 1003.091 MB in 0.341 sec (2942.70 MB/s), memcpy was 0.18%
2019-03-11T21:07:00.866734000Z | Writing buffer 1 with 8 threads took 1.62 sec (9554.12 MB/s)
2019-03-11T21:07:00.867306000Z | Received 1000.117 MB in 0.357 sec (2799.06 MB/s), memcpy was 0.17%
2019-03-11T21:07:00.867639000Z | Received 1001.017 MB in 0.330 sec (3032.78 MB/s), memcpy was 0.16%
2019-03-11T21:07:00.867965000Z | Received 1000.241 MB in 0.361 sec (2771.81 MB/s), memcpy was 0.14%
2019-03-11T21:07:00.868162000Z | Received 1000.616 MB in 0.328 sec (3054.23 MB/s), memcpy was 0.15%
2019-03-11T21:07:00.868348000Z | Received 1000.661 MB in 0.362 sec (2763.35 MB/s), memcpy was 0.14%
2019-03-11T21:07:00.868540000Z | Received 1000.339 MB in 0.327 sec (3054.48 MB/s), memcpy was 0.15%
2019-03-11T21:07:00.868708000Z | Received 1000.545 MB in 0.363 sec (2755.88 MB/s), memcpy was 0.13%
2019-03-11T21:07:00.868921000Z | Received 1001.509 MB in 0.328 sec (3050.76 MB/s), memcpy was 0.15%
2019-03-11T21:07:00.869120000Z | Re-assigned buffer 1
2019-03-11T21:07:00.869292000Z | Received 1000.321 MB in 0.363 sec (2755.54 MB/s), memcpy was 0.14%
2019-03-11T21:07:00.869496000Z | Received 1001.197 MB in 0.328 sec (3053.62 MB/s), memcpy was 0.15%
2019-03-11T21:07:00.869695000Z | Received 1000.696 MB in 0.364 sec (2751.78 MB/s), memcpy was 0.13%
2019-03-11T21:07:00.869877000Z | Locked buffer 0 for writing
2019-03-11T21:07:00.870070000Z | Writing buffer 0 from CPU 9...
2019-03-11T21:07:00.870241000Z | Received 1000.768 MB in 0.328 sec (3051.25 MB/s), memcpy was 0.16%
2019-03-11T21:07:00.870421000Z | Received 1000.491 MB in 0.363 sec (2756.00 MB/s), memcpy was 0.15%
2019-03-11T21:07:05.740394000Z | Received 1000.424 MB in 0.329 sec (3043.22 MB/s), memcpy was 0.16%
2019-03-11T21:07:05.741146000Z | Received 1000.665 MB in 0.363 sec (2759.06 MB/s), memcpy was 0.15%
2019-03-11T21:07:05.741419000Z | Received 1000.726 MB in 0.332 sec (3012.66 MB/s), memcpy was 0.16%
2019-03-11T21:07:05.741759000Z | Writing buffer 0 with 8 threads took 1.63 sec (9461.44 MB/s)
2019-03-11T21:07:05.741997000Z | Received 1000.372 MB in 0.360 sec (2779.25 MB/s), memcpy was 0.15%
2019-03-11T21:07:05.742257000Z | Received 1000.581 MB in 0.334 sec (2992.66 MB/s), memcpy was 0.16%
2019-03-11T21:07:05.742525000Z | Received 1001.313 MB in 0.358 sec (2795.94 MB/s), memcpy was 0.15%
2019-03-11T21:07:05.742787000Z | Received 1000.408 MB in 0.345 sec (2896.87 MB/s), memcpy was 0.16%
2019-03-11T21:07:05.743090000Z | Received 1001.253 MB in 0.346 sec (2893.36 MB/s), memcpy was 0.17%
2019-03-11T21:07:05.743330000Z | Received 1000.688 MB in 0.352 sec (2845.65 MB/s), memcpy was 0.16%
2019-03-11T21:07:05.743586000Z | Received 1000.384 MB in 0.339 sec (2947.69 MB/s), memcpy was 0.20%
2019-03-11T21:07:05.743852000Z | Re-assigned buffer 0
2019-03-11T21:07:05.744124000Z | Received 1000.667 MB in 0.351 sec (2850.82 MB/s), memcpy was 0.19%
2019-03-11T21:07:05.744387000Z | Received 1001.352 MB in 0.340 sec (2945.00 MB/s), memcpy was 0.16%
2019-03-11T21:07:05.744651000Z | Received 1000.403 MB in 0.351 sec (2850.47 MB/s), memcpy was 0.15%
2019-03-11T21:07:05.744937000Z | Received 1000.070 MB in 0.339 sec (2954.40 MB/s), memcpy was 0.16%
2019-03-11T21:07:05.745195000Z | Locked buffer 1 for writing
2019-03-11T21:07:05.745504000Z | Writing buffer 1 from CPU 9...
2019-03-11T21:07:10.584579000Z | Received 1000.911 MB in 0.363 sec (2756.18 MB/s), memcpy was 0.16%
2019-03-11T21:07:10.585111000Z | Received 1000.232 MB in 0.327 sec (3061.55 MB/s), memcpy was 0.16%
2019-03-11T21:07:10.585410000Z | Received 1000.577 MB in 0.362 sec (2761.25 MB/s), memcpy was 0.19%
2019-03-11T21:07:10.585675000Z | Received 1002.066 MB in 0.332 sec (3014.30 MB/s), memcpy was 0.31%
2019-03-11T21:07:10.585906000Z | Writing buffer 1 with 8 threads took 1.51 sec (10217.33 MB/s)
2019-03-11T21:07:10.586144000Z | Received 1000.446 MB in 0.360 sec (2781.04 MB/s), memcpy was 0.32%
2019-03-11T21:07:10.586403000Z | Received 1000.214 MB in 0.328 sec (3053.05 MB/s), memcpy was 0.40%
2019-03-11T21:07:10.586659000Z | Received 1001.750 MB in 0.364 sec (2755.36 MB/s), memcpy was 0.36%
2019-03-11T21:07:10.586909000Z | Received 1002.492 MB in 0.332 sec (3022.30 MB/s), memcpy was 0.41%
2019-03-11T21:07:10.587163000Z | Received 1000.920 MB in 0.368 sec (2720.80 MB/s), memcpy was 0.35%
2019-03-11T21:07:10.587389000Z | Received 1001.009 MB in 0.328 sec (3054.24 MB/s), memcpy was 0.41%
2019-03-11T21:07:10.587666000Z | Received 1002.947 MB in 0.364 sec (2757.04 MB/s), memcpy was 0.37%
2019-03-11T21:07:10.587923000Z | Received 1000.311 MB in 0.328 sec (3054.02 MB/s), memcpy was 0.40%
2019-03-11T21:07:10.588176000Z | Re-assigned buffer 1
2019-03-11T21:07:10.588413000Z | Received 1000.743 MB in 0.363 sec (2754.16 MB/s), memcpy was 0.21%
2019-03-11T21:07:10.588663000Z | Received 1000.403 MB in 0.330 sec (3029.54 MB/s), memcpy was 0.15%
2019-03-11T21:07:15.086870000Z | Received 1000.034 MB in 0.359 sec (2782.61 MB/s), memcpy was 0.14%
2019-03-11T21:07:15.087663000Z | Locked buffer 0 for writing
2019-03-11T21:07:15.088216000Z | Writing buffer 0 from CPU 17...
2019-03-11T21:07:15.088687000Z | Received 1000.142 MB in 0.334 sec (2991.03 MB/s), memcpy was 0.16%
2019-03-11T21:07:15.089105000Z | Received 1001.046 MB in 0.357 sec (2804.87 MB/s), memcpy was 0.15%
2019-03-11T21:07:15.089456000Z | Received 1000.340 MB in 0.339 sec (2949.41 MB/s), memcpy was 0.15%
2019-03-11T21:07:15.089855000Z | Received 1001.018 MB in 0.352 sec (2840.59 MB/s), memcpy was 0.15%
2019-03-11T21:07:15.090233000Z | Writing buffer 0 with 8 threads took 1.51 sec (10197.13 MB/s)
2019-03-11T21:07:15.090609000Z | Received 1000.083 MB in 0.348 sec (2877.44 MB/s), memcpy was 0.15%
2019-03-11T21:07:15.091010000Z | Received 1000.729 MB in 0.343 sec (2917.20 MB/s), memcpy was 0.16%
2019-03-11T21:07:15.091386000Z | Received 1000.166 MB in 0.351 sec (2852.54 MB/s), memcpy was 0.15%
2019-03-11T21:07:15.091723000Z | Received 1000.540 MB in 0.340 sec (2942.05 MB/s), memcpy was 0.16%
2019-03-11T21:07:15.092096000Z | Received 1001.265 MB in 0.351 sec (2848.80 MB/s), memcpy was 0.15%
2019-03-11T21:07:15.092462000Z | Received 1000.360 MB in 0.340 sec (2944.06 MB/s), memcpy was 0.15%
2019-03-11T21:07:15.092811000Z | Received 1000.243 MB in 0.352 sec (2844.77 MB/s), memcpy was 0.16%
2019-03-11T21:07:15.093174000Z | Received 1003.160 MB in 0.342 sec (2936.91 MB/s), memcpy was 0.16%
2019-03-11T21:07:15.093547000Z | Re-assigned buffer 0
2019-03-11T21:07:19.567211000Z | Received 1000.940 MB in 0.353 sec (2831.65 MB/s), memcpy was 0.16%
2019-03-11T21:07:19.568038000Z | Received 1000.703 MB in 0.335 sec (2986.41 MB/s), memcpy was 0.16%
2019-03-11T21:07:19.568471000Z | Received 1000.656 MB in 0.363 sec (2754.77 MB/s), memcpy was 0.15%
2019-03-11T21:07:19.568895000Z | Locked buffer 1 for writing
2019-03-11T21:07:19.569319000Z | Writing buffer 1 from CPU 17...
2019-03-11T21:07:19.569693000Z | Received 1000.058 MB in 0.327 sec (3061.78 MB/s), memcpy was 0.16%
2019-03-11T21:07:19.570106000Z | Received 1000.036 MB in 0.362 sec (2766.01 MB/s), memcpy was 0.16%
2019-03-11T21:07:19.570523000Z | Received 1000.643 MB in 0.328 sec (3054.00 MB/s), memcpy was 0.16%
2019-03-11T21:07:19.570904000Z | Received 1000.973 MB in 0.362 sec (2764.00 MB/s), memcpy was 0.14%
2019-03-11T21:07:19.571300000Z | Received 1000.679 MB in 0.328 sec (3053.55 MB/s), memcpy was 0.16%
2019-03-11T21:07:19.571713000Z | Writing buffer 1 with 8 threads took 1.56 sec (9897.60 MB/s)
2019-03-11T21:07:19.572030000Z | Received 1000.696 MB in 0.362 sec (2762.08 MB/s), memcpy was 0.14%
2019-03-11T21:07:19.572412000Z | Received 1000.607 MB in 0.328 sec (3052.09 MB/s), memcpy was 0.15%
2019-03-11T21:07:19.572775000Z | Received 1000.759 MB in 0.362 sec (2762.29 MB/s), memcpy was 0.14%
2019-03-11T21:07:19.573127000Z | Received 1000.475 MB in 0.328 sec (3048.48 MB/s), memcpy was 0.15%
2019-03-11T21:07:19.573475000Z | Received 1000.471 MB in 0.364 sec (2751.13 MB/s), memcpy was 0.13%
2019-03-11T21:07:24.761899000Z | Received 1000.381 MB in 0.332 sec (3014.51 MB/s), memcpy was 0.15%
2019-03-11T21:07:24.762837000Z | Received 1000.145 MB in 0.358 sec (2793.55 MB/s), memcpy was 0.14%
2019-03-11T21:07:24.763412000Z | Re-assigned buffer 1
2019-03-11T21:07:24.763913000Z | Received 1000.474 MB in 0.336 sec (2981.83 MB/s), memcpy was 0.15%
2019-03-11T21:07:24.764303000Z | Received 1000.437 MB in 0.354 sec (2823.62 MB/s), memcpy was 0.15%
2019-03-11T21:07:24.764713000Z | Received 1000.171 MB in 0.341 sec (2930.34 MB/s), memcpy was 0.15%
2019-03-11T21:07:24.765117000Z | Received 1000.043 MB in 0.349 sec (2867.22 MB/s), memcpy was 0.24%
2019-03-11T21:07:24.765472000Z | Locked buffer 0 for writing
2019-03-11T21:07:24.765844000Z | Writing buffer 0 from CPU 17...
2019-03-11T21:07:24.766268000Z | Received 1002.881 MB in 0.351 sec (2858.12 MB/s), memcpy was 0.30%
2019-03-11T21:07:24.766637000Z | Received 1000.790 MB in 0.340 sec (2941.39 MB/s), memcpy was 0.41%
2019-03-11T21:07:24.767042000Z | Received 1003.480 MB in 0.357 sec (2811.12 MB/s), memcpy was 0.41%
2019-03-11T21:07:24.767462000Z | Received 1001.093 MB in 0.367 sec (2725.87 MB/s), memcpy was 0.48%
2019-03-11T21:07:24.767921000Z | Writing buffer 0 with 8 threads took 1.53 sec (10066.00 MB/s)
<snip>
```
