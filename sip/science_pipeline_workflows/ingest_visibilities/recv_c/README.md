# Simple SPEAD UDP Receiver in C

## Performance Summary

This directory contains C code for a visibility receiver capable of receiving UDP-based SPEAD streams containing the item identifiers specified in the current version of the SDP-CSP interface control document.

The receiver has been tested using the 7-node Docker Swarm cluster on the P3-ALaSKA system, and is capable of sustainably receiving data at a rate of (at least) 2.9 GB/s (23.2 Gb/s) using the 25 GbE network. This test used 432 separate SPEAD streams to simulate the expected use case of 1-channel-per-stream, and to achieve this rate, it was necessary to use at least 4 receiver threads: A single-threaded receiver was capable of receiving only around 970 MB/s. This receiver works well on the 16-core-per-socket ALaSKA system using 4, 8 or 16 receiver threads, but using more than 4 threads does not seem to be advantageous. Average CPU usage with 4 threads was 10% (as reported on the Grafana dashboard), and with 16 threads was 13%.

With 432 streams and a buffer size of 10 samples per stream, the size of the in-memory buffer was 19.3 GB. Three buffers were used to accommodate out-of-order packets, and to allow for concurrent data receive and future data writes (not yet implemented): the Grafana dashboard showed there was 60.4 GB of memory in use on the receiver node.

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

## Testing

To run the test on P3-ALaSKA, it is sufficient to deploy the Compose file found in the parent directory.
*Before running the test, check that the IP address of the receiver node (all `destination_host` values) is still correct!* (It may need to be updated if the Swarm cluster has been rebuilt.)

The Docker image used for the receiver should be at least `skasip/vis_recv_c:1.1.9`.

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

## Sample Output

Screenshots of the Grafana dashboard panels are shown below. Node 1 was designated as the receiver node, while the other 6 nodes were used to send data.

