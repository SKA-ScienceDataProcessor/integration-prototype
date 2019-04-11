#ifdef __linux__
#  define _GNU_SOURCE
#  include <sched.h>
#endif
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

#include "buffer.h"
#include "receiver.h"
#include "stream.h"
#include "thread_barrier.h"
#include "thread_pool.h"
#include "timer.h"

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
        int num_threads_recv, int num_threads_write, int num_streams,
        unsigned short int port_start, int num_channels_per_file,
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
    cls->num_threads_write = num_threads_write;
    cls->num_streams = num_streams;
    cls->num_channels_per_file = num_channels_per_file;
    if (output_root && strlen(output_root) > 0)
    {
        cls->output_root = (char*) malloc(1 + strlen(output_root));
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
    struct Buffer* buffer;
};

static void* thread_write_parallel(void* arg)
{
    struct ThreadArg* a = (struct ThreadArg*) arg;
    struct Receiver* receiver = a->receiver;
    struct Buffer* buf = a->buffer;
    const int thread_id = a->thread_id;
    const int num_threads = receiver->num_threads_write;
    const int num_baselines = buf->num_baselines;
    const int num_channels = buf->num_channels;
    const int num_channels_per_file = receiver->num_channels_per_file;
    size_t len = 2 + strlen(receiver->output_root);
    len += (10 + 1 + 10 + 4);
    char* filename = (char*) calloc(len, sizeof(char));
    for (int c = thread_id * num_channels_per_file; c < num_channels;
            c += (num_threads * num_channels_per_file))
    {
        int c_end = c + num_channels_per_file - 1;
        if (c_end >= num_channels) c_end = num_channels - 1;
        int num_channels_block = c_end - c + 1;
        snprintf(filename, len, "%s_t%.4d-%.4d_c%.4d-%.4d.dat",
                receiver->output_root,
                buf->heap_id_start, buf->heap_id_end, c, c_end);
        /* Use POSIX creat(), write(), close()
         * instead of fopen(), fwrite(), fclose(),
         * as fwrite() doesn't seem to work with Alpine and BeeGFS. */
        int file_handle = creat(filename,
                S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);
        if (file_handle < 0)
        {
            printf("Unable to open file %s\n", filename);
            break;
        }
        for (int t = 0; t < buf->num_times; ++t)
        {
            const struct DataType* block_start = buf->vis_data +
                    num_baselines * (num_channels * t + c);
            write(file_handle, (const void*)block_start,
                    num_channels_block * buf->block_size);
        }
        close(file_handle);
    }
    free(filename);
    return 0;
}

static void* thread_write_buffer(void* arg)
{
    struct Buffer* buf = (struct Buffer*) arg;
    struct Receiver* receiver = buf->receiver;
    if (buf->byte_counter != buf->buffer_size)
        printf("WARNING: Buffer %d incomplete (%zu/%zu, %.1f%%)\n",
                buf->buffer_id, buf->byte_counter, buf->buffer_size,
                100 * buf->byte_counter / (float)buf->buffer_size);
    if (receiver->output_root)
    {
#ifdef __linux__
        const int cpu_id = sched_getcpu();
        printf("Writing buffer %d from CPU %d...\n", buf->buffer_id, cpu_id);
#else
        printf("Writing buffer %d...\n", buf->buffer_id);
#endif
        const double start = tmr_get_timestamp();
        const int num_threads = receiver->num_threads_write;
        pthread_attr_t attr;
        pthread_attr_init(&attr);
        pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);
        pthread_t* threads =
                (pthread_t*) malloc(num_threads * sizeof(pthread_t));
        struct ThreadArg* args = (struct ThreadArg*)
                malloc(num_threads * sizeof(struct ThreadArg));
        for (int i = 0; i < num_threads; ++i)
        {
            args[i].thread_id = i;
            args[i].receiver = receiver;
            args[i].buffer = buf;
            pthread_create(&threads[i], &attr,
                    &thread_write_parallel, &args[i]);
        }
        for (int i = 0; i < num_threads; ++i)
            pthread_join(threads[i], NULL);
        pthread_attr_destroy(&attr);
        free(args);
        free(threads);
        const double time_taken = tmr_get_timestamp() - start;
        printf("Writing buffer %d with %d threads took %.2f sec (%.2f MB/s)\n",
                buf->buffer_id, num_threads, time_taken,
                buf->buffer_size * 1e-6 / time_taken);
    }
    buffer_clear(buf);
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
        pthread_create(&threads[i], &attr, &thread_receive, &args[i]);
    }
    for (int i = 0; i < num_threads; ++i)
        pthread_join(threads[i], NULL);
    pthread_attr_destroy(&attr);
    free(args);
    free(threads);
    printf("All %d stream(s) completed.\n", self->num_streams);
}
