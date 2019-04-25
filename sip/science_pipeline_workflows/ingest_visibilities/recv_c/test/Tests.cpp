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



TEST(Stream, test_stream_receive)
{
    /* Verify stream_decode() function and verify if correct
    data is received */

    typedef enum _item_ids {
        heap_counter=0x01,
        heap_size,
        heap_offset,
        packet_payload_length,
        item_descriptor,
        stream_control,
        item_desc_name=0x10,
        item_des_description,
        item_desc_shape,
        item_desc_type,
        item_desc_ID,
        item_desc_dtype,
        visibility_timestamp_count=0x6000,
        visibility_timestamp_fraction,
        visibility_baseline_count=0x6005,
        // scan_ID=0x6008,
        visibility_data=0x600A
    } item_id;

    typedef struct _item_block {
        item_id id;
        uint64_t val;
        uint64_t imm;
    } item_block;

    int num_baselines = (512 * 513) / 2;

    const item_block p_items[] = { 
	{heap_counter, 4, 1}, 
	{heap_size, 10, 1},
	{heap_offset, 55, 1}, 
	{packet_payload_length, 55, 1},
	{item_descriptor, 0, 0}, 
	{stream_control, 1, 1},
	{visibility_timestamp_count, 1, 1}, 
	{visibility_timestamp_fraction, 0, 1},
    {visibility_baseline_count, (uint64_t) num_baselines, 1},
	//{scan_ID, 100000000, 0}
    //(visibility_data, , 0)
    };
    const unsigned int num_items = sizeof(p_items) / sizeof(item_block);
    
    uint64_t heap_count;

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
    buf[7] = (unsigned char) num_items;  // Luckily < 256 items :-)

    // Construct SPEAD packet payload containing items in
    // "immediate addressing mode".
    uint64_t* items = (uint64_t*) &buf[8];
    for (unsigned int i = 0; i < num_items; i++)
    {
        const uint64_t item_id = (uint64_t) p_items[i].id;
        const uint64_t item_addr_or_val = (uint64_t) p_items[i].val;
	const uint64_t imm_or_abs = p_items[i].imm << 63;
        //printf("Item Value: %i\n", item_val[i]);
        const uint64_t item =
                imm_or_abs |
                (item_id << heap_address_bits) |
                item_addr_or_val;
        items[i] = htobe64(item);
	switch (p_items[i].id)
	{
	    case heap_counter : heap_count = p_items[i].val; break;
	}
    }

    // Create a test receiver.
    struct Receiver* receiver = create_test_receiver();
    ASSERT_TRUE(receiver != NULL);

    // Call stream_decode().
    stream_decode(receiver->streams[0], buf, 0);
    printf("Heap count - %i\n", receiver->streams[0]->heap_count); // could assert heap count value here
    printf("Buffer Len - %i\n", receiver->streams[0]->buffer_len); // could assert default values here
    printf("Num buffers - %i\n", receiver->num_buffers);
    printf("completed_streams - %i\n", receiver->completed_streams);
    printf("max_num_buffers - %i\n", receiver->max_num_buffers);
    printf("num_baselines - %i\n", receiver->num_baselines);
    // printf("buffer_id - %i\n", receiver->buffers[0]->buffer_id);
    // struct Buffer* buff = receiver->buffers[0];
    // printf("Buf %i", buff->buffer_id);

    // Clean up.
    receiver_free(receiver);
    free(buf);
}
