#ifdef __linux__
#  define _GNU_SOURCE
#  include <sched.h>
#endif
#include <sys/socket.h>
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

#define RECV_VERSION "1.2.1"

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

struct ThreadTask
{
    void *(*thread_func)(void*);
    void* arg;
    struct ThreadTask* next;
};

struct ThreadPool
{
    pthread_mutex_t lock;
    pthread_cond_t cond;
    pthread_t* threads;
    struct ThreadTask *task_list, *last_task;
    int do_abort, num_threads, num_tasks;
};

struct Buffer
{
    /* From slowest to fastest varying, dimension order is
     * (time, channel, baseline) */
    struct DataType* vis_data;
    struct Receiver* receiver;
    double last_updated;
    size_t buffer_size, block_size, byte_counter;
    int buffer_id, heap_id_start, heap_id_end, locked_for_write;
    int num_times, num_channels, num_baselines;
};

struct Stream
{
    uchar* socket_buffer;
    struct Receiver* receiver;
    struct Timer *tmr_memcpy;
    size_t dump_byte_counter, recv_byte_counter, vis_data_heap_offset;
    int buffer_len, done, heap_count, socket_handle, stream_id;
    unsigned short int port;
};

struct Receiver
{
    pthread_mutex_t lock;
    struct ThreadBarrier* barrier;
    struct ThreadPool* pool;
    struct Timer* tmr;
    struct Stream** streams;
    struct Buffer** buffers;
    char* output_root;
    int completed_streams;
    int num_baselines, num_times_in_buffer, max_num_buffers;
    int num_threads_recv, num_streams, num_buffers;
    unsigned short int port_start;
};

struct Buffer* buffer_create(int num_times, int num_channels,
        int num_baselines, int buffer_id, struct Receiver* receiver);
void buffer_free(struct Buffer* self);

struct Buffer* receiver_buffer(struct Receiver* self, int heap, size_t length,
        double timestamp);
struct Receiver* receiver_create(int num_buffers, int num_times_in_buffer,
        int num_threads_recv, int num_streams, unsigned short int port_start,
        const char* output_root);
void receiver_free(struct Receiver* self);
void receiver_start(struct Receiver* self);

struct Stream* stream_create(unsigned short int port, int stream_id,
        struct Receiver* receiver);
void stream_decode(struct Stream* self, const unsigned char* buf, int depth);
void stream_free(struct Stream* self);
void stream_receive(struct Stream* self);

struct ThreadPool* threadpool_create(int num_threads);
void threadpool_enqueue(struct ThreadPool* self,
        void *(*thread_func)(void*), void *arg);
void threadpool_free(struct ThreadPool* self);
static void* threadpool_thread(void* arg);

void tmr_clear(struct Timer* self);
struct Timer* tmr_create(void);
double tmr_elapsed(struct Timer* self);
void tmr_free(struct Timer* self);
double tmr_get_timestamp(void);
void tmr_pause(struct Timer* self);
void tmr_restart(struct Timer* self);
void tmr_resume(struct Timer* self);
void tmr_start(struct Timer* self);

char* construct_output_root(const char* output_location,
        const char* output_name);

void tmr_clear(struct Timer* self)
{
    self->paused = 1;
    self->start = self->elapsed = 0.0;
}

struct Timer* tmr_create(void)
{
    struct Timer* cls = (struct Timer*) calloc(1, sizeof(struct Timer));
    tmr_clear(cls);
    return cls;
}

double tmr_elapsed(struct Timer* self)
{
    if (self->paused) return self->elapsed;
    const double now = tmr_get_timestamp();
    self->elapsed += (now - self->start);
    self->start = now;
    return self->elapsed;
}

void tmr_free(struct Timer* self)
{
    free(self);
}

double tmr_get_timestamp(void)
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

void tmr_pause(struct Timer* self)
{
    if (self->paused) return;
    (void)tmr_elapsed(self);
    self->paused = 1;
}

void tmr_restart(struct Timer* self)
{
    self->paused = 0;
    self->start = tmr_get_timestamp();
}

void tmr_resume(struct Timer* self)
{
    if (!self->paused) return;
    tmr_restart(self);
}

void tmr_start(struct Timer* self)
{
    self->elapsed = 0.0;
    tmr_restart(self);
}

