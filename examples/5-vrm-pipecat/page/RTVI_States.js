// The VRM character's movements change with the turn state, which follows Pipecat's RTVI events.
//
//   import { RTVI_States } from "./RTVI_States.js";
//   views: [vrm, RTVI_States(vrm)]     // in ConnectConversation, on the Pipecat voice mount
//
//   UserStartedSpeaking                                      -> listening
//   UserTranscript                                           -> listening, and thinking after 750 ms with no new transcript
//   UserStoppedSpeaking                                      -> thinking
//   BotStartedSpeaking, BotOutput, BotTtsText, BotTtsStarted -> speaking
//   BotStoppedSpeaking                                       -> idle
//
// The character starts idle, so nothing is sent before the first event: its first turn state, like its first phase,
// comes after the Start click, when vrm_motion.js opens the microphone.

const THINK_AFTER_SILENCE_MS = 750;
const BOT_OUTPUT = ["BotStartedSpeaking", "BotOutput", "BotTtsText", "BotTtsStarted"];

export function RTVI_States(vrm) {
  let state = "idle", silenceTimer = 0;
  const go = (s) => { if (s !== state) { state = s; vrm.turnState(s); } };
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
