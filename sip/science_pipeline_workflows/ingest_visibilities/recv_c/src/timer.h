#ifndef RECV_TIMER_H_
#define RECV_TIMER_H_

#ifdef __cplusplus
extern "C" {
#endif

struct Timer;

/**
 * @brief Re-initialises the timer.
 */
void tmr_clear(struct Timer* self);

/**
 * @brief Creates a new timer.
 */
struct Timer* tmr_create(void);

/**
 * @brief Returns the elapsed time on the timer.
 */
double tmr_elapsed(struct Timer* self);

/**
 * @brief Destroys the timer.
 */
void tmr_free(struct Timer* self);

/**
 * @brief Returns a timestamp.
 */
double tmr_get_timestamp(void);

/**
 * @brief Pauses the timer.
 */
void tmr_pause(struct Timer* self);

/**
 * @brief Resumes a paused timer.
 */
void tmr_resume(struct Timer* self);

/**
 * @brief Starts the timer, clearing the current elapsed time.
 */
void tmr_start(struct Timer* self);

#ifdef __cplusplus
}
#endif

#endif /* include guard */
