const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

const controls = {
  calls: document.querySelector("#calls"),
  aht: document.querySelector("#aht"),
  labour: document.querySelector("#labour"),
  containment: document.querySelector("#containment"),
  platform: document.querySelector("#platform"),
  implementation: document.querySelector("#implementation"),
};

function updateBusinessCase() {
  const calls = Number(controls.calls.value);
  const aht = Number(controls.aht.value);
  const labour = Number(controls.labour.value);
  const containment = Number(controls.containment.value) / 100;
  const platform = Number(controls.platform.value);
  const implementation = Number(controls.implementation.value);
  const minutes = calls * aht;
  const current = minutes / 60 * labour;
  const projected = minutes * platform + current * (1 - containment);
  const monthlyBenefit = current - projected;
  const payback = monthlyBenefit > 0 ? implementation / monthlyBenefit : null;

  document.querySelector("#calls-value").textContent = calls.toLocaleString("en-US");
  document.querySelector("#aht-value").textContent = `${aht.toFixed(1)} min`;
  document.querySelector("#labour-value").textContent = money.format(labour);
  document.querySelector("#containment-value").textContent = `${Math.round(containment * 100)}%`;
  document.querySelector("#platform-value").textContent = `$${platform.toFixed(2)}/min`;
  document.querySelector("#implementation-value").textContent = money.format(implementation);
  document.querySelector("#current-cost").textContent = money.format(current);
  document.querySelector("#projected-cost").textContent = money.format(projected);
  document.querySelector("#annual-benefit").textContent = money.format(monthlyBenefit * 12);
  document.querySelector("#payback").textContent = payback ? `${payback.toFixed(1)} mo` : "No payback";

  const recommendation = document.querySelector("#recommendation");
  const note = document.querySelector("#recommendation-note");
  if (monthlyBenefit <= 0) {
    recommendation.textContent = "Return to discovery";
    note.textContent = "The modelled workflow does not yet create a positive operating case.";
  } else if (payback > 24) {
    recommendation.textContent = "Narrow the pilot";
    note.textContent = "Validate a higher-value cohort before committing to a broad rollout.";
  } else {
    recommendation.textContent = "Shadow mode";
    note.textContent = "Validate real call patterns without customer exposure.";
  }
}

Object.values(controls).forEach((control) => control.addEventListener("input", updateBusinessCase));
updateBusinessCase();

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((candidate) => {
      candidate.classList.toggle("is-active", candidate === tab);
      candidate.setAttribute("aria-selected", String(candidate === tab));
    });
    document.querySelectorAll(".tab-panel").forEach((panel) => {
      const selected = panel.id === tab.dataset.tab;
      panel.classList.toggle("is-active", selected);
      panel.hidden = !selected;
    });
  });
});

