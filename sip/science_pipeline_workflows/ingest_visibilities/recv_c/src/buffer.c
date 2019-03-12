#include <stdio.h>
#include <stdlib.h>
#include "buffer.h"

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
