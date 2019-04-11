#ifndef RECV_BUFFER_H_
#define RECV_BUFFER_H_

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

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

/**
 * @brief Clear an in-memory buffer (placeholder).
 */
void buffer_clear(struct Buffer* self);

/**
 * @brief Creates a new in-memory buffer.
 */
struct Buffer* buffer_create(int num_times, int num_channels,
        int num_baselines, int buffer_id, struct Receiver* receiver);

/**
 * @brief Destroys the in-memory buffer.
 */
void buffer_free(struct Buffer* self);

#ifdef __cplusplus
}
#endif

#endif /* include guard */