![Sender node rate](https://drive.google.com/uc?id=10EIX-UxSq-536SOAJy99-dEjiM-q5TCh "")

![Receiver node rate](https://drive.google.com/uc?id=1vOqTaQP-46e-p-3YQB0ybZQAK9DSOLgF "")

![CPU and memory usage](https://drive.google.com/uc?id=1tyA4fQriveDQPZ326lMp1WY54t5bcqHl "")

Some sample output from `docker service logs i_recv` is shown below:

```
2019-02-14T15:19:06.847775000Z | Running RECV_VERSION 1.1.9
2019-02-14T15:19:20.858923000Z |  + Number of SPEAD streams    : 432
2019-02-14T15:19:20.859342000Z |  + Number of receiver threads : 4
2019-02-14T15:19:20.859696000Z |  + Number of times in buffer  : 10
2019-02-14T15:19:20.859999000Z |  + Number of buffers          : 3
2019-02-14T15:19:20.860311000Z |  + UDP port range             : 41000-41431
2019-02-14T15:19:20.860630000Z | Received 0.000 MB in 1.000 sec (0.00 MB/s), memcpy was 0.00%
<snip>
2019-02-14T15:19:32.700002000Z | Allocating 19289.457 MB buffer.
2019-02-14T15:19:32.700373000Z | Created buffer 0
2019-02-14T15:19:32.700726000Z | Received 1000.526 MB in 0.771 sec (1298.17 MB/s), memcpy was 0.21%
2019-02-14T15:19:32.701107000Z | Received 1002.841 MB in 0.357 sec (2811.13 MB/s), memcpy was 0.45%
2019-02-14T15:19:32.701495000Z | Received 1002.267 MB in 0.346 sec (2898.43 MB/s), memcpy was 0.46%
2019-02-14T15:19:32.701857000Z | Received 1000.357 MB in 0.348 sec (2876.10 MB/s), memcpy was 0.46%
2019-02-14T15:19:32.702272000Z | Received 1001.876 MB in 0.327 sec (3067.78 MB/s), memcpy was 0.47%
2019-02-14T15:19:32.702620000Z | Received 1001.876 MB in 0.361 sec (2777.56 MB/s), memcpy was 0.43%
2019-02-14T15:19:37.532778000Z | Received 1001.250 MB in 0.328 sec (3054.42 MB/s), memcpy was 0.47%
2019-02-14T15:19:37.533521000Z | Received 1001.563 MB in 0.363 sec (2759.04 MB/s), memcpy was 0.42%
2019-02-14T15:19:37.533937000Z | Received 1001.018 MB in 0.328 sec (3053.49 MB/s), memcpy was 0.47%
2019-02-14T15:19:37.534339000Z | Received 1002.197 MB in 0.369 sec (2718.58 MB/s), memcpy was 0.40%
2019-02-14T15:19:37.534743000Z | Received 1002.831 MB in 0.324 sec (3099.19 MB/s), memcpy was 0.45%
2019-02-14T15:19:37.535113000Z | Received 1000.688 MB in 0.362 sec (2764.96 MB/s), memcpy was 0.39%
2019-02-14T15:19:37.535501000Z | Received 1001.179 MB in 0.328 sec (3054.20 MB/s), memcpy was 0.43%
2019-02-14T15:19:37.535867000Z | Received 1000.205 MB in 0.362 sec (2760.87 MB/s), memcpy was 0.39%
2019-02-14T15:19:37.536253000Z | Received 1001.563 MB in 0.328 sec (3053.94 MB/s), memcpy was 0.43%
2019-02-14T15:19:37.536620000Z | Received 1000.491 MB in 0.363 sec (2758.35 MB/s), memcpy was 0.39%
2019-02-14T15:19:37.537009000Z | Received 1001.500 MB in 0.328 sec (3054.32 MB/s), memcpy was 0.43%
2019-02-14T15:19:37.537375000Z | Received 1000.295 MB in 0.363 sec (2757.40 MB/s), memcpy was 0.39%
2019-02-14T15:19:37.537744000Z | Received 1001.197 MB in 0.328 sec (3051.68 MB/s), memcpy was 0.43%
2019-02-14T15:19:37.538125000Z | Allocating 19289.457 MB buffer.
2019-02-14T15:19:37.538450000Z | Created buffer 1
2019-02-14T15:19:37.538806000Z | Received 1001.438 MB in 0.364 sec (2751.01 MB/s), memcpy was 0.39%
2019-02-14T15:19:43.098088000Z | Received 1001.733 MB in 0.328 sec (3053.28 MB/s), memcpy was 0.44%
2019-02-14T15:19:43.098911000Z | Received 1000.929 MB in 0.366 sec (2736.83 MB/s), memcpy was 0.42%
2019-02-14T15:19:43.099369000Z | Received 1000.079 MB in 0.327 sec (3056.72 MB/s), memcpy was 0.46%
2019-02-14T15:19:43.099737000Z | Received 1000.421 MB in 0.363 sec (2753.69 MB/s), memcpy was 0.42%
2019-02-14T15:19:43.100158000Z | Received 1000.029 MB in 0.332 sec (3008.53 MB/s), memcpy was 0.46%
2019-02-14T15:19:43.100588000Z | Received 1001.007 MB in 0.361 sec (2774.89 MB/s), memcpy was 0.43%
2019-02-14T15:19:43.100958000Z | Received 1000.323 MB in 0.347 sec (2884.38 MB/s), memcpy was 0.45%
2019-02-14T15:19:43.101406000Z | Received 1000.739 MB in 0.342 sec (2927.47 MB/s), memcpy was 0.46%
2019-02-14T15:19:43.101781000Z | Received 1002.095 MB in 0.361 sec (2773.32 MB/s), memcpy was 0.43%
2019-02-14T15:19:43.102160000Z | Received 1001.272 MB in 0.326 sec (3068.38 MB/s), memcpy was 0.47%
2019-02-14T15:19:43.102600000Z | Received 1000.554 MB in 0.363 sec (2754.30 MB/s), memcpy was 0.43%
2019-02-14T15:19:43.102921000Z | Received 1000.777 MB in 0.328 sec (3053.64 MB/s), memcpy was 0.47%
2019-02-14T15:19:43.103282000Z | Received 1003.841 MB in 0.364 sec (2755.73 MB/s), memcpy was 0.43%
2019-02-14T15:19:43.103604000Z | Received 1003.064 MB in 0.331 sec (3033.78 MB/s), memcpy was 0.47%
2019-02-14T15:19:43.103940000Z | Received 1000.786 MB in 0.360 sec (2777.37 MB/s), memcpy was 0.42%
2019-02-14T15:19:43.104296000Z | Received 1003.233 MB in 0.330 sec (3040.92 MB/s), memcpy was 0.46%
2019-02-14T15:19:47.940670000Z | Received 1001.634 MB in 0.363 sec (2756.56 MB/s), memcpy was 0.42%
2019-02-14T15:19:47.941429000Z | Received 1000.607 MB in 0.336 sec (2974.07 MB/s), memcpy was 0.45%
2019-02-14T15:19:47.941837000Z | Allocating 19289.457 MB buffer.
2019-02-14T15:19:47.942260000Z | Created buffer 2
2019-02-14T15:19:47.942660000Z | Received 1003.215 MB in 0.362 sec (2770.67 MB/s), memcpy was 0.45%
2019-02-14T15:19:47.943038000Z | Received 1001.233 MB in 0.321 sec (3123.57 MB/s), memcpy was 0.49%
2019-02-14T15:19:47.943440000Z | Received 1003.099 MB in 0.373 sec (2692.13 MB/s), memcpy was 0.44%
2019-02-14T15:19:47.943803000Z | Received 1003.242 MB in 0.348 sec (2880.68 MB/s), memcpy was 0.48%
2019-02-14T15:19:47.944141000Z | Received 1002.876 MB in 0.342 sec (2931.56 MB/s), memcpy was 0.48%
2019-02-14T15:19:47.944497000Z | Received 1002.197 MB in 0.321 sec (3122.50 MB/s), memcpy was 0.49%
2019-02-14T15:19:47.944874000Z | Received 1000.143 MB in 0.368 sec (2715.80 MB/s), memcpy was 0.44%
2019-02-14T15:19:47.945286000Z | Received 1003.814 MB in 0.325 sec (3087.31 MB/s), memcpy was 0.48%
2019-02-14T15:19:47.945646000Z | Received 1003.394 MB in 0.365 sec (2745.96 MB/s), memcpy was 0.43%
2019-02-14T15:19:47.946044000Z | Received 1000.939 MB in 0.324 sec (3084.65 MB/s), memcpy was 0.47%
2019-02-14T15:19:47.946424000Z | Received 1001.249 MB in 0.374 sec (2677.61 MB/s), memcpy was 0.42%
2019-02-14T15:19:47.946782000Z | Received 1000.221 MB in 0.321 sec (3119.68 MB/s), memcpy was 0.48%
2019-02-14T15:19:53.142761000Z | Received 1000.234 MB in 0.361 sec (2768.36 MB/s), memcpy was 0.42%
2019-02-14T15:19:53.143435000Z | Received 1001.750 MB in 0.344 sec (2915.39 MB/s), memcpy was 0.45%
2019-02-14T15:19:53.143823000Z | Received 1001.341 MB in 0.349 sec (2872.97 MB/s), memcpy was 0.44%
2019-02-14T15:19:53.144126000Z | Received 1000.168 MB in 0.358 sec (2793.20 MB/s), memcpy was 0.43%
2019-02-14T15:19:53.144482000Z | Received 1001.868 MB in 0.333 sec (3005.06 MB/s), memcpy was 0.44%
2019-02-14T15:19:53.145018000Z | Received 1002.190 MB in 0.363 sec (2759.53 MB/s), memcpy was 0.41%
2019-02-14T15:19:53.145666000Z | Received 1001.463 MB in 0.328 sec (3054.67 MB/s), memcpy was 0.46%
2019-02-14T15:19:53.146090000Z | Re-assigned buffer 0
2019-02-14T15:19:53.146540000Z | Received 1000.134 MB in 0.362 sec (2759.83 MB/s), memcpy was 0.34%
2019-02-14T15:19:53.146892000Z | Received 1000.107 MB in 0.327 sec (3053.81 MB/s), memcpy was 0.15%
2019-02-14T15:19:53.147315000Z | Received 1000.134 MB in 0.363 sec (2755.69 MB/s), memcpy was 0.13%
2019-02-14T15:19:53.147727000Z | Received 1000.420 MB in 0.328 sec (3053.09 MB/s), memcpy was 0.15%
2019-02-14T15:19:53.148156000Z | Received 1000.518 MB in 0.363 sec (2752.82 MB/s), memcpy was 0.14%
2019-02-14T15:19:53.148631000Z | Received 1000.464 MB in 0.328 sec (3052.49 MB/s), memcpy was 0.16%
2019-02-14T15:19:53.149091000Z | Received 1000.563 MB in 0.364 sec (2751.74 MB/s), memcpy was 0.15%
2019-02-14T15:19:53.149521000Z | Received 1000.196 MB in 0.328 sec (3053.48 MB/s), memcpy was 0.15%
2019-02-14T15:19:58.334839000Z | Received 1000.259 MB in 0.364 sec (2744.53 MB/s), memcpy was 0.14%
2019-02-14T15:19:58.335475000Z | Received 1000.688 MB in 0.328 sec (3054.58 MB/s), memcpy was 0.15%
2019-02-14T15:19:58.335882000Z | Received 1000.330 MB in 0.363 sec (2757.01 MB/s), memcpy was 0.13%
2019-02-14T15:19:58.336274000Z | Received 1000.893 MB in 0.328 sec (3053.53 MB/s), memcpy was 0.15%
2019-02-14T15:19:58.336590000Z | Received 1000.071 MB in 0.363 sec (2752.11 MB/s), memcpy was 0.14%
2019-02-14T15:19:58.336983000Z | Received 1000.107 MB in 0.327 sec (3056.48 MB/s), memcpy was 0.16%
2019-02-14T15:19:58.337371000Z | Received 1000.893 MB in 0.363 sec (2756.90 MB/s), memcpy was 0.14%
2019-02-14T15:19:58.337695000Z | Received 1000.509 MB in 0.327 sec (3055.38 MB/s), memcpy was 0.16%
2019-02-14T15:19:58.337992000Z | Received 1000.545 MB in 0.363 sec (2755.92 MB/s), memcpy was 0.14%
2019-02-14T15:19:58.338406000Z | Received 1000.466 MB in 0.328 sec (3050.14 MB/s), memcpy was 0.16%
2019-02-14T15:19:58.338722000Z | Received 1002.026 MB in 0.362 sec (2764.61 MB/s), memcpy was 0.14%
2019-02-14T15:19:58.339036000Z | Re-assigned buffer 1
2019-02-14T15:19:58.339427000Z | Received 1000.150 MB in 0.336 sec (2975.99 MB/s), memcpy was 0.14%
2019-02-14T15:19:58.339763000Z | Received 1001.243 MB in 0.355 sec (2823.46 MB/s), memcpy was 0.14%
2019-02-14T15:19:58.340082000Z | Received 1000.209 MB in 0.346 sec (2889.55 MB/s), memcpy was 0.15%
2019-02-14T15:19:58.340435000Z | Received 1000.515 MB in 0.345 sec (2901.35 MB/s), memcpy was 0.16%
2019-02-14T15:20:03.577649000Z | Received 1000.221 MB in 0.357 sec (2800.62 MB/s), memcpy was 0.16%
2019-02-14T15:20:03.578334000Z | Received 1000.717 MB in 0.333 sec (3001.39 MB/s), memcpy was 0.15%
2019-02-14T15:20:03.578766000Z | Received 1000.643 MB in 0.362 sec (2760.41 MB/s), memcpy was 0.13%
2019-02-14T15:20:03.579122000Z | Received 1000.036 MB in 0.328 sec (3051.33 MB/s), memcpy was 0.15%
2019-02-14T15:20:03.579471000Z | Received 1000.661 MB in 0.363 sec (2758.15 MB/s), memcpy was 0.13%
2019-02-14T15:20:03.579839000Z | Received 1000.965 MB in 0.328 sec (3051.90 MB/s), memcpy was 0.14%
2019-02-14T15:20:03.580168000Z | Received 1001.206 MB in 0.363 sec (2761.06 MB/s), memcpy was 0.13%
2019-02-14T15:20:03.580503000Z | Received 1000.581 MB in 0.328 sec (3055.13 MB/s), memcpy was 0.15%
2019-02-14T15:20:03.580815000Z | Received 1000.152 MB in 0.363 sec (2756.39 MB/s), memcpy was 0.14%
2019-02-14T15:20:03.581142000Z | Received 1000.241 MB in 0.327 sec (3054.52 MB/s), memcpy was 0.16%
2019-02-14T15:20:03.581527000Z | Received 1001.402 MB in 0.364 sec (2752.41 MB/s), memcpy was 0.15%
2019-02-14T15:20:03.581869000Z | Received 1000.187 MB in 0.327 sec (3055.81 MB/s), memcpy was 0.16%
2019-02-14T15:20:03.582259000Z | Received 1000.518 MB in 0.363 sec (2756.58 MB/s), memcpy was 0.14%
2019-02-14T15:20:03.582671000Z | Received 1000.670 MB in 0.328 sec (3054.25 MB/s), memcpy was 0.14%
2019-02-14T15:20:03.583031000Z | Received 1000.741 MB in 0.363 sec (2753.54 MB/s), memcpy was 0.13%
2019-02-14T15:20:03.583409000Z | Received 1000.196 MB in 0.327 sec (3054.17 MB/s), memcpy was 0.14%
2019-02-14T15:20:09.073517000Z | Re-assigned buffer 2
2019-02-14T15:20:09.074279000Z | Received 1000.446 MB in 0.363 sec (2753.02 MB/s), memcpy was 0.13%
2019-02-14T15:20:09.074698000Z | Received 1000.098 MB in 0.328 sec (3053.18 MB/s), memcpy was 0.15%
2019-02-14T15:20:09.075054000Z | Received 1000.938 MB in 0.363 sec (2758.95 MB/s), memcpy was 0.13%
2019-02-14T15:20:09.075482000Z | Received 1000.104 MB in 0.327 sec (3055.05 MB/s), memcpy was 0.15%
2019-02-14T15:20:09.075841000Z | Received 1000.280 MB in 0.363 sec (2751.91 MB/s), memcpy was 0.13%
2019-02-14T15:20:09.076233000Z | Received 1000.253 MB in 0.331 sec (3023.31 MB/s), memcpy was 0.15%
2019-02-14T15:20:09.076594000Z | Received 1000.631 MB in 0.360 sec (2776.25 MB/s), memcpy was 0.13%
2019-02-14T15:20:09.076912000Z | Received 1000.163 MB in 0.339 sec (2951.61 MB/s), memcpy was 0.14%
2019-02-14T15:20:09.077291000Z | Received 1000.069 MB in 0.351 sec (2848.52 MB/s), memcpy was 0.14%
2019-02-14T15:20:09.077623000Z | Received 1000.113 MB in 0.346 sec (2889.20 MB/s), memcpy was 0.14%
2019-02-14T15:20:09.077977000Z | Received 1000.468 MB in 0.344 sec (2908.16 MB/s), memcpy was 0.14%
2019-02-14T15:20:09.078316000Z | Received 1000.177 MB in 0.355 sec (2815.44 MB/s), memcpy was 0.14%
2019-02-14T15:20:09.078669000Z | Received 1000.180 MB in 0.335 sec (2985.31 MB/s), memcpy was 0.15%
2019-02-14T15:20:09.078988000Z | Received 1000.829 MB in 0.362 sec (2763.76 MB/s), memcpy was 0.14%
2019-02-14T15:20:09.079354000Z | Received 1000.422 MB in 0.330 sec (3029.97 MB/s), memcpy was 0.16%
2019-02-14T15:20:14.231692000Z | Received 1000.460 MB in 0.372 sec (2689.23 MB/s), memcpy was 0.15%
2019-02-14T15:20:14.232650000Z | Received 1000.174 MB in 0.328 sec (3052.74 MB/s), memcpy was 0.14%
2019-02-14T15:20:14.233156000Z | Received 1000.411 MB in 0.363 sec (2757.18 MB/s), memcpy was 0.12%
2019-02-14T15:20:14.233703000Z | Received 1000.009 MB in 0.328 sec (3053.43 MB/s), memcpy was 0.14%
2019-02-14T15:20:14.234179000Z | Re-assigned buffer 0
2019-02-14T15:20:14.234574000Z | Received 1000.446 MB in 0.363 sec (2759.81 MB/s), memcpy was 0.13%
2019-02-14T15:20:14.234992000Z | Received 1000.054 MB in 0.327 sec (3053.65 MB/s), memcpy was 0.15%
<snip>
```
