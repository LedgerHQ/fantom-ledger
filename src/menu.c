#include <os_io_seproxyhal.h>
#include <ux.h>
#include "menu.h"
#include "get_version.h"
#include "glyphs.h"
#include "state.h"

#ifdef HAVE_NBGL
#include "os.h"
#include "nbgl_page.h"
#include "nbgl_use_case.h"
#endif

#ifdef HAVE_BAGL
// ux_idle_flow declares the UI flow for idle state
extern const ux_flow_step_t* const ux_idle_flow [];

// ITEMS macro is used for pure formatting purpose.
#define ITEMS(...) { __VA_ARGS__ }

// UX_STEP_NOCB is a macro for simple flow step, given its name, layout and content.
// ux_idle_main is the main idle screen.
// The layout contains Fantom logo and two lines of normal text (pnn layout).
// See SDK /lib_ux/include/ux_flow_engine for details about macros,
// see /lib_ux/include/ux_layouts.h for layouts.
UX_STEP_NOCB(
        ux_idle_main,
        pnn,
        ITEMS (
            &C_fantom_logo,
            "Fantom FTM",
            "Ready ..."
        )
);

// ux_idle_version is the version information screen.
// Layout contains two lines, normal text and bold text (bn layout).
UX_STEP_NOCB(
        ux_idle_version,
        bn,
        ITEMS(
            "Version",
            APPVERSION,
        )
);

// UX_STEP_CB is a macro for a simple flow step with a validation callback.
// ux_idle_quit is the app termination screen.
// Layout contains an icon and single line of bold text (pb layout).
UX_STEP_CB(
        ux_idle_quit,
        pb,
        os_sched_exit(-1),
        ITEMS(
            &C_icon_dashboard_x,
            "Quit"
        )
);

// ux_idle_flow defines the idle menu flow, uses steps defined above.
UX_FLOW(
        ux_idle_flow,
        &ux_idle_main,
        &ux_idle_version,
        &ux_idle_quit,
        FLOW_LOOP
);
#endif

#ifdef HAVE_NBGL
#define NB_INFO_FIELDS 2
static const char* const infoTypes[] = {"Version", "Fantom App"};
static const char* const infoContents[] = {APPVERSION, "(c) 2022 Ledger"};

static void displayInfoMenu(void);
static bool infoNavCallback(uint8_t page, nbgl_pageContent_t *content);

void onQuitCallback(void)
{
    os_sched_exit(-1);
}

static bool infoNavCallback(uint8_t page, nbgl_pageContent_t *content) {
  if (page == 0) {
    content->type = INFOS_LIST;
    content->infosList.nbInfos = NB_INFO_FIELDS;
    content->infosList.infoTypes = (const char**) infoTypes;
    content->infosList.infoContents = (const char**) infoContents;    
  }
  else {
    return false;
  }
  return true;
}

static void displayInfoMenu(void) {
    nbgl_useCaseSettings("Fantom infos",0,1,true,ui_idle,infoNavCallback,NULL);
}
#endif // HAVE_NBGL

// ui_idle displays the main menu. Note that your app isn't required to use a
// menu as its idle screen; you can define your own completely custom screen.
void ui_idle(void) {
    // no instruction is being processed; the last one called idle
    currentIns = INS_NONE;

    // we support Nano S/S+, Nano X and Stax devices.
#if defined(TARGET_NANOS) || defined(TARGET_NANOX) || defined(TARGET_NANOS2)
    // reserve a display stack slot if none yet
    if(G_ux.stack_count == 0) {
        ux_stack_push();
    }

    // initiate the idle flow
    ux_flow_init(0, ux_idle_flow, NULL);
#elif defined(TARGET_STAX)
    nbgl_useCaseHome("Fantom",&C_fantom_logo_64px, "This app confirms actions on\nthe Fantom network.", false, displayInfoMenu, onQuitCallback);
#else
    // unknown device?
    STATIC_ASSERT(false, "unknown target device");
#endif
}