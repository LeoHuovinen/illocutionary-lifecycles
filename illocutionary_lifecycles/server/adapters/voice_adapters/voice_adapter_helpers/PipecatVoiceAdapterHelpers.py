"""The assembler, ``UserSpeechTurnAggregationAssembler``, which joins one user's final transcriptions from the STT into
turns and sets when each turn goes to the session through the voice adapter, for every speech source.

This repository runs conversations through authored illocutionary states (named for speech act theory, where an
utterance's force is what it does, such as asking or answering), with analyzers (separate calls with their own prompts
over the latest utterance), not the reply itself, updating the pragmatic state (what the dialogue has established so
far, from which the next prompt is composed), and when the user speaks rather than types, something must set where one
turn ends before the folder ``core`` can process it, check it with ``analyzers`` and record it in ``memory``. This
class, in the folder ``server`` beside the voice adapter, is that speech side of turn taking, and
``illocutionary_lifecycles.core.turn_taking`` only processes the finished turn. The class imports nothing from
Pipecat. Both speech mounts build one assembler per
connection, ``PipecatVoiceAdapterWebRtcMount``, whose pipeline relays the STT's frames to it, and
``PressToSpeakAdapterWebsocketMount``, which feeds it from Azure Speech with no Pipecat. A mount passes it interim
transcriptions, final transcriptions, typed text, speech start and stop, and the start of reply playback.

The rules apply in this order. Final transcriptions separated by pauses shorter than ``debounce_s`` belong to one turn,
and when the pause has passed the turn goes to the session. Once a turn has gone to the session, no further turn goes
until its reply has started playing, and the assembler's marks call this the gate going down and up. Speech heard in
that interval was said before the user heard the reply, so it is held back and joins the next turn as its first part,
followed by the text of ``PRE_POST_MARKER``, or is dropped if the user says nothing more, which is an accepted cost. A
turn that has passed its checks and gone to the session is never cancelled by speech that starts later, because the
timer's reference is dropped before the turn is sent. A turn whose reply is empty lets turns go again at once, and a
reply that never starts playing lets them go after ``gate_failsafe_s``. Typed text on a speech way arrives through
``segment`` like a final transcription and joins the spoken turn, and is never a turn of its own.

Two conditions are detected, and both are counts or flags over what the mount passed in, never what was said. The
condition ``AggregateInterimCountExceededConfiguredThreshold`` holds once the speech collected for the next turn has
had ``unyielding_speech_interim_threshold`` interim and final transcriptions, 20 by default, and ends when the turn goes
to the session. The condition ``TranscriptOrVadActiveAtReplyPlaybackStart`` holds when a reply started playing while
the user was speaking, with the reason "double-talk", or while collected speech was waiting, with the reason
"pre-hearing", ends the next time a reply starts with neither, and takes precedence over the first. Each change of
condition goes to the ``marker`` callable at once and, with the next speech passed to the session, under the key
``user_speech_turn_aggregation_interim_threshold_or_playback_overlap_transition``.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable


class UserSpeechTurnAggregationAssembler:
    """The assembler of one connection's spoken turns, built by a speech mount with that connection's voice adapter, as
    the module docstring above explains.

    ``voice`` is the session's ``PipecatVoiceAdapter``, whose ``incremental_phrase_tick`` receives the speech so far on
    every interim and final transcription and whose ``on_user_turn`` receives every turn. ``on_reply`` is an async
    callable that receives each non-empty reply, which the mount then speaks by TTS. ``debounce_s`` is the pause in
    seconds that ends a turn, 2.5 by default, which the press mount sets to 0.3, and a shorter pause splits one hesitant
    utterance into several turns. ``gate_failsafe_s`` is the longest wait in seconds, 20.0 by default, for a reply to
    start playing before turns go again. ``marker`` is an optional callable taking three strings, the source, the mark's
    name and a text, that receives what the assembler does for logging, and nothing is logged without it.
    ``unyielding_speech_interim_threshold`` is the count that raises the first detected condition, 20 by default, and
    ``None`` turns off both conditions. ``churns`` counts the turns handed to the session.
    """

    PRE_POST_MARKER = ("[above is what user said before they heard the question, "
                       "below is what user said after they heard the question:]")

    def __init__(self, voice: Any, on_reply: Callable[[str], Awaitable[None]],
                 debounce_s: float = 2.5,
                 gate_failsafe_s: float = 20.0,
                 marker: Callable[[str, str, str], None] | None = None,
                 unyielding_speech_interim_threshold: int | None = 20) -> None:
        """Keep the arguments the class docstring above describes and start with nothing collected and turns free to go."""
        self._voice = voice
        self._on_reply = on_reply
        self._debounce_s = float(debounce_s)
        self._gate_failsafe_s = float(gate_failsafe_s)
        self._marker = marker
        self._unyielding_speech_interim_threshold = unyielding_speech_interim_threshold
        self._segments: list[str] = []
        # Speech collected before the reply started playing.
        self._pre_segments: list[str] = []
        self._speaking = False
        self._interim_after_final = False
        self._timer: asyncio.Task | None = None
        self._settling = False
        # Time the last turn went to the session. None once its reply has started playing.
        self._gate_down_since: float | None = None
        self.churns = 0
        self._aggregate_interim_count = 0
        self._interim_threshold_or_playback_overlap_state: str | None = None
        self._interim_threshold_or_playback_overlap_record: dict | None = None

    def interim(self, InterimTranscriptionText: str) -> None:
        """Take ``InterimTranscriptionText``, the STT's provisional text of the speech in progress, pass the speech so
        far to the voice adapter's ``incremental_phrase_tick``, note that a final transcription is still to come so no
        turn ends yet, and return ``None``, ignoring empty text. Called by both speech mounts for every interim
        transcription, under the rules the module docstring above gives."""
        InterimTranscriptionText = (InterimTranscriptionText or "").strip()
        if not InterimTranscriptionText:
            return
        self._interim_after_final = True
        self._RelayIncrementalInterimBundle(InterimTranscriptionText)
        self._rearm()

    def segment(self, FinalTranscriptionText: str) -> None:
        """Add ``FinalTranscriptionText``, the STT's settled text of one stretch of speech or a line the user typed on a
        speech way, to the speech collected for the next turn, pass the speech so far to ``incremental_phrase_tick``,
        start the pause that may end the turn, and return ``None``, ignoring empty text. Called by both speech mounts for
        every final transcription and every typed line, under the rules the module docstring above gives."""
        FinalTranscriptionText = (FinalTranscriptionText or "").strip()
        if not FinalTranscriptionText:
            return
        self._segments.append(FinalTranscriptionText)
        self._interim_after_final = False
        self._RelayIncrementalInterimBundle("")
        self._rearm()

    def speech_started(self) -> None:
        """Note that the user started speaking and cancel the pause that would end the turn, and return ``None``. A turn
        already sent is not affected, as the module docstring above explains."""
        self._speaking = True
        self._cancel_timer()

    def speech_stopped(self) -> None:
        """Note that the user stopped speaking and start the pause that may end the turn, and return ``None``, under the
        rules the module docstring above gives."""
        self._speaking = False
        self._rearm()

    def TTSStarted(self) -> None:
        """Note that a reply started playing, let turns go again, set or end the playback-overlap condition, move every
        piece of speech collected so far aside to be held back for the next turn, and return ``None``. Called by both
        speech mounts when TTS audio of a reply begins to play, under the rules the module docstring above gives."""
        if self._gate_down_since is not None:
            held = time.monotonic() - self._gate_down_since
            self._gate_down_since = None
            self._mark("UserSpeechTurnAggregationAssembler", "GateUp",
                       f"held {held * 1000:.0f} ms")
        # Checked before the collected speech is moved aside below, so the check sees it.
        overlap_reason = ("double-talk" if self._speaking
                          else ("pre-hearing" if self._segments else None))
        if (overlap_reason is not None
                and self._unyielding_speech_interim_threshold is not None):
            self._LatchInterimThresholdOrPlaybackOverlapState(
                "TranscriptOrVadActiveAtReplyPlaybackStart", overlap_reason)
        elif (self._interim_threshold_or_playback_overlap_state
                == "TranscriptOrVadActiveAtReplyPlaybackStart"):
            self._ResolveInterimThresholdOrPlaybackOverlapState()
        # Everything collected so far was said before the user heard the reply.
        if self._segments:
            self._pre_segments.extend(self._segments)
            self._segments = []
            self._mark("UserSpeechTurnAggregationAssembler", "PreHearingHold",
                       " ".join(self._pre_segments))
        self._rearm()

    def _mark(self, tap: str, frame: str, text: str = "") -> None:
        """Call the ``marker`` callable with ``tap``, ``frame`` and ``text``, ignoring any exception it raises, or do
        nothing without one. Called by the methods of this class for every mark."""
        if self._marker is None:
            return
        try:
            self._marker(tap, frame, text)
        except Exception:
            pass

    def _LatchInterimThresholdOrPlaybackOverlapState(self, state: str,
                                                      reason: str) -> None:
        """Set ``state`` as the current detected condition with ``reason``, mark it, and keep a record of the change to
        send with the next speech, and return ``None``. Setting the condition already current does nothing, and the
        count condition never replaces the playback-overlap condition. The two conditions are described in the module
        docstring above."""
        if self._interim_threshold_or_playback_overlap_state == state:
            return
        if (state == "AggregateInterimCountExceededConfiguredThreshold"
                and self._interim_threshold_or_playback_overlap_state
                == "TranscriptOrVadActiveAtReplyPlaybackStart"):
            return
        self._interim_threshold_or_playback_overlap_state = state
        detail = f"reason={reason} interim_count={self._aggregate_interim_count}"
        self._mark("UserSpeechTurnAggregationAssembler", state, detail)
        self._interim_threshold_or_playback_overlap_record = {
            "state": state, "event": "Fired", "reason": reason,
            "interim_count": self._aggregate_interim_count,
        }

    def _ResolveInterimThresholdOrPlaybackOverlapState(self) -> None:
        """Clear the current detected condition, mark ``InterimThresholdOrPlaybackOverlapResolved``, and keep a record
        of the end to send with the next speech, and return ``None``, doing nothing when no condition holds. The two
        conditions are described in the module docstring above."""
        if self._interim_threshold_or_playback_overlap_state is None:
            return
        resolved = self._interim_threshold_or_playback_overlap_state
        self._interim_threshold_or_playback_overlap_state = None
        self._mark("UserSpeechTurnAggregationAssembler",
                   "InterimThresholdOrPlaybackOverlapResolved", f"was={resolved}")
        self._interim_threshold_or_playback_overlap_record = {
            "state": resolved, "event": "Resolved", "reason": "",
            "interim_count": self._aggregate_interim_count,
        }

    def _RelayIncrementalInterimBundle(self, interim: str) -> None:
        """Count one more transcription, raise the count condition when the threshold is reached, and pass the voice
        adapter's ``incremental_phrase_tick`` a dict with the speech so far under ``IncrementalPhrase`` and any pending
        condition record, and return ``None``, passing nothing when both are empty.

        The speech so far is the held-back speech, then the collected final transcriptions, then ``interim``, so the
        incremental analyzer keeps receiving the whole unfinished turn while a turn waits for its reply. Called by
        ``interim`` and ``segment`` in this class.
        """
        self._aggregate_interim_count += 1
        if (self._unyielding_speech_interim_threshold is not None
                and self._interim_threshold_or_playback_overlap_state is None
                and self._aggregate_interim_count
                >= self._unyielding_speech_interim_threshold):
            self._LatchInterimThresholdOrPlaybackOverlapState(
                "AggregateInterimCountExceededConfiguredThreshold", "interim transcription-threshold")
        inputs: dict = {}
        current = " ".join(self._pre_segments + self._segments
                           + ([interim] if interim else [])).strip()
        if current:
            inputs["IncrementalPhrase"] = current
        # A change of detected condition is sent once, with this interim transcription.
        if self._interim_threshold_or_playback_overlap_record is not None:
            inputs["user_speech_turn_aggregation_interim_threshold_or_playback_overlap_transition"] = \
                self._interim_threshold_or_playback_overlap_record
            self._interim_threshold_or_playback_overlap_record = None
        if inputs:
            self._voice.incremental_phrase_tick(inputs)

    def _turn_text(self) -> str:
        """Return the text of the turn and empty both the held-back and the collected speech. When both hold speech, the
        text is the held-back speech, a line with ``PRE_POST_MARKER``, and the speech from after, and otherwise the one
        that holds speech, joined by spaces. Called only by ``_flush_after`` in this class."""
        pre, post = self._pre_segments, self._segments
        self._pre_segments, self._segments = [], []
        if pre and post:
            return (" ".join(pre).strip() + "\n" + self.PRE_POST_MARKER + "\n"
                    + " ".join(post).strip())
        return " ".join(pre + post).strip()

    def _gate_blocked(self) -> bool:
        """Return whether a turn sent earlier is still waiting for its reply to start playing, letting turns go again,
        with the mark ``GateUp`` and the text "FAILSAFE", once ``gate_failsafe_s`` has passed, as the module docstring
        above explains."""
        if self._gate_down_since is None:
            return False
        if time.monotonic() - self._gate_down_since > self._gate_failsafe_s:
            self._gate_down_since = None
            self._mark("UserSpeechTurnAggregationAssembler", "GateUp", "FAILSAFE")
            return False
        return True

    def _cancel_timer(self) -> None:
        """Cancel the pending wait for the pause that ends a turn, if there is one, and return ``None``. Called by
        ``speech_started`` and ``_rearm`` in this class."""
        if self._timer is not None and not self._timer.done():
            self._timer.cancel()
        self._timer = None

    def _rearm(self) -> None:
        """Cancel and restart the wait of ``debounce_s`` seconds after which the collected speech becomes a turn, and
        return ``None``. No wait starts while the user is speaking, while nothing is collected, while a turn is being
        processed, while an interim transcription has arrived after the last final one, or while a turn waits for its
        reply to start playing, under the rules the module docstring above gives."""
        self._cancel_timer()
        if (self._speaking or not self._segments or self._settling
                or self._interim_after_final or self._gate_blocked()):
            return
        self._timer = asyncio.ensure_future(self._flush_after(self._debounce_s))

    async def _flush_after(self, delay: float) -> None:
        """Wait ``delay`` seconds, then, when the conditions of ``_rearm`` still allow it, give the collected speech to
        the voice adapter's ``on_user_turn`` as one turn, pass a non-empty reply to ``on_reply``, and return ``None``.
        While a turn waits for its reply the check is repeated every second. An empty reply lets turns go again at once,
        with the mark ``GateUp`` and the text "empty reply". This is the step the module docstring above calls the turn
        going to the session, counted in ``churns``."""
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            return
        # The timer reference is dropped here so that speech starting now can cancel only
        # the wait above, never a turn the session is already processing.
        self._timer = None
        if (self._speaking or not self._segments or self._settling
                or self._interim_after_final or self._gate_blocked()):
            if self._gate_blocked():
                self._timer = asyncio.ensure_future(self._flush_after(1.0))
            return
        text = self._turn_text()
        self._settling = True
        self.churns += 1
        # The interim transcription-count condition ends with the turn. The playback-overlap condition
        # ends only in ``TTSStarted``.
        self._aggregate_interim_count = 0
        if (self._interim_threshold_or_playback_overlap_state
                == "AggregateInterimCountExceededConfiguredThreshold"):
            self._ResolveInterimThresholdOrPlaybackOverlapState()
        self._gate_down_since = time.monotonic()
        self._mark("UserSpeechTurnAggregationAssembler", "GateDown", text)
        self._mark("il_settle", "SettleStart", text)
        try:
            reply = (await self._voice.on_user_turn(text) or "").strip()
        finally:
            self._settling = False
        self._mark("il_settle", "SettleEnd", reply)
        if reply:
            await self._on_reply(reply)
        else:
            # No reply will start playing for this turn, so turns may be sent again.
            if self._gate_down_since is not None:
                self._gate_down_since = None
                self._mark("UserSpeechTurnAggregationAssembler", "GateUp", "empty reply")
        self._rearm()
