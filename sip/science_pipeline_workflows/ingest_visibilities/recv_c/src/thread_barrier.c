#include <pthread.h>
#include <stdlib.h>
#include "thread_barrier.h"

struct ThreadBarrier
{
    pthread_cond_t cond;
    pthread_mutex_t lock;
    unsigned int num_threads, count, iter;
};

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
