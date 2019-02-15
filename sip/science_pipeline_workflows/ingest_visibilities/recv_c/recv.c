#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <sys/time.h>
#include <sys/types.h>
#include <fcntl.h>
#include <inttypes.h>
#include <netinet/in.h>
#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>
#ifdef __APPLE__
#  include <libkern/OSByteOrder.h>
#  define be32toh(x) OSSwapBigToHostInt32(x)
#  define be64toh(x) OSSwapBigToHostInt64(x)
#else
#  define _BSD_SOURCE
#  include <endian.h>
#endif

/*
 * Compile with:
 * gcc -O3 -Wall -Wextra -pthread -o recv recv.c
 */

#define RECV_VERSION "1.1.9"

typedef unsigned char uchar;
struct Timer;
struct Buffer;
struct Stream;
struct Receiver;

typedef struct float2 { float x, y; } float2;

/*
 * NOTE - This is a really bad idea if we want decent performance!
 * We should try to change the ICD so that this struct can be padded naturally.
 * Without this hack, sizeof(struct DataType) will be 36 instead of 34,
 * which will definitely break things -- but vis[] is not currently
 * aligned to a 4-byte address, so that may also break things...
 */
#pragma pack(push)
#pragma pack(1)     /* set alignment to 1 byte boundary */

struct DataType
{
    int8_t tci;
    uint8_t fd;
    float2 vis[4]; /* num_pols */
};

#pragma pack(pop)

struct Timer
{
    double start, elapsed;
    int paused;
};

struct ThreadBarrier
{
    pthread_cond_t cond;
    pthread_mutex_t lock;
    unsigned int num_threads, count, iter;
};

struct Buffer
{
    /* From slowest to fastest varying, dimension order is
     * (time, channel, baseline) */
    struct DataType* vis_data;
    size_t buffer_size, block_size, byte_counter;
    int num_times, num_channels, num_baselines;
    int heap_id_start, heap_id_end;
};

struct Stream
{
    uchar* socket_buffer;
    struct Receiver* receiver;
    struct Timer *tmr_memcpy;
    size_t dump_byte_counter, recv_byte_counter, vis_data_heap_offset;
    int buffer_len, socket_handle, stream_id;
    int heap_count, done;
    unsigned short int port;
};

struct Receiver
{
    pthread_mutex_t lock;
    struct ThreadBarrier* barrier;
    struct Timer* tmr;
    struct Stream** streams;
    struct Buffer** buffers;
    int completed_streams;
    int num_baselines, num_times_in_buffer, max_num_buffers;
    int num_threads, num_streams, num_buffers;
    unsigned short int port_start;
};

void tmr_clear(struct Timer* h);
struct Timer* tmr_create(void);
double tmr_elapsed(struct Timer* h);
void tmr_free(struct Timer* h);
double tmr_get_wtime(void);
void tmr_pause(struct Timer* h);
void tmr_restart(struct Timer* h);
void tmr_resume(struct Timer* h);
void tmr_start(struct Timer* h);

struct Buffer* buffer_create(int num_times, int num_channels,
        int num_baselines);
void buffer_free(struct Buffer* h);

struct Stream* stream_create(unsigned short int port, int stream_id,
        struct Receiver* receiver);
void stream_decode(struct Stream* h, const unsigned char* buf, int depth);
void stream_free(struct Stream* h);
void stream_receive(struct Stream* h);

struct Buffer* receiver_buffer(struct Receiver* h, int heap, size_t length);
struct Receiver* receiver_create(int num_buffers, int num_times_in_buffer,
        int num_threads, int num_streams, unsigned short int port_start);
void receiver_free(struct Receiver* h);
void receiver_receive(struct Receiver* h);


void tmr_clear(struct Timer* h)
{
    h->paused = 1;
    h->start = h->elapsed = 0.0;
}

struct Timer* tmr_create(void)
{
    struct Timer* h = (struct Timer*) calloc(1, sizeof(struct Timer));
    tmr_clear(h);
    return h;
}

