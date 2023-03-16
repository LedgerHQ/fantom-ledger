#ifdef HAVE_NBGL
#include <stdbool.h>
#include <sys/types.h>
#include <string.h>
#include <stdint.h>
#include <ux.h>
#include "ui_helpers.h"
#include "glyphs.h"
#include "nbgl_use_case.h"
#include "menu.h"

// Globals
static ui_callback_fn_t *confirm_clbk;
static ui_callback_fn_t *reject_clbk;
static char *rejection_text;
static nbgl_layoutTagValueList_t pairList;
static nbgl_layoutTagValue_t fields[MAX_FIELDS_PER_TRANSACTION];
static nbgl_pageInfoLongPress_t infoLongPress;
static bool isDisplayAddress;
static bool isDisplayPath;

// Static functions declarations
static void rejectChoice(void);
static void displayTransaction(void);
static void rejectAndDisplayIdleMenu(void);
static void displayAddress(void);

// Static functions definitions
static void warningChoice(bool accept) {
    if (accept) {
        confirm_clbk();
    } else {
        rejectAndDisplayIdleMenu();
    }
}

static void contractWarningChoice(bool accept) {
    if (accept) {
        displayTransaction();
    } else {
        rejectAndDisplayIdleMenu();
    }
}

static void reviewChoice(bool confirm) {
    if (confirm) {
        confirm_clbk();
        nbgl_useCaseStatus("TRANSACTION\nCONFIRMED", true, ui_idle);
    } else {
        rejectChoice();
    }
}

static void rejectConfirmation(void) {
    rejectAndDisplayIdleMenu();
}

static void rejectChoice(void) {
    nbgl_useCaseConfirm("Reject transaction?",
                        NULL,
                        "Yes, cancel",
                        "Go back to transaction",
                        rejectConfirmation);
}

static void rejectAndDisplayIdleMenu(void) {
    reject_clbk();
    nbgl_useCaseStatus(rejection_text, false, ui_idle);
}

static void displayTransaction(void) {
    nbgl_useCaseStaticReview(&pairList, &infoLongPress, "Reject", reviewChoice);
}

static void displayAddressCallback(bool confirm) {
    if (confirm) {
        confirm_clbk();
        nbgl_useCaseStatus("ADDRESS\nVERIFIED", true, ui_idle);
    } else {
        rejectAndDisplayIdleMenu();
    }
}

static void displayAddress(void) {
    if (isDisplayAddress) {
        if (isDisplayPath) {
            nbgl_useCaseAddressConfirmationExt(fields[1].value, &displayAddressCallback, &pairList);
        } else {
            nbgl_useCaseAddressConfirmation(fields[1].value, &displayAddressCallback);
        }
    } else {
        memset(&infoLongPress, 0, sizeof(infoLongPress));
        infoLongPress.text = "Confirm address ?";
        infoLongPress.longPressText = "Confirm";
        infoLongPress.icon = &C_fantom_logo_64px;
        nbgl_useCaseStaticReviewLight(&pairList, &infoLongPress, "Cancel", &displayAddressCallback);
    }
}

static void displayPathCallback(bool confirm) {
    if (confirm) {
        confirm_clbk();
        nbgl_useCaseStatus("PUBLIC KEY\nEXPORTED", true, ui_idle);
    } else {
        rejectAndDisplayIdleMenu();
    }
}

// Public functions definitions
void ui_doDisplayBusy() {
    nbgl_useCaseSpinner("Loading transaction");
}