const scenarios = {
  success: {
    outcome: "Appointment booked and confirmed",
    path: "Contained",
    latency: 1940,
    explanation: "The agent checks policy before acting, reads customer context, and confirms the appointment only after the calendar write succeeds. Outcome telemetry closes the loop.",
    transcript: [
      ["Caller", "I need my car serviced tomorrow."],
      ["Agent", "I found two verified service slots. Would 10:30 work?"],
      ["Caller", "Yes."],
      ["Agent", "Your appointment is confirmed. I will send the details now."],
    ],
    events: [
      ["Telephony", 0, 160, "Receive audio frame", "ok"],
      ["Speech-to-text", 160, 340, "Transcribe caller", "ok"],
      ["Policy", 500, 90, "Consent + intent", "ok"],
      ["Orchestrator", 590, 420, "Select action", "ok"],
      ["CRM", 1010, 280, "Read context", "ok"],
      ["Calendar", 1290, 310, "Reserve slot", "ok"],
      ["Text-to-speech", 1600, 260, "Stream confirmation", "ok"],
      ["Events", 1860, 80, "Emit telemetry", "ok"],
    ],
  },
  "crm-down": {
    outcome: "Callback captured; no slot invented",
    path: "Degraded mode",
    latency: 1690,
    explanation: "The CRM request times out. The agent does not guess availability or promise an appointment; it switches to the approved callback path and emits a dependency-degraded event.",
    transcript: [
      ["Agent", "The booking system is temporarily unavailable."],
      ["Agent", "I can arrange a callback rather than promise an unconfirmed slot."],
    ],
    events: [
      ["Telephony", 0, 160, "Receive audio frame", "ok"],
      ["Speech-to-text", 160, 340, "Transcribe caller", "ok"],
      ["Policy", 500, 90, "Consent + intent", "ok"],
      ["Orchestrator", 590, 420, "Select action", "ok"],
      ["CRM", 1010, 500, "Read slots", "error"],
      ["Fallback", 1510, 180, "Create callback", "warning"],
    ],
  },
  human: {
    outcome: "Warm transfer completed",
    path: "Human handoff",
    latency: 1250,
    explanation: "A request for a person is honoured immediately. The handoff includes intent and consent context so the customer does not need to repeat the conversation.",
    transcript: [
      ["Caller", "I would like to speak to a service adviser."],
      ["Agent", "Certainly. I will transfer you and pass along the reason for your call."],
    ],
    events: [
      ["Telephony", 0, 160, "Receive audio frame", "ok"],
      ["Speech-to-text", 160, 340, "Transcribe caller", "ok"],
      ["Policy", 500, 90, "Human request", "ok"],
      ["Orchestrator", 590, 420, "Package context", "ok"],
      ["Handoff", 1010, 240, "Warm transfer", "warning"],
    ],
  },
  "no-consent": {
    outcome: "Stopped before personal-data processing",
    path: "Policy escalation",
    latency: 1220,
    explanation: "Without consent, the workflow stops before CRM access. The system moves to a human route governed by the approved operating policy.",
    transcript: [
      ["Agent", "May I process your details to arrange service?"],
      ["Caller", "No."],
      ["Agent", "Understood. I will connect you to a colleague."],
    ],
    events: [
      ["Telephony", 0, 160, "Receive audio frame", "ok"],
      ["Speech-to-text", 160, 340, "Transcribe caller", "ok"],
      ["Policy", 500, 90, "Consent check", "error"],
      ["Orchestrator", 590, 420, "Block tool access", "warning"],
      ["Handoff", 1010, 210, "Transfer to human", "warning"],
    ],
  },
};

function runScenario() {
  const scenario = scenarios[document.querySelector("#scenario").value];
  const timeline = document.querySelector("#runtime-timeline");
  const maxTime = 2000;
  timeline.innerHTML = scenario.events.map(([component, offset, duration, action, status]) => `
    <div class="runtime-row">
      <div class="runtime-label"><strong>${component}</strong><span>${action}</span></div>
      <div class="runtime-track">
        <div class="runtime-bar ${status === "error" ? "is-error" : status === "warning" ? "is-warning" : ""}"
             style="--left:${offset / maxTime * 100}%;--width:${duration / maxTime * 100}%"
             aria-label="${component}: ${action}, starts ${offset} milliseconds, lasts ${duration} milliseconds">
          ${duration}ms
        </div>
      </div>
    </div>`).join("");

  document.querySelector("#runtime-outcome").textContent = scenario.outcome;
  document.querySelector("#runtime-path").textContent = scenario.path;
  document.querySelector("#runtime-latency").textContent = `${scenario.latency.toLocaleString("en-US")} ms`;
  document.querySelector("#runtime-explanation").textContent = scenario.explanation;
  document.querySelector("#transcript").innerHTML = scenario.transcript.map(([speaker, line]) => `<p><strong>${speaker}:</strong> ${line}</p>`).join("");

  document.querySelectorAll(".runtime-bar").forEach((bar, index) => {
    window.setTimeout(() => bar.classList.add("is-active"), index * 140);
  });
}

document.querySelector("#run-call").addEventListener("click", runScenario);
runScenario();
