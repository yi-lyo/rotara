#define INPUT_PIN   (R_PFS->PORT[1].PIN[4]) // P104 is D2
#define OUTPUT_PIN  (R_PFS->PORT[3].PIN[3]) // P303 is D9

#define PULSE_HIGH_CYCLES  400

static const uint32_t DELAYS_CYCLES[] = {
  0,
  5950,
  10228,
  13701,
  16683,
  19328,
  21725,
  23931,
  25983,
  27910,
  29731,
  31463,
  33117,
  34703,
  36229,
  37702,
  39127,
  40510,
  41853,
  43160,
  44435,
  45680,
  46898,
  48090,
  49258,
  50404,
  51530,
  52636,
  53725,
  54796,
  55852,
  56893,
  57920,
  58933,
  59934,
  60924,
  61902,
  62869,
  63826,
  64774,
  65713,
  66643,
  67565,
  68479,
  69386,
  70286,
  71179,
  72066,
  72947,
  73822,
  74691,
  75556,
  76415,
  77270,
  78120,
  78967,
  79809,
  80647,
  81482,
  82314,
  83142,
  83968,
  84790,
  85610,
  86428,
  87243,
  88057,
  88868,
  89678,
  90486,
  91292,
  92097,
  92901,
  93704,
  94506,
  95308,
  96109,
  96909,
  97710,
  98509,
  99309,
  100110,
  100910,
  101711,
  102512,
  103314,
  104118,
  104922,
  105727,
  106533,
  107341,
  108151,
  108962,
  109776,
  110591,
  111408,
  112229,
  113051,
  113877,
  114705,
  115537,
  116371,
  117210,
  118052,
  118898,
  119749,
  120604,
  121463,
  122328,
  123197,
  124072,
  124953,
  125840,
  126733,
  127633,
  128540,
  129454,
  130376,
  131306,
  132245,
  133193,
  134150,
  135117,
  136095,
  137084,
  138085,
  139099,
  140126,
  141167,
  142223,
  143294,
  144383,
  145489,
  146615,
  147761,
  148929,
  150121,
  151338,
  152584,
  153858,
  155166,
  156509,
  157891,
  159317,
  160790,
  162316,
  163902,
  165556,
  167287,
  169109,
  171036,
  173088,
  175294,
  177691,
  180336,
  183318,
  186791,
  191069,
  197019,
  218509,
};
static const uint8_t NUM_PULSES = sizeof(DELAYS_CYCLES) / sizeof(DELAYS_CYCLES[0]);

// ── DWT init ─────────────────────────────────────────────────────
// DWT_CYCCNT is a 32-bit CPU cycle counter that runs at 48 MHz.
// No peripheral setup needed; it's part of the Cortex-M4 core.
static void dwt_init() {
  // Enable the trace/debug subsystem
  CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;

  // Reset and start the cycle counter
  DWT->CYCCNT = 0;
  DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

  Serial.println("DWT cycle counter enabled.");
}

// ── Setup ────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  while (!Serial);

  dwt_init();

  OUTPUT_PIN.PmnPFS_b.PDR = 1;
  OUTPUT_PIN.PmnPFS_b.PODR = 0;

  INPUT_PIN.PmnPFS_b.PDR = 0;

  uint_fast8_t last_input = 0;
  while (1) {
    uint_fast8_t input_now = INPUT_PIN.PmnPFS_b.PIDR;

    if ((!last_input) && input_now) {
      uint32_t start = DWT->CYCCNT;
      for (uint8_t i = 0; i < NUM_PULSES; i++) {
        uint32_t pulse_high = DELAYS_CYCLES[i];
        uint32_t pulse_low = pulse_high + PULSE_HIGH_CYCLES;
        while ((DWT->CYCCNT - start) < pulse_high) {};

        OUTPUT_PIN.PmnPFS_b.PODR = 1;

        while ((DWT->CYCCNT - start) < pulse_low) {};

        OUTPUT_PIN.PmnPFS_b.PODR = 0;
      }
    }

    last_input = input_now;
  }
}

// ── Main loop ────────────────────────────────────────────────────
void loop() {

}