struct ThreadBarrier* barrier_create(int num_threads)
{
    struct ThreadBarrier* cls =
            (struct ThreadBarrier*) calloc(1, sizeof(struct ThreadBarrier));
    pthread_mutex_init(&cls->lock, NULL);
    pthread_cond_init(&cls->cond, NULL);
    cls->num_threads = num_threads;
    cls->count = num_threads;
    cls->iter = 0;
    return cls;
}

void barrier_free(struct ThreadBarrier* self)
{
    if (!self) return;
    pthread_mutex_destroy(&self->lock);
    pthread_cond_destroy(&self->cond);
    free(self);
}

int barrier_wait(struct ThreadBarrier* self)
{
    pthread_mutex_lock(&self->lock);
    const unsigned int i = self->iter;
    if (--(self->count) == 0)
    {
        (self->iter)++;
        self->count = self->num_threads;
        pthread_cond_broadcast(&self->cond);
        pthread_mutex_unlock(&self->lock);
        return 1;
    }
    do {
        pthread_cond_wait(&self->cond, &self->lock);
    } while (i == self->iter);
    pthread_mutex_unlock(&self->lock);
    return 0;
}

struct ThreadPool* threadpool_create(int num_threads)
{
    struct ThreadPool* cls =
            (struct ThreadPool*) calloc(1, sizeof(struct ThreadPool));
    pthread_mutex_init(&cls->lock, 0);
    pthread_cond_init(&cls->cond, 0);
    cls->threads = (pthread_t*) malloc(num_threads * sizeof(pthread_t));
    cls->num_threads = num_threads;
    for (int i = 0; i < num_threads; ++i)
        pthread_create(&cls->threads[i], 0, &threadpool_thread, cls);
    return cls;
}

void threadpool_enqueue(struct ThreadPool* self,
        void *(*thread_func)(void*), void *arg)
{
    if (!self) return;
    struct ThreadTask* task =
            (struct ThreadTask*) malloc(sizeof(struct ThreadTask));
    task->thread_func = thread_func;
    task->arg = arg;
    task->next = 0;
    pthread_mutex_lock(&self->lock);
    if (self->last_task) self->last_task->next = task;
    if (!self->task_list) self->task_list = task;
    self->last_task = task;
    self->num_tasks++;
    pthread_cond_signal(&self->cond);
    pthread_mutex_unlock(&self->lock);
}

void threadpool_free(struct ThreadPool* self)
{
    if (!self) return;
    self->do_abort = 1;
    pthread_mutex_lock(&self->lock);
    pthread_cond_broadcast(&self->cond);
    pthread_mutex_unlock(&self->lock);
    for (int i = 0; i < self->num_threads; i++)
        pthread_join(self->threads[i], 0);
    while (self->task_list)
    {
        struct ThreadTask* task = self->task_list;
        self->task_list = task->next;
        free(task);
    }
    free(self->threads);
    free(self);
}

static void* threadpool_thread(void* arg)
{
    struct ThreadPool* pool = (struct ThreadPool*)arg;
    while (!pool->do_abort)
    {
        pthread_mutex_lock(&pool->lock);
        while (!pool->do_abort && !pool->task_list)
            pthread_cond_wait(&pool->cond, &pool->lock);
        if (pool->do_abort)
        {
            pthread_mutex_unlock(&pool->lock);
            return 0;
        }
        struct ThreadTask* task = pool->task_list;
        pool->task_list = task->next;
        pool->num_tasks--;
        if (task == pool->last_task) pool->last_task = 0;
        pthread_mutex_unlock(&pool->lock);
        task->thread_func(task->arg);
        free(task);
        pthread_mutex_lock(&pool->lock);
        pthread_cond_broadcast(&pool->cond);
        pthread_mutex_unlock(&pool->lock);
    }
    return 0;
}

void buffer_clear(struct Buffer* self)
{
    // memset(self->vis_data, 0, self->buffer_size);
#if 0
    const int num_times = self->num_times;
    const int num_channels = self->num_channels;
    const int num_baselines = self->num_baselines;
    for (int t = 0; t < num_times; ++t)
        for (int c = 0; c < num_channels; ++c)
            for (int b = 0; b < num_baselines; ++b)
                self->vis_data[
                        num_baselines * (num_channels * t + c) + b].fd = 1;
#endif
    self->byte_counter = 0;
}