double tmr_elapsed(struct Timer* h)
{
    if (h->paused) return h->elapsed;
    const double now = tmr_get_wtime();
    h->elapsed += (now - h->start);
    h->start = now;
    return h->elapsed;
}

void tmr_free(struct Timer* h)
{
    free(h);
}

double tmr_get_wtime(void)
{
#if _POSIX_MONOTONIC_CLOCK > 0
    /* Use monotonic clock if available. */
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
#else
    /* Use gettimeofday() as fallback. */
    struct timeval tv;
    gettimeofday(&tv, 0);
    return tv.tv_sec + tv.tv_usec / 1e6;
#endif
}

void tmr_pause(struct Timer* h)
{
    if (h->paused) return;
    (void)tmr_elapsed(h);
    h->paused = 1;
}

void tmr_restart(struct Timer* h)
{
    h->paused = 0;
    h->start = tmr_get_wtime();
}

void tmr_resume(struct Timer* h)
{
    if (!h->paused) return;
    tmr_restart(h);
}

void tmr_start(struct Timer* h)
{
    h->elapsed = 0.0;
    tmr_restart(h);
}

struct ThreadBarrier* barrier_create(int num_threads)
{
    struct ThreadBarrier* barrier =
            (struct ThreadBarrier*) calloc(1, sizeof(struct ThreadBarrier));
    pthread_mutex_init(&barrier->lock, NULL);
    pthread_cond_init(&barrier->cond, NULL);
    barrier->num_threads = num_threads;
    barrier->count = num_threads;
    barrier->iter = 0;
    return barrier;
}

void barrier_free(struct ThreadBarrier* barrier)
{
    if (!barrier) return;
    pthread_mutex_destroy(&barrier->lock);
    pthread_cond_destroy(&barrier->cond);
    free(barrier);
}

int barrier_wait(struct ThreadBarrier* barrier)
{
    pthread_mutex_lock(&barrier->lock);
    const unsigned int i = barrier->iter;
    if (--(barrier->count) == 0)
    {
        (barrier->iter)++;
        barrier->count = barrier->num_threads;
        pthread_cond_broadcast(&barrier->cond);
        pthread_mutex_unlock(&barrier->lock);
        return 1;
    }
    do {
        pthread_cond_wait(&barrier->cond, &barrier->lock);
    } while (i == barrier->iter);
    pthread_mutex_unlock(&barrier->lock);
    return 0;
}

void buffer_clear(struct Buffer* h)
{
    const int num_times = h->num_times;
    const int num_channels = h->num_channels;
    const int num_baselines = h->num_baselines;
    for (int t = 0; t < num_times; ++t)
        for (int c = 0; c < num_channels; ++c)
            for (int b = 0; b < num_baselines; ++b)
                h->vis_data[num_baselines * (num_channels * t + c) + b].fd = 1;
}

struct Buffer* buffer_create(int num_times, int num_channels,
        int num_baselines)
{
    struct Buffer* h = (struct Buffer*) calloc(1, sizeof(struct Buffer));
    h->num_baselines = num_baselines;
    h->num_channels = num_channels;
    h->num_times = num_times;
    h->block_size = num_baselines * sizeof(struct DataType);
    h->buffer_size = h->block_size * num_channels * num_times;
    printf("Allocating %.3f MB buffer.\n", h->buffer_size * 1e-6);
    h->vis_data = (struct DataType*) malloc(h->buffer_size);
    if (!h->vis_data)
    {
        fprintf(stderr, "malloc failed: requested %zu bytes\n", h->buffer_size);
        exit(1);
    }
    // if (mlock(h->vis_data, h->buffer_size) == -1) perror("mlock failed");
    // memset(h->vis_data, 0, h->buffer_size);
    // buffer_clear(h);
    return h;
}

void buffer_free(struct Buffer* h)
{
    if (!h) return;
    free(h->vis_data);
    free(h);
}

