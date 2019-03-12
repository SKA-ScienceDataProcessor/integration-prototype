#ifndef RECV_STREAM_H_
#define RECV_STREAM_H_

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

struct Timer;
struct Receiver;

struct Stream
{
    unsigned char* socket_buffer;
    struct Receiver* receiver;
    struct Timer *tmr_memcpy;
    size_t dump_byte_counter, recv_byte_counter, vis_data_heap_offset;
    int buffer_len, done, heap_count, socket_handle, stream_id;
    unsigned short int port;
};

/**
 * @brief Creates a new stream to receive data on the specified UDP port.
 */
struct Stream* stream_create(unsigned short int port, int stream_id,
        struct Receiver* receiver);

/**
 * @brief Decodes one or more UDP packets in the buffer.
 */
void stream_decode(struct Stream* self, const unsigned char* buf, int depth);

/**
 * @brief Destroys the stream.
 */
void stream_free(struct Stream* self);

/**
 * @brief Receives data from the stream's network socket.
 */
void stream_receive(struct Stream* self);

#ifdef __cplusplus
}
#endif

#endif /* include guard */