struct Buffer* buffer_create(int num_times, int num_channels,
        int num_baselines, int buffer_id, struct Receiver* receiver)
{
    struct Buffer* cls = (struct Buffer*) calloc(1, sizeof(struct Buffer));
    cls->buffer_id = buffer_id;
    cls->num_baselines = num_baselines;
    cls->num_channels = num_channels;
    cls->num_times = num_times;
    cls->block_size = num_baselines * sizeof(struct DataType);
    cls->buffer_size = cls->block_size * num_channels * num_times;
    printf("Allocating %.3f MB buffer.\n", cls->buffer_size * 1e-6);
    cls->vis_data = (struct DataType*) malloc(cls->buffer_size);
    if (!cls->vis_data)
    {
        fprintf(stderr,
                "malloc failed: requested %zu bytes\n", cls->buffer_size);
        exit(1);
    }
    // buffer_clear(cls);
    cls->receiver = receiver;
    return cls;
}

void buffer_free(struct Buffer* self)
{
    if (!self) return;
    free(self->vis_data);
    free(self);
}

struct Stream* stream_create(unsigned short int port, int stream_id,
        struct Receiver* receiver)
{
    struct Stream* cls = (struct Stream*) calloc(1, sizeof(struct Stream));
    const int requested_buffer_len = 16*1024*1024;
    cls->port = port;
    cls->buffer_len = requested_buffer_len;
    cls->stream_id = stream_id;
    if ((cls->socket_handle = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        fprintf(stderr, "Cannot create socket.\n");
        return cls;
    }
    fcntl(cls->socket_handle, F_SETFL, O_NONBLOCK);
    setsockopt(cls->socket_handle, SOL_SOCKET, SO_RCVBUF,
            &cls->buffer_len, sizeof(int));
    uint32_t int_size = (uint32_t) sizeof(int);
    getsockopt(cls->socket_handle, SOL_SOCKET, SO_RCVBUF,
            &cls->buffer_len, &int_size);
    if (int_size != (uint32_t) sizeof(int))
    {
        fprintf(stderr, "Error at line %d\n", __LINE__);
        exit(1);
    }
    if ((cls->buffer_len / 2) < requested_buffer_len)
    {
        printf("Requested socket buffer of %d bytes; actual size is %d bytes\n",
                requested_buffer_len, cls->buffer_len / 2);
    }
    struct sockaddr_in myaddr;
    myaddr.sin_family = AF_INET;
    myaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    myaddr.sin_port = htons(port);
    if (bind(cls->socket_handle, (struct sockaddr*)&myaddr, sizeof(myaddr)) < 0)
    {
        fprintf(stderr, "Bind failed.\n");
        return cls;
    }
    cls->socket_buffer = (uchar*) malloc(cls->buffer_len);
    memset(cls->socket_buffer, 0, cls->buffer_len);
    cls->receiver = receiver;
    cls->tmr_memcpy = tmr_create();
    return cls;
}

void stream_decode(struct Stream* self, const uchar* buf, int depth)
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
            if (depth == 0) self->heap_count = (int) item_addr - 2;
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
            /*stream_decode(self, &payload_start[item_addr], depth + 1);*/
            break;
        case 0x6:
            /* Stream control messages (immediate addressing, big endian). */
            packet_has_stream_control = 1;
            if (item_addr == 2) self->done = 1;
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
            self->receiver->num_baselines = be32toh((uint32_t) item_addr);
            packet_has_header_data = 1;
            break;
        case 0x6008:
            /* Scan ID (absolute addressing). */
            scan_id = *( (uint64_t*)(payload_start + item_addr) );
            packet_has_header_data = 1;
            break;
        case 0x600A:
            /* Visibility data (absolute addressing). */
            self->vis_data_heap_offset = (size_t) item_addr;
            vis_data_start = (size_t) item_addr;
            break;
        default:
            /*printf("Heap %3d  ID: %#6llx, %s: %llu\n", self->heap_count,
                    item_id, immediate ? "VAL" : "ptr", item_addr);*/
            break;
        }
    }
    if (0 && !packet_has_stream_control)
        printf("==== Packet in heap %3d "
                "(heap offset %zu/%zu, payload length %zu)\n", self->heap_count,
                heap_offset, heap_size, packet_payload_length);
    if (0 && packet_has_header_data)
    {
        printf("     heap               : %d\n", self->heap_count);
        printf("     timestamp_count    : %" PRIu32 "\n", timestamp_count);
        printf("     timestamp_fraction : %" PRIu32 "\n", timestamp_fraction);
        printf("     scan_id            : %" PRIu64 "\n", scan_id);
        printf("     num_baselines      : %d\n", self->receiver->num_baselines);
    }
    if (!packet_has_stream_control && self->vis_data_heap_offset > 0 &&
            self->receiver->num_baselines > 0)
    {
        const double timestamp = tmr_get_timestamp();
        const size_t vis_data_length = packet_payload_length - vis_data_start;
        /*printf("Visibility data length: %zu bytes\n", vis_data_length);*/
        struct Buffer* buf = receiver_buffer(
                self->receiver, self->heap_count, vis_data_length, timestamp);
        if (buf)
        {
            const uchar* src_addr = payload_start + vis_data_start;
            const int i_time = self->heap_count - buf->heap_id_start;
            const int i_chan = self->stream_id;
            uchar* dst_addr = ((uchar*) buf->vis_data) +
                    heap_offset - self->vis_data_heap_offset + vis_data_start +
                    buf->block_size * (i_time * buf->num_channels + i_chan);
            tmr_resume(self->tmr_memcpy);
            memcpy(dst_addr, src_addr, vis_data_length);
            tmr_pause(self->tmr_memcpy);
            self->recv_byte_counter += vis_data_length;
        }
        else
        {
            self->dump_byte_counter += vis_data_length;
        }
    }
}