void ui_reviewDisplay(ui_tx_fields_t *tx_fields,
                      ui_callback_fn_t *confirm,
                      ui_callback_fn_t *reject,
                      bool contract_warning) {
    ASSERT(io_state == IO_EXPECT_NONE || io_state == IO_EXPECT_UI);
    memset(&pairList, 0, sizeof(pairList));
    memset(&infoLongPress, 0, sizeof(infoLongPress));
    memset(&fields, 0, sizeof(fields));

    confirm_clbk = confirm;
    reject_clbk = reject;

    infoLongPress.text = "Send Transaction ?";
    infoLongPress.longPressText = "Hold to confirm";
    infoLongPress.icon = &C_fantom_logo_64px;

    for (int i = 0; i < tx_fields->nbPairs; i++) {
        fields[i].item = tx_fields->pairs[i].header;
        fields[i].value = tx_fields->pairs[i].text;
    }

    pairList.pairs = (nbgl_layoutTagValue_t *) fields;
    pairList.nbPairs = tx_fields->nbPairs;

    if (contract_warning) {
        nbgl_useCaseChoice(&C_round_warning_64px,
                           "Contract call",
                           "Review carefully",
                           "Continue",
                           "Reject",
                           contractWarningChoice);
    } else {
        displayTransaction();
    }
}

void ui_displayWarning(const char *warning_text,
                       ui_callback_fn_t *confirm,
                       ui_callback_fn_t *reject) {
    ASSERT(io_state == IO_EXPECT_NONE || io_state == IO_EXPECT_UI);
    confirm_clbk = confirm;
    reject_clbk = reject;
    nbgl_useCaseChoice(&C_round_warning_64px,
                       (char *) warning_text,
                       "Reject if you're not sure",
                       "Continue",
                       "Reject",
                       warningChoice);
}

void ui_reviewStart(ui_callback_fn_t *confirm, ui_callback_fn_t *reject) {
    ASSERT(io_state == IO_EXPECT_NONE || io_state == IO_EXPECT_UI);
    confirm_clbk = confirm;
    reject_clbk = reject;
    rejection_text = "Transaction rejected";
    nbgl_useCaseReviewStart(&C_fantom_logo_64px,
                            "Review\ntransaction",
                            NULL,
                            "Reject",
                            confirm,
                            rejectChoice);
}

void ui_verifyAddress(ui_tx_fields_t *tx_fields,
                      ui_callback_fn_t *confirm,
                      ui_callback_fn_t *reject,
                      bool show_addr,
                      bool show_path) {
    ASSERT(io_state == IO_EXPECT_NONE || io_state == IO_EXPECT_UI);
    memset(&pairList, 0, sizeof(pairList));
    memset(&fields, 0, sizeof(fields));

    confirm_clbk = confirm;
    reject_clbk = reject;
    rejection_text = "Address rejected";

    // Derivation path
    fields[0].item = tx_fields->pairs[0].header;
    fields[0].value = tx_fields->pairs[0].text;
    // Address
    fields[1].item = NULL;
    fields[1].value = tx_fields->pairs[1].text;

    pairList.pairs = (nbgl_layoutTagValue_t *) fields;
    // Use only the second field (derivation path).
    // The first field is passed manually as nbgl_useCaseAddressConfirmationExt's
    // first parameter in displayAddress.
    pairList.nbPairs = 1;
    // This bool will condition which NBGL use case function is called for address
    // verification in displayAddress.
    isDisplayAddress = show_addr;
    isDisplayPath = show_path;

    nbgl_useCaseReviewStart(&C_fantom_logo_64px,
                            "Verify \naddress",
                            NULL,
                            "Cancel",
                            displayAddress,
                            rejectAndDisplayIdleMenu);
}

void ui_exportKeyConfirm(ui_tx_fields_t *tx_fields,
                         ui_callback_fn_t *confirm,
                         ui_callback_fn_t *reject) {
    ASSERT(io_state == IO_EXPECT_NONE || io_state == IO_EXPECT_UI);

    confirm_clbk = confirm;
    reject_clbk = reject;
    rejection_text = "Key export cancelled";

    // Copy derivation path
    char subtext[40];
    snprintf(subtext,
             sizeof(subtext),
             "%s\n%s",
             tx_fields->pairs[0].header,
             tx_fields->pairs[0].text);

    nbgl_useCaseChoice(&C_fantom_logo_64px,
                       "Export public key ?",
                       subtext,
                       "Confirm",
                       "Cancel",
                       displayPathCallback);
}
#endif  //  HAVE_NBGL
