#include <gtest/gtest.h>

#ifdef __APPLE__
#  include <libkern/OSByteOrder.h>
#  define htobe32(x) OSSwapHostToBigInt32(x)
#  define htobe64(x) OSSwapHostToBigInt64(x)
#else
#  include <endian.h>
#endif

#include "receiver.h"
#include "stream.h"
#include "buffer.h"

#include <cstdio>
#include <inttypes.h>

//////////////////////////////////////////////////////////////////////
// Test utility functions.
//////////////////////////////////////////////////////////////////////

static struct Receiver* create_test_receiver()
{
    const int num_buffers_max = 1;
    const int num_times_in_buffer = 4;
    const int num_threads_recv = 1;
    const int num_threads_write = 1;
    const int num_streams = 1;
    const unsigned short int port_start = 41000;
    const int num_channels_per_file = 1;
    const char* output_root = "";
    struct Receiver* receiver = receiver_create(num_buffers_max,
            num_times_in_buffer, num_threads_recv, num_threads_write,
            num_streams, port_start, num_channels_per_file, output_root);
    return receiver;
}

//////////////////////////////////////////////////////////////////////
// Tests.
//////////////////////////////////////////////////////////////////////

TEST(Receiver, test_create)
{
    struct Receiver* receiver = create_test_receiver();
    ASSERT_TRUE(receiver != NULL);
    receiver_free(receiver);
}

TEST(Stream, test_stream_decode)
{
    // Verify stream_decode() function can handle a simple SPEAD packet.

    // SPEAD packet item IDs.
    const unsigned int item_ids[] = {
        0x1,    // Heap counter.
        0x2,    // Heap size.
        0x3     // Heap offset.
    };

    // Dummy values for items.
    const int item_val[] = {
        4,
        10,
        55
    };
    const unsigned int num_items = sizeof(item_ids) / sizeof(unsigned int);

    // Allocate memory for a SPEAD packet.
    unsigned char* buf = (unsigned char*) malloc(8 + num_items * 8);
    ASSERT_TRUE(buf != NULL);

    // Define SPEAD flavour.
    const unsigned char heap_address_bits = 48;
    const unsigned char item_id_bits = 64 - heap_address_bits - 1;

    // Construct SPEAD packet header.
    buf[0] = 'S';
    buf[1] = 4;
    buf[2] = (item_id_bits + 1) / 8;
    buf[3] = heap_address_bits / 8;
    buf[4] = 0;
    buf[5] = 0;
    buf[6] = 0;
    buf[7] = (unsigned char) num_items;

    // Construct SPEAD packet payload containing items in
    // "immediate addressing mode".
    uint64_t* items = (uint64_t*) &buf[8];
    for (unsigned int i = 0; i < num_items; i++)
    {
        const uint64_t item_id = (uint64_t) item_ids[i];
        const uint64_t item_addr_or_val = (uint64_t) item_val[i];
        const uint64_t item =
                (1ull << 63) |
                (item_id << heap_address_bits) |
                item_addr_or_val;
        items[i] = htobe64(item);
    }

    // Create a test receiver.
    struct Receiver* receiver = create_test_receiver();
    ASSERT_TRUE(receiver != NULL);

    // Call stream_decode().
    stream_decode(receiver->streams[0], buf, 0);

    // Clean up.
    receiver_free(receiver);
    free(buf);
}