void stream_free(struct Stream* self)
{
    if (!self) return;
    tmr_free(self->tmr_memcpy);
    close(self->socket_handle);
    free(self->socket_buffer);
    free(self);
}

void stream_receive(struct Stream* self)
{
    if (!self) return;
    const int recvlen = recv(
            self->socket_handle, self->socket_buffer, self->buffer_len, 0);
    if (recvlen >= 8)
        stream_decode(self, self->socket_buffer, 0);
}

struct Buffer* receiver_buffer(struct Receiver* self, int heap, size_t length,
        double timestamp)
{
    if (!self) return 0;
    struct Buffer* buf = 0;
    int oldest = -1, min_heap_start = 1 << 30;
    pthread_mutex_lock(&self->lock);
    for (int i = 0; i < self->num_buffers; ++i)
    {
        struct Buffer* buf_test = self->buffers[i];
        if (heap >= buf_test->heap_id_start && heap <= buf_test->heap_id_end &&
                !buf_test->locked_for_write)
        {
            buf_test->byte_counter += length;
            buf_test->last_updated = timestamp;
            pthread_mutex_unlock(&self->lock);
            return buf_test;
        }
        if (buf_test->heap_id_start < min_heap_start)
        {
            min_heap_start = buf_test->heap_id_start;
            oldest = i;
        }
    }
    /* Heap does not belong in any active buffer. */
    if (oldest >= 0)
    {
        if (heap < min_heap_start)
        {
            /* Dump data if it's too old. */
            pthread_mutex_unlock(&self->lock);
            return 0;
        }
        struct Buffer* buf_test = self->buffers[oldest];
        if (buf_test->byte_counter == 0 && !buf_test->locked_for_write)
        {
            /* Re-purpose the oldest buffer, if it isn't in use. */
            buf = buf_test;
            printf("Re-assigned buffer %d\n", buf->buffer_id);
        }
    }
    if (!buf && (self->num_buffers < self->max_num_buffers))
    {
        /* Create a new buffer. */
        buf = buffer_create(self->num_times_in_buffer, self->num_streams,
                self->num_baselines, self->num_buffers, self);
        printf("Created buffer %d\n", self->num_buffers);
        self->num_buffers++;
        self->buffers = (struct Buffer**) realloc(self->buffers,
                self->num_buffers * sizeof(struct Buffer*));
        self->buffers[self->num_buffers - 1] = buf;
    }
    if (buf)
    {
        buf->byte_counter += length;
        buf->last_updated = timestamp;
        buf->heap_id_start =
                self->num_times_in_buffer * (heap / self->num_times_in_buffer);
        buf->heap_id_end = buf->heap_id_start + self->num_times_in_buffer - 1;
    }
    pthread_mutex_unlock(&self->lock);
    return buf;
}