struct Stream* stream_create(unsigned short int port, int stream_id,
        struct Receiver* receiver)
{
    struct Stream* h = (struct Stream*) calloc(1, sizeof(struct Stream));
    const int requested_buffer_len = 16*1024*1024;
    h->port = port;
    h->buffer_len = requested_buffer_len;
    h->stream_id = stream_id;
    if ((h->socket_handle = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        fprintf(stderr, "Cannot create socket.\n");
        return h;
    }
    fcntl(h->socket_handle, F_SETFL, O_NONBLOCK);
    setsockopt(h->socket_handle, SOL_SOCKET, SO_RCVBUF,
            &h->buffer_len, sizeof(int));
    uint32_t int_size = (uint32_t) sizeof(int);
    getsockopt(h->socket_handle, SOL_SOCKET, SO_RCVBUF,
            &h->buffer_len, &int_size);
    if (int_size != (uint32_t) sizeof(int))
    {
        fprintf(stderr, "Error at line %d\n", __LINE__);
        exit(1);
    }
    if ((h->buffer_len / 2) < requested_buffer_len)
    {
        printf("Requested socket buffer of %d bytes; actual size is %d bytes\n",
                requested_buffer_len, h->buffer_len / 2);
    }
    struct sockaddr_in myaddr;
    myaddr.sin_family = AF_INET;
    myaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    myaddr.sin_port = htons(port);
    if (bind(h->socket_handle, (struct sockaddr*)&myaddr, sizeof(myaddr)) < 0)
    {
        fprintf(stderr, "Bind failed.\n");
        return h;
    }
    h->socket_buffer = (uchar*) malloc(h->buffer_len);
    memset(h->socket_buffer, 0, h->buffer_len);
    h->receiver = receiver;
    h->tmr_memcpy = tmr_create();
    return h;
}

void stream_decode(struct Stream* h, const uchar* buf, int depth)
{
    /* Extract SPEAD packet headers. */
    const uchar magic = buf[0];
    const uchar version = buf[1];
    if (magic != 'S' || version != (uchar)4) return;
    const uchar item_id_bits = buf[2] * 8 - 1;
    const uchar heap_address_bits = buf[3] * 8;
    const uchar num_items = buf[7];

    /* Get pointers to items and payload start. */
    const uint64_t* items = (const uint64_t*) &buf[8];
    const uint64_t mask_addr = (1ull << heap_address_bits) - 1;
    const uint64_t mask_id   = (1ull << item_id_bits) - 1;
    const uchar* payload_start = (const uchar*) &items[num_items];

    /* Heap data. */
    int packet_has_header_data = 0, packet_has_stream_control = 0;
    uint32_t timestamp_count = 0, timestamp_fraction = 0;
    uint64_t scan_id = 0;
    size_t packet_payload_length = 0;
    size_t heap_offset = 0, heap_size = 0;
    size_t vis_data_start = 0;

    /* Iterate ItemPointers. */
    for (uchar i = 0; i < num_items; ++i)
    {
        const uint64_t item = be64toh(items[i]);
        /*const uint64_t immediate = item & (1ull << 63);*/
        const uint64_t item_addr = item & mask_addr;
        const uint64_t item_id   = (item >> heap_address_bits) & mask_id;
        switch (item_id)
        {
        case 0x0:
            /* NULL - ignore. */
            break;
        case 0x1:
            /* Heap counter (immediate addressing, big endian). */
            if (depth == 0) h->heap_count = (int) item_addr - 2;
            break;
        case 0x2:
            /* Heap size (immediate addressing, big endian). */
            heap_size = item_addr;
            break;
        case 0x3:
            /* Heap offset (immediate addressing, big endian). */
            heap_offset = (size_t) item_addr;
            break;
        case 0x4:
            /* Packet payload length (immediate addressing, big endian). */
            packet_payload_length = (size_t) item_addr;
            break;
        case 0x5:
            /* Nested item descriptor (recursive call). */
            /*stream_decode(h, &payload_start[item_addr], depth + 1);*/
            break;
        case 0x6:
            /* Stream control messages (immediate addressing, big endian). */
            packet_has_stream_control = 1;
            if (item_addr == 2) h->done = 1;
            break;
        case 0x10: /* Item descriptor name     (absolute addressing). */
        case 0x11: /* Item descriptor desc.    (absolute addressing). */
        case 0x12: /* Item descriptor shape    (absolute addressing). */
        case 0x13: /* Item descriptor type     (absolute addressing). */
        case 0x14: /* Item descriptor ID       (immediate addressing). */
        case 0x15: /* Item descriptor DataType (absolute addressing). */
            break;
        case 0x6000:
            /* Visibility timestamp count (immediate addressing). */
            timestamp_count = be32toh((uint32_t) item_addr);
            packet_has_header_data = 1;
            break;
        case 0x6001:
            /* Visibility timestamp fraction (immediate addressing). */
            timestamp_fraction = be32toh((uint32_t) item_addr);
            packet_has_header_data = 1;
            break;
        case 0x6005:
            /* Visibility baseline count (immediate addressing). */
            h->receiver->num_baselines = be32toh((uint32_t) item_addr);
            packet_has_header_data = 1;
            break;
        case 0x6008:
            /* Scan ID (absolute addressing). */
            scan_id = *( (uint64_t*)(payload_start + item_addr) );
            packet_has_header_data = 1;
            break;
        case 0x600A:
            /* Visibility data (absolute addressing). */
            h->vis_data_heap_offset = (size_t) item_addr;
            vis_data_start = (size_t) item_addr;
            break;
        default:
            /*printf("Heap %3d  ID: %#6llx, %s: %llu\n", h->heap_count, item_id,
                    immediate ? "VAL" : "ptr", item_addr);*/
            break;
        }
    }
    if (0 && !packet_has_stream_control)
        printf("==== Packet in heap %3d "
                "(heap offset %zu/%zu, payload length %zu)\n",
                h->heap_count, heap_offset, heap_size, packet_payload_length);
    if (0 && packet_has_header_data)
    {
        printf("     heap               : %d\n", h->heap_count);
        printf("     timestamp_count    : %" PRIu32 "\n", timestamp_count);
        printf("     timestamp_fraction : %" PRIu32 "\n", timestamp_fraction);
        printf("     scan_id            : %" PRIu64 "\n", scan_id);
        printf("     num_baselines      : %d\n", h->receiver->num_baselines);
    }
    if (!packet_has_stream_control &&
            h->vis_data_heap_offset > 0 && h->receiver->num_baselines > 0)
    {
        const size_t vis_data_length = packet_payload_length - vis_data_start;
        /*printf("Visibility data length: %zu bytes\n", vis_data_length);*/
        struct Buffer* buf = receiver_buffer(
                h->receiver, h->heap_count, vis_data_length);
        if (buf)
        {
            const uchar* src_addr = payload_start + vis_data_start;
            const int i_time = h->heap_count - buf->heap_id_start;
            const int i_chan = h->stream_id;
            uchar* dst_addr = ((uchar*) buf->vis_data) +
                    (heap_offset - h->vis_data_heap_offset + vis_data_start) +
                    buf->block_size * (i_time * buf->num_channels + i_chan);
            tmr_resume(h->tmr_memcpy);
            memcpy(dst_addr, src_addr, vis_data_length);
            tmr_pause(h->tmr_memcpy);
            h->recv_byte_counter += vis_data_length;
        }
        else
        {
            h->dump_byte_counter += vis_data_length;
        }
    }
}

void stream_free(struct Stream* h)
{
    if (!h) return;
    tmr_free(h->tmr_memcpy);
    close(h->socket_handle);
    free(h->socket_buffer);
    free(h);
}

void stream_receive(struct Stream* h)
{
    if (!h) return;
    const int recvlen = recv(h->socket_handle,
            h->socket_buffer, h->buffer_len, 0);
    if (recvlen >= 8)
        stream_decode(h, h->socket_buffer, 0);
}

struct Buffer* receiver_buffer(struct Receiver* h, int heap, size_t length)
{
    if (!h) return 0;
    struct Buffer* buf = 0;
    int oldest = 0, min_heap_start = 1 << 30;
    pthread_mutex_lock(&h->lock);
    for (int i = 0; i < h->num_buffers; ++i)
    {
        struct Buffer* buf_test = h->buffers[i];
        if (heap >= buf_test->heap_id_start && heap <= buf_test->heap_id_end)
        {
            buf_test->byte_counter += length;
            pthread_mutex_unlock(&h->lock);
            return buf_test;
        }
        if (buf_test->heap_id_start < min_heap_start)
        {
            min_heap_start = buf_test->heap_id_start;
            oldest = i;
        }
    }
    /* Heap does not belong in any active buffer. */
    if (h->num_buffers > 0 && heap < min_heap_start)
    {
        /* Dump data if it's too old. */
        pthread_mutex_unlock(&h->lock);
        return 0;
    }
    if (h->num_buffers < h->max_num_buffers)
    {
        /* Create a new buffer. */
        buf = buffer_create(h->num_times_in_buffer,
                h->num_streams, h->num_baselines);
        printf("Created buffer %d\n", h->num_buffers);
        h->num_buffers++;
        h->buffers = (struct Buffer**) realloc(h->buffers,
                h->num_buffers * sizeof(struct Buffer*));
        h->buffers[h->num_buffers - 1] = buf;
    }
    else
    {
        /* Re-purpose the oldest buffer. */
        buf = h->buffers[oldest];
        printf("Re-assigned buffer %d\n", oldest);
        if (buf->byte_counter > 0)
        {
            if (buf->byte_counter != buf->buffer_size)
                printf("WARNING: Incomplete buffer (%zu/%zu, %.1f%%)\n",
                        buf->byte_counter, buf->buffer_size,
                        100 * buf->byte_counter / (float)buf->buffer_size);
            buf->byte_counter = 0;
        }
        // memset(buf->vis_data, 0, buf->buffer_size);
        // buffer_clear(buf);
    }
    buf->byte_counter += length;
    buf->heap_id_start =
            h->num_times_in_buffer * (heap / h->num_times_in_buffer);
    buf->heap_id_end = buf->heap_id_start + h->num_times_in_buffer - 1;
    pthread_mutex_unlock(&h->lock);
    return buf;
}

struct Receiver* receiver_create(int num_buffers, int num_times_in_buffer,
        int num_threads, int num_streams, unsigned short int port_start)
{
    struct Receiver* h = (struct Receiver*) calloc(1, sizeof(struct Receiver));
    pthread_mutex_init(&h->lock, NULL);
    h->tmr = tmr_create();
    h->barrier = barrier_create(num_threads);
    h->max_num_buffers = num_buffers;
    h->num_times_in_buffer = num_times_in_buffer;
    h->num_threads = num_threads;
    h->num_streams = num_streams;
    h->port_start = port_start;
    h->streams = (struct Stream**) calloc(num_streams, sizeof(struct Stream*));
    for (int i = 0; i < num_streams; ++i)
        h->streams[i] = stream_create(port_start + (unsigned short int)i, i, h);
    return h;
}

void receiver_free(struct Receiver* h)
{
    if (!h) return;
    tmr_free(h->tmr);
    barrier_free(h->barrier);
    for (int i = 0; i < h->num_streams; ++i) stream_free(h->streams[i]);
    for (int i = 0; i < h->num_buffers; ++i) buffer_free(h->buffers[i]);
    pthread_mutex_destroy(&h->lock);
    free(h);
}

struct ThreadArg
{
    int thread_id;
    struct Receiver* receiver;
};

static void* do_receive(void* arg)
{
    struct ThreadArg* a = (struct ThreadArg*) arg;
    struct Receiver* receiver = a->receiver;
    const int thread_id = a->thread_id;
    const int num_threads = receiver->num_threads;
    const int num_streams = receiver->num_streams;
    while (receiver->completed_streams != num_streams)
    {
        for (int i = thread_id; i < num_streams; i += num_threads)
        {
            struct Stream* stream = receiver->streams[i];
            if (!stream->done)
                stream_receive(stream);
        }
        barrier_wait(receiver->barrier);
        if (thread_id == 0)
        {
            size_t dump_byte_counter = 0, recv_byte_counter = 0;
            receiver->completed_streams = 0;
            for (int i = 0; i < num_streams; ++i)
            {
                struct Stream* stream = receiver->streams[i];
                if (stream->done) receiver->completed_streams++;
                recv_byte_counter += stream->recv_byte_counter;
                dump_byte_counter += stream->dump_byte_counter;
            }
            const double overall_time = tmr_elapsed(receiver->tmr);
            if (recv_byte_counter > 1000000000uL || overall_time > 1.0)
            {
                double memcpy_total = 0.0;
                for (int i = 0; i < num_streams; ++i)
                {
                    struct Stream* stream = receiver->streams[i];
                    stream->recv_byte_counter = 0;
                    stream->dump_byte_counter = 0;
                    memcpy_total += tmr_elapsed(stream->tmr_memcpy);
                    tmr_clear(stream->tmr_memcpy);
                }
                memcpy_total /= num_streams;
                printf("Received %.3f MB in %.3f sec (%.2f MB/s), "
                        "memcpy was %.2f%%\n",
                        recv_byte_counter / 1e6, overall_time,
                        (recv_byte_counter / 1e6) / overall_time,
                        100 * (memcpy_total / overall_time));
                if (dump_byte_counter > 0)
                    printf("WARNING: Dumped %zu bytes\n", dump_byte_counter);
                tmr_start(receiver->tmr);
            }
        }
        barrier_wait(receiver->barrier);
    }
    return 0;
}

void receiver_receive(struct Receiver* h)
{
    if (!h) return;
    const int num_threads = h->num_threads;
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);
    pthread_t* threads =
            (pthread_t*) malloc(num_threads * sizeof(pthread_t));
    struct ThreadArg* args =
            (struct ThreadArg*) malloc(num_threads * sizeof(struct ThreadArg));
    tmr_start(h->tmr);
    for (int i = 0; i < num_threads; ++i)
    {
        args[i].thread_id = i;
        args[i].receiver = h;
        pthread_create(&threads[i], &attr, do_receive, &args[i]);
    }
    for (int i = 0; i < num_threads; ++i)
        pthread_join(threads[i], NULL);
    pthread_attr_destroy(&attr);
    free(args);
    printf("All %d stream(s) completed.\n", h->num_streams);
}

