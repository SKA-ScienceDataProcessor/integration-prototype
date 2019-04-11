#include <pthread.h>
#include <stdlib.h>
#include "thread_pool.h"

static void* threadpool_thread(void* arg);

struct ThreadTask
{
    void *(*thread_func)(void*);
    void* arg;
    struct ThreadTask* next;
};

struct ThreadPool
{
    pthread_mutex_t lock;
    pthread_cond_t cond;
    pthread_t* threads;
    struct ThreadTask *task_list, *last_task;
    int do_abort, num_threads, num_tasks;
};

struct ThreadPool* threadpool_create(int num_threads)
{
    struct ThreadPool* cls =
            (struct ThreadPool*) calloc(1, sizeof(struct ThreadPool));
    pthread_mutex_init(&cls->lock, 0);
    pthread_cond_init(&cls->cond, 0);
    cls->threads = (pthread_t*) malloc(num_threads * sizeof(pthread_t));
    cls->num_threads = num_threads;
    for (int i = 0; i < num_threads; ++i)
        pthread_create(&cls->threads[i], 0, &threadpool_thread, cls);
    return cls;
}

void threadpool_enqueue(struct ThreadPool* self,
        void *(*thread_func)(void*), void *arg)
{
    if (!self) return;
    struct ThreadTask* task =
            (struct ThreadTask*) malloc(sizeof(struct ThreadTask));
    task->thread_func = thread_func;
    task->arg = arg;
    task->next = 0;
    pthread_mutex_lock(&self->lock);
    if (self->last_task) self->last_task->next = task;
    if (!self->task_list) self->task_list = task;
    self->last_task = task;
    self->num_tasks++;
    pthread_cond_signal(&self->cond);
    pthread_mutex_unlock(&self->lock);
}

void threadpool_free(struct ThreadPool* self)
{
    if (!self) return;
    self->do_abort = 1;
    pthread_mutex_lock(&self->lock);
    pthread_cond_broadcast(&self->cond);
    pthread_mutex_unlock(&self->lock);
    for (int i = 0; i < self->num_threads; i++)
        pthread_join(self->threads[i], 0);
    while (self->task_list)
    {
        struct ThreadTask* task = self->task_list;
        self->task_list = task->next;
        free(task);
    }
    free(self->threads);
    free(self);
}

static void* threadpool_thread(void* arg)
{
    struct ThreadPool* pool = (struct ThreadPool*)arg;
    while (!pool->do_abort)
    {
        pthread_mutex_lock(&pool->lock);
        while (!pool->do_abort && !pool->task_list)
            pthread_cond_wait(&pool->cond, &pool->lock);
        if (pool->do_abort)
        {
            pthread_mutex_unlock(&pool->lock);
            return 0;
        }
        struct ThreadTask* task = pool->task_list;
        pool->task_list = task->next;
        pool->num_tasks--;
        if (task == pool->last_task) pool->last_task = 0;
        pthread_mutex_unlock(&pool->lock);
        task->thread_func(task->arg);
        free(task);
        pthread_mutex_lock(&pool->lock);
        pthread_cond_broadcast(&pool->cond);
        pthread_mutex_unlock(&pool->lock);
    }
    return 0;
}
