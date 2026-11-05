// Pipecat's Plasma changes its look with the turn state, which follows Pipecat's RTVI events.
//
//   import { RTVI_States } from "./RTVI_States.js";
//   views: [plasma, RTVI_States(plasma)]     // in ConnectConversation, on the Pipecat voice mount
//
//   UserStartedSpeaking                                      -> listening
//   UserTranscript                                           -> listening, and thinking after 750 ms with no new transcript
//   UserStoppedSpeaking                                      -> thinking
//   BotStartedSpeaking, BotOutput, BotTtsText, BotTtsStarted -> speaking
//   BotStoppedSpeaking                                       -> idle

import { PLASMA_TURN_STATES } from "./pipecat_plasma.js";

const THINK_AFTER_SILENCE_MS = 750;
const BOT_OUTPUT = ["BotStartedSpeaking", "BotOutput", "BotTtsText", "BotTtsStarted"];

export function RTVI_States(plasma) {
  let state = null, silenceTimer = 0;
  const go = (s) => { if (s !== state) { state = s; plasma.update(PLASMA_TURN_STATES[s]); } };
  go("idle");
  return {
    rtvi(name) {
      if (name === "UserStartedSpeaking") { clearTimeout(silenceTimer); go("listening"); }
      else if (name === "UserTranscript") { go("listening"); clearTimeout(silenceTimer); silenceTimer = setTimeout(() => go("thinking"), THINK_AFTER_SILENCE_MS); }
      else if (name === "UserStoppedSpeaking") { clearTimeout(silenceTimer); go("thinking"); }
      else if (BOT_OUTPUT.includes(name)) { clearTimeout(silenceTimer); go("speaking"); }
      else if (name === "BotStoppedSpeaking") go("idle");
    },
  };
}