struct Receiver* receiver_create(int num_buffers, int num_times_in_buffer,
        int num_threads_recv, int num_streams, unsigned short int port_start,
        const char* output_root)
{
    struct Receiver* cls =
            (struct Receiver*) calloc(1, sizeof(struct Receiver));
    pthread_mutex_init(&cls->lock, NULL);
    cls->tmr = tmr_create();
    cls->barrier = barrier_create(num_threads_recv);
    cls->pool = threadpool_create(1);
    cls->max_num_buffers = num_buffers;
    cls->num_times_in_buffer = num_times_in_buffer;
    cls->num_threads_recv = num_threads_recv;
    cls->num_streams = num_streams;
    if (output_root)
    {
        cls->output_root = malloc(1 + strlen(output_root));
        strcpy(cls->output_root, output_root);
    }
    cls->port_start = port_start;
    cls->streams =
            (struct Stream**) calloc(num_streams, sizeof(struct Stream*));
    for (int i = 0; i < num_streams; ++i)
        cls->streams[i] = stream_create(
                port_start + (unsigned short int)i, i, cls);
    return cls;
}

void receiver_free(struct Receiver* self)
{
    if (!self) return;
    tmr_free(self->tmr);
    barrier_free(self->barrier);
    threadpool_free(self->pool);
    for (int i = 0; i < self->num_streams; ++i) stream_free(self->streams[i]);
    for (int i = 0; i < self->num_buffers; ++i) buffer_free(self->buffers[i]);
    pthread_mutex_destroy(&self->lock);
    free(self->output_root);
    free(self);
}

struct ThreadArg
{
    int thread_id;
    struct Receiver* receiver;
};

static void* thread_write_buffer(void* arg)
{
    struct Buffer* buf = (struct Buffer*) arg;
    struct Receiver* receiver = buf->receiver;
    printf("Writing buffer %d...\n", buf->buffer_id);
#ifdef __linux__
    const int cpu_id = sched_getcpu();
    printf("Writer thread running on CPU %d\n", cpu_id);
#endif
    double start = tmr_get_timestamp();
    if (buf->byte_counter != buf->buffer_size)
        printf("WARNING: Incomplete buffer (%zu/%zu, %.1f%%)\n",
                buf->byte_counter, buf->buffer_size,
                100 * buf->byte_counter / (float)buf->buffer_size);
    /* Could start another parallel region here to perform the write. */
    if (receiver->output_root)
    {
        size_t len = 2 + strlen(receiver->output_root);
        len += (10 + 1 + 10 + 4);
        char* filename = calloc(len, sizeof(char));
        const int time_start = buf->heap_id_start;
        const int time_end = buf->heap_id_end;
        const int chan_start = 0;
        const int chan_end = buf->num_channels - 1;
        snprintf(filename, len, "%s_t%.4d-%.4d_c%.4d-%.4d.dat",
                receiver->output_root,
                time_start, time_end, chan_start, chan_end);
        FILE* file_handle = fopen(filename, "w");
        if (file_handle)
        {
            fwrite(buf->vis_data, buf->buffer_size, 1, file_handle);
            fclose(file_handle);
        }
        free(filename);
    }
    buffer_clear(buf);
    printf("Writing buffer %d took %.3f sec.\n",
            buf->buffer_id, tmr_get_timestamp() - start);
    buf->locked_for_write = 0;
    return 0;
}

