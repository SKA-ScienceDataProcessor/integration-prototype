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

// TEST(Stream, test_stream_receive)
// {
//     /* Verify stream_decode() function and verify if correct
//     data is received */

//     // ADD DESCRIPTOR AND OTHER IDS
//     // SPEAD packet item IDs.
//     const unsigned int item_ids[] = {
//         0x1,    // Heap counter.
//         0x2,    // Heap size.
//         0x3,    // Heap offset.
//         0x4,    // packet payload length
//         0x5,    // item descriptor
//         0x6,    // stream control
//         // 0x10,   // item descriptor: name
//         // 0x11,   // item descriptor: description
//         // 0x12,   // item descriptor: shape
//         // 0x13,   // item descriptor: type
//         // 0x14,   // item descriptor: ID
//         // 0x15,   // item descriptor: dtype  
//         0x6000, // Visibility timestamp count
//         0x6001, // Visibility timestamp fraction
//         0x6005, // Visibility baseline count
//         0x6008, // Scan ID 
//         0x600A  // Visibility data 

//     };

//     // NEED TO FIGURE OUT HOW TO DO FLOOR IN C
//     // ADD DESCRIPTOR AND OTHER VALUES
//     // int num_baselines = (512 * 513) // 2
//     // Dummy values for items.

//     // # Update values in the heap.
//     // item_group['visibility_timestamp_count'].value = 1
//     // item_group['visibility_timestamp_fraction'].value = 0
//     // item_group['visibility_baseline_count'].value = num_baselines
//     // item_group['scan_id'].value = 100000000
//     // item_group['correlator_output_data'].value = vis

//     // Alternative to this in C
//     // vis = numpy.zeros(shape=(num_baselines,), dtype=dtype)

//     const int item_val[] = {
//         4,
//         10,
//         55,
//         55,
//         0,
//         1,              // Visibility timestamp count
//         0,              // Visibility timestamp fraction    
//         // num_baselines,  // Visibility baseline count
//         100000000,      // Scan ID 
//         // vis             // Visibility data 

//         // 1,
//         // 0
        
//     };
//     const unsigned int num_items = sizeof(item_ids) / sizeof(unsigned int);

//     // Allocate memory for a SPEAD packet.
//     unsigned char* buf = (unsigned char*) malloc(8 + num_items * 8);
//     ASSERT_TRUE(buf != NULL);

//     // Define SPEAD flavour.
//     const unsigned char heap_address_bits = 48;
//     const unsigned char item_id_bits = 64 - heap_address_bits - 1;

//     // Construct SPEAD packet header.
//     buf[0] = 'S';
//     buf[1] = 4;
//     buf[2] = (item_id_bits + 1) / 8;
//     buf[3] = heap_address_bits / 8;
//     buf[4] = 0;
//     buf[5] = 0;
//     buf[6] = 0;
//     buf[7] = (unsigned char) num_items;

//     // Construct SPEAD packet payload containing items in
//     // "immediate addressing mode".
//     uint64_t* items = (uint64_t*) &buf[8];
//     for (unsigned int i = 0; i < num_items; i++)
//     {
//         const uint64_t item_id = (uint64_t) item_ids[i];
//         const uint64_t item_addr_or_val = (uint64_t) item_val[i];
//         //printf("Item Value: %i\n", item_val[i]);
//         const uint64_t item =
//                 (1ull << 63) |
//                 (item_id << heap_address_bits) |
//                 item_addr_or_val;
//         items[i] = htobe64(item);
//     }

//     // Create a test receiver.
//     struct Receiver* receiver = create_test_receiver();
//     ASSERT_TRUE(receiver != NULL);

//     // Call stream_decode().
//     stream_decode(receiver->streams[0], buf, 0);
//     printf("Heap count - %i\n", receiver->streams[0]->heap_count);
//     printf("BUffer Len - %i\n", receiver->streams[0]->buffer_len);
//     printf("Num buffers - %i\n", receiver->num_buffers);
//     printf("completed_streams - %i\n", receiver->completed_streams);
//     printf("max_num_buffers - %i\n", receiver->max_num_buffers);
//     printf("num_baselines - %i\n", receiver->num_baselines);
//     // printf("buffer_id - %i\n", receiver->buffers[0]->buffer_id);
//     // struct Buffer* buff = receiver->buffers[0];
//     // printf("Buf %i", buff->buffer_id);

//     // Clean up.
//     receiver_free(receiver);
//     free(buf);
// }