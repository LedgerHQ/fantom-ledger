#ifndef FANTOM_LEDGER_UI_HELPERS_H
#define FANTOM_LEDGER_UI_HELPERS_H

#include <stdint.h>
#include <stddef.h>
#include "transaction.h"

// MAX_SIMPLE_TEXT_LENGTH defines the maximal length of a text
// which can be displayed on a single screen on Ledger Nano devices.
// everything longer must be displayed as paginated text with scrolling.
#define MAX_SIMPLE_TEXT_LENGTH 18

// ui_callback_fn_t declares callback function from user interaction.
typedef void ui_callback_fn_t();

#ifdef HAVE_BAGL
// ui_callback_state_t declares states a callback pair can have.
typedef enum {
    CALLBACK_NOT_RUN,
    CALLBACK_RUN,
} ui_callback_state_t;

// ui_callback_t declares pair of callbacks for user interaction results.
// the pair covers interaction outcomes and a state; we don't want to allow
// a bug to fire both callbacks.
typedef struct {
    ui_callback_state_t state;
    ui_callback_fn_t *confirm;
    ui_callback_fn_t *reject;
} ui_callback_t;

// ui_paginated_text_state_t declares a state of paginated text displayed
// to end user for interaction and waiting for interaction. The paginated
// text is not used to let end user decide between different course of
// actions, just to confirm that they saw the text.
typedef struct {
    uint16_t guard;
    char header[30];
    char text[200];
    ui_callback_t callback;
} ui_paginated_text_state_t;

// ui_prompt_state_t declares a state of prompt asking for end user
// simple decision. We don't need any extra scrolling related stuff for this
// since the question here is short enough to fit the Ledger screen.
// This prompt type of text is used to ask end user to decide between
// two different actions. User can confirm, or reject the prompted question.
typedef struct {
    uint16_t guard;
    char header[30];
    char text[30];
    ui_callback_t callback;
} ui_prompt_state_t;

// ui_displayPaginatedText displays paginated text and waits for basic user
// interaction; we don't need user to decide a course of action
// so there is just one callback signaling that user did finish reading the text.
void ui_displayPaginatedText(
        const char *headerStr,
        const char *bodyStr,
        ui_callback_fn_t *callback);

// ui_displayPrompt displays a prompt asking and user to decide the course of action.
// The user can confirm, or reject the action and corresponding callback is fired
// to pass the decision.
void ui_displayPrompt(
        const char *headerStr,
        const char *bodyStr,
        ui_callback_fn_t *confirm,
        ui_callback_fn_t *reject
);

// ui_displayTxDetails displays transaction details to end user asking to confirm
// the transaction before being handled in any way (usually signed).
void ui_displayTxDetails(
        ui_callback_fn_t *confirm,
        ui_callback_fn_t *reject);


// ui_doDisplayPrompt implements actual change in UX flow to show the configured prompt.
void ui_doDisplayPrompt();

// ui_doDisplayPaginatedText implements actual change in UX flow to show the configured paginated text.
void ui_doDisplayPaginatedText();


// ui_callbackConfirm implements action callback for confirmed prompt.
void ui_callbackConfirm(ui_callback_t *cb);

// ui_callbackReject implements action callback for rejected prompt.
void ui_callbackReject(ui_callback_t *cb);

// ui_assertPaginatedTextGuard implements verification of the shared state
// so we know the state is set for paginated text.
void ui_assertPaginatedTextGuard();

// ui_assertPromptGuard implements verification of the shared state
// so we know the state is set for prompt.
void ui_assertPromptGuard();

// what guards we use for the shared state
enum {
    UI_STATE_GUARD_PAGINATED_TEXT = 0xF0F0,
    UI_STATE_GUARD_PROMPT = 0x0F0F,
    UI_STATE_GUARD_TX_DETAIL = 0xF1F1,
};

#endif // HAVE_BAGL

#ifdef HAVE_NBGL

// Should be updated if new transaction types require more fields.
#define MAX_FIELDS_PER_TRANSACTION 4

static inline void INCR_AND_ASSERT_PAIR_NB(uint8_t * nbPairs) {
    (*nbPairs)++;
    ASSERT(*nbPairs <= MAX_FIELDS_PER_TRANSACTION);
}

typedef struct {
    char header[30];
    char text[200];
} ui_field_pair_t;

typedef struct {
    ui_field_pair_t pairs[MAX_FIELDS_PER_TRANSACTION];
    uint8_t nbPairs;
} ui_tx_fields_t;

void ui_displayWarning(const char * warning_text, ui_callback_fn_t *confirm, ui_callback_fn_t *reject);
void ui_reviewStart(ui_callback_fn_t *confirm, ui_callback_fn_t *reject);
void ui_reviewDisplay(ui_tx_fields_t *tx_fields, ui_callback_fn_t *confirm, ui_callback_fn_t *reject, bool contract_warning);
void ui_verifyAddress(ui_tx_fields_t *tx_fields, ui_callback_fn_t *confirm, ui_callback_fn_t *reject, bool show_addr,bool show_path);
void ui_exportKeyConfirm(ui_tx_fields_t *tx_fields, ui_callback_fn_t *confirm, ui_callback_fn_t *reject);

#endif


// ui_display_state_t merges both types of "display text & wait for decision" state together
// in a single union. We never need both so we re-use the structure to save some space.
// Notice the guard is on the beginning of both structures and so will always align the same way.
typedef union {
#ifdef HAVE_BAGL
    ui_paginated_text_state_t paginatedText;
    ui_prompt_state_t prompt;
#endif
#ifdef HAVE_NBGL
    ui_tx_fields_t txFields;
#endif
} ui_display_state_t;

// displayState declares the common display state container shared between paginated text and prompt states.
// We use this trick since only one of the two may happen at any time.
extern ui_display_state_t displayState;

#ifdef HAVE_BAGL
// keep references to internal type specific states inside the shared state.
static ui_paginated_text_state_t *paginatedTextState = &(displayState.paginatedText);
static ui_prompt_state_t *promptState = &(displayState.prompt);
#endif

// ui_idle implements transaction to idle state
void ui_idle(void);

// ui_respondWithUserReject implements sending rejection response
// to host and resetting current instruction from being processed
// any further.
void ui_respondWithUserReject();

// ui_displayBusy displays busy screen notifying end user that the device
// is in the middle of processing stuff.
void ui_displayBusy();

// ui_doDisplayBusy implements actual change in UX flow to show the busy screen.
void ui_doDisplayBusy();

// ui_crash_handler implements critical UI failure handling.
// We don't deal with crashes on UI, we reset the device in that case.
// seproxyhal may be locked in an unreachable state anyway.
static inline void ui_crash_handler() {
    #ifdef RESET_ON_CRASH
    io_seproxyhal_se_reset();
    #endif
}

// TRY_CATCH_UI implements convenience macro for capturing exceptions on UI
// interactions.
#define TRY_CATCH_UI(ui_call) \
    BEGIN_TRY { \
        TRY { \
            ui_call; \
        } \
        CATCH(EXCEPTION_IO_RESET) \
        { \
            THROW(EXCEPTION_IO_RESET); \
        } \
        CATCH_OTHER(e) \
        { \
            ui_crash_handler(); \
        } \
        FINALLY { \
        } \
    } \
    END_TRY;

#endif //FANTOM_LEDGER_UI_HELPERS_H