static void* thread_receive(void* arg)
{
    struct ThreadArg* a = (struct ThreadArg*) arg;
    struct Receiver* receiver = a->receiver;
    const int thread_id = a->thread_id;
    const int num_threads = receiver->num_threads_recv;
    const int num_streams = receiver->num_streams;
    while (receiver->completed_streams != num_streams)
    {
        for (int i = thread_id; i < num_streams; i += num_threads)
        {
            struct Stream* stream = receiver->streams[i];
            if (!stream->done)
                stream_receive(stream);
        }
        if (num_threads > 1)
            barrier_wait(receiver->barrier);
        if (thread_id == 0)
        {
            const int num_buffers = receiver->num_buffers;
            double now = tmr_get_timestamp();
            for (int i = 0; i < num_buffers; ++i)
            {
                struct Buffer* buf = receiver->buffers[i];
                if ((buf->byte_counter > 0) && !buf->locked_for_write &&
                        (now - buf->last_updated >= 1.0))
                {
                    buf->locked_for_write = 1;
                    printf("Locked buffer %d for writing\n", buf->buffer_id);
                    threadpool_enqueue(receiver->pool,
                            &thread_write_buffer, buf);
                }
            }
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
        if (num_threads > 1)
            barrier_wait(receiver->barrier);
    }
    return 0;
}

void receiver_start(struct Receiver* self)
{
    if (!self) return;
    const int num_threads = self->num_threads_recv;
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);
    pthread_t* threads =
            (pthread_t*) malloc(num_threads * sizeof(pthread_t));
    struct ThreadArg* args =
            (struct ThreadArg*) malloc(num_threads * sizeof(struct ThreadArg));
    tmr_start(self->tmr);
    for (int i = 0; i < num_threads; ++i)
    {
        args[i].thread_id = i;
        args[i].receiver = self;
        pthread_create(&threads[i], &attr, thread_receive, &args[i]);
    }
    for (int i = 0; i < num_threads; ++i)
        pthread_join(threads[i], NULL);
    pthread_attr_destroy(&attr);
    free(args);
    printf("All %d stream(s) completed.\n", self->num_streams);
}

char* construct_output_root(const char* output_location,
        const char* output_name)
{
    if (!output_location || strlen(output_location) == 0) return 0;
    size_t len = 3 + strlen(output_location) + strlen(output_name);
    len += (8 + 1 + 6); /* Date and time. */
    char* output_root = calloc(len, sizeof(char));
    const time_t unix_time = time(NULL);
    struct tm* timeinfo = localtime(&unix_time);
    snprintf(output_root, len, "%s/%s_%.4d%.2d%.2d-%.2d%.2d%.2d",
            output_location, output_name,
            timeinfo->tm_year + 1900, timeinfo->tm_mon + 1, timeinfo->tm_mday,
            timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);
    return output_root;
}

int main(int argc, char** argv)
{
    int num_streams = 1, num_threads_recv = 1;
    int num_times_in_buffer = 8, num_buffers = 2;
    unsigned short int port_start = 41000;
    const char* output_location = 0;
    const char* output_name = "ingest_run";
    if (argc > 1) num_streams = atoi(argv[1]);
    if (argc > 2) num_threads_recv = atoi(argv[2]);
    if (argc > 3) num_times_in_buffer = atoi(argv[3]);
    if (argc > 4) num_buffers = atoi(argv[4]);
    if (argc > 5) port_start  = (unsigned short int) atoi(argv[5]);
    if (argc > 6) output_location = argv[6];
    if (num_streams < 1) num_streams = 1;
    if (num_threads_recv < 1) num_threads_recv = 1;
    if (num_times_in_buffer < 1) num_times_in_buffer = 1;
    if (num_buffers < 1) num_buffers = 1;
    printf("Running RECV_VERSION %s\n", RECV_VERSION);
    char* output_root = construct_output_root(output_location, output_name);
    const int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (num_threads_recv > num_cores - 2) num_threads_recv = num_cores - 2;
#ifdef __linux__
    cpu_set_t my_set;
    CPU_ZERO(&my_set);
    for (int i = 0; i < num_cores / 2; i++)
    {
        CPU_SET(i, &my_set);
    }
    sched_setaffinity(0, sizeof(cpu_set_t), &my_set);
#endif
    printf(" + Number of system CPU cores : %d\n", num_cores);
    printf(" + Number of SPEAD streams    : %d\n", num_streams);
    printf(" + Number of receiver threads : %d\n", num_threads_recv);
    printf(" + Number of times in buffer  : %d\n", num_times_in_buffer);
    printf(" + Number of buffers          : %d\n", num_buffers);
    printf(" + UDP port range             : %d-%d\n",
            (int) port_start, (int) port_start + num_streams - 1);
    printf(" + Output root                : %s\n", output_root);
    struct Receiver* receiver = receiver_create(num_buffers,
            num_times_in_buffer, num_threads_recv, num_streams, port_start,
            output_root);
    receiver_start(receiver);
    receiver_free(receiver);
    free(output_root);
    return 0;
}