int main(int argc, char** argv)
{
    int num_streams = 1, num_receiver_threads = 1;
    int num_times_in_buffer = 8, num_buffers = 2;
    unsigned short int port_start = 41000;
    if (argc > 1) num_streams = atoi(argv[1]);
    if (argc > 2) num_receiver_threads = atoi(argv[2]);
    if (argc > 3) num_times_in_buffer = atoi(argv[3]);
    if (argc > 4) num_buffers = atoi(argv[4]);
    if (argc > 5) port_start  = (unsigned short int) atoi(argv[5]);
    if (num_streams < 1) num_streams = 1;
    if (num_receiver_threads < 1) num_receiver_threads = 1;
    if (num_times_in_buffer < 1) num_times_in_buffer = 1;
    if (num_buffers < 1) num_buffers = 1;
    printf("Running RECV_VERSION %s\n", RECV_VERSION);
    printf(" + Number of SPEAD streams    : %d\n", num_streams);
    printf(" + Number of receiver threads : %d\n", num_receiver_threads);
    printf(" + Number of times in buffer  : %d\n", num_times_in_buffer);
    printf(" + Number of buffers          : %d\n", num_buffers);
    printf(" + UDP port range             : %d-%d\n",
            (int) port_start, (int) port_start + num_streams - 1);
    struct Receiver* receiver = receiver_create(num_buffers,
            num_times_in_buffer, num_receiver_threads, num_streams, port_start);
    receiver_receive(receiver);
    receiver_free(receiver);
    return 0;
}
