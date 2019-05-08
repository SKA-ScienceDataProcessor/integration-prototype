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


TEST(Stream, test_stream_receive)
{
    /* Verify stream_decode() function and verify if correct
    data is received */
    typedef enum _item_ids {
        heap_counter=0x01,
        heap_size,
        heap_offset,
        packet_payload_length,
        visibility_baseline_count=0x6005,
        scan_ID=0x6008,
        visibility_data=0x600A
    } item_id;

    typedef struct _item_block {
        item_id id;
        uint64_t val;
        uint64_t imm;
    } item_block;

    int num_baselines = 512 *513 / 2;
    struct  DataType vis_data = {0,0,{{1.5,2.5},{3.5,4.5},{5.5,6.5},{7.5,8.5}}};
    uint64_t scan_id=0, *scan_ptr=NULL;
    void *heap_start;
    struct DataType * vis_ptr;
    size_t heap_sz = 8 + sizeof(vis_data);

    const item_block p_items[] = { 
	{heap_counter, 2, 1}, 
	{heap_size, (uint64_t) heap_sz, 1},
	{heap_offset, 0, 1}, 
	{packet_payload_length, (uint64_t) heap_sz, 1},
	{visibility_baseline_count, (uint64_t) htobe32((uint32_t)num_baselines), 1},
	{scan_ID, 0, 0},
	{visibility_data, 8, 0}
    };
    
    const unsigned int num_items = sizeof(p_items) / sizeof(item_block);

    // Allocate memory for a SPEAD packet.
    unsigned char* buf = (unsigned char*) malloc(8 + num_items * 8 + heap_sz);
    ASSERT_NE(buf, nullptr);

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
        const uint64_t item_id = (uint64_t) p_items[i].id;
        const uint64_t item_addr_or_val = (uint64_t) p_items[i].val;
        const uint64_t imm_or_abs = p_items[i].imm << 63;
        const uint64_t item =
                imm_or_abs |
                (item_id << heap_address_bits) |
                item_addr_or_val;
        items[i] = htobe64(item);
	/* APM - the following is for picking up any values we may wish
	 * to use for testing later. Place a star-slash at
	 * the end of this line to include the below code. 
	switch (p_items[i].id)
	{
	    // heap_count will need to be defined.
	    case heap_counter : heap_count = p_items[i].val; break;
	} /* */
    }

    // get start of heap
    heap_start = (void *)&items[num_items];

    // insert scan_id at heap_start, 8 bytes
    scan_ptr = (uint64_t *) heap_start;
    // APM - Should it be this:
    *scan_ptr = scan_id;
    // ... or this?
    // *scan_ptr = htobe64(scan_id);
    vis_ptr = (struct DataType *) (scan_ptr+1);
    memcpy((void *)vis_ptr, (void *) &vis_data, sizeof(vis_data));

    // Create a test receiver.
    struct Receiver* receiver = create_test_receiver();
    ASSERT_NE(receiver, nullptr);

    // Passing the buffer and stream to stream decode
    stream_decode(receiver->streams[0], buf, 0);

    // Testing
    ASSERT_NE(receiver->streams[0], nullptr);
    ASSERT_NE(receiver->buffers[0], nullptr);
    ASSERT_NE(receiver->num_buffers, 0);
    EXPECT_EQ(num_baselines, receiver->buffers[0]->num_baselines);
    EXPECT_EQ(vis_ptr->fd, receiver->buffers[0]->vis_data->fd);
    EXPECT_EQ(vis_ptr->tci, receiver->buffers[0]->vis_data->tci);

    // Clean up.
    receiver_free(receiver);
    free(buf);
}
