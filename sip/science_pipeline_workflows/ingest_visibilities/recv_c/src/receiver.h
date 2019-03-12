#ifndef RECV_RECEIVER_H_
#define RECV_RECEIVER_H_

#include <pthread.h>

#ifdef __cplusplus
extern "C" {
#endif

struct ThreadBarrier;
struct ThreadPool;
struct Timer;
struct Stream;
struct Buffer;

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
    int num_threads_recv, num_threads_write, num_streams, num_buffers;
    int num_channels_per_file;
    unsigned short int port_start;
};

/**
 * @brief Returns a handle to the buffer to use for the specified heap.
 */
struct Buffer* receiver_buffer(struct Receiver* self, int heap, size_t length,
        double timestamp);

/**
 * @brief Creates a new receiver.
 */
struct Receiver* receiver_create(int num_buffers, int num_times_in_buffer,
        int num_threads_recv, int num_threads_write, int num_streams,
        unsigned short int port_start, int num_channels_per_file,
        const char* output_root);

/**
 * @brief Destroys the receiver.
 */
void receiver_free(struct Receiver* self);

/**
 * @brief Activates the receiver and blocks until all streams have finished.
 */
void receiver_start(struct Receiver* self);

#ifdef __cplusplus
}
#endif

#endif /* include guard */
