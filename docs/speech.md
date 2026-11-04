# Speech

The speak channel says a message on speakers: media players and Assist satellites. Use it with `heads_up.notify` (`channels: [speak]`) or the `heads_up.speak` shortcut.

```yaml
- action: heads_up.speak
  data:
    id: garage_open
    message: The garage door has been open for 10 minutes.
    recipients:
      - media_player.kitchen
      - assist_satellite.hall
```

## Who hears it

`recipients` are media players, Assist satellites, recipient groups (written `Name (group)`) and areas. An area is written by its ID (`living_room`) or its name (`Living Room`, any case); it needs no group. A group or area stands for its speakers; see [Audiences and recipients](audiences.md). Speech has no audience: it goes to speakers, not to people.

## What is said

The text is `tts_message` if you set it, otherwise the title, otherwise the message. A text longer than 200 characters is cut after the last word that fits and ends with `…`. Change the limit with the option Spoken text: longest (characters).

## How it is said

| Speaker | What Heads Up calls |
|---|---|
| Assist satellite | `assist_satellite.announce` |
| Media player that supports announcements | `tts.speak`, which announces: the player lowers or pauses what it is playing and continues afterwards, if the player does that |
| Other media player | `media_player.play_media` with the text-to-speech media source, as plain playback |

- The text-to-speech engine is the option Text-to-speech engine. If it is empty and exactly one `tts` entity exists, that one is used. With several or none, speech to media players fails with the reason `no_tts_engine`.
- The language is the Home Assistant language.
- Heads Up never changes or restores a volume. A player speaks at the volume it has.
- What happens to music after an announcement depends on the player. Heads Up promises nothing beyond calling the services above.

## Queue and repeats

- A speaker says one message at a time. A player without announcement support is given up to 30 seconds to stop playing before the next message.
- The same text is not said again on the same speaker within 60 seconds (option Spoken text: repeat pause, 0 for no pause). A different text is never held back. The trace shows `cooldown`.
- An update to a message does not say it again (`already_spoken`).
- Speech cannot be taken back. When a message is cleared or expires, nothing is said.
- A Quiet hours policy with the action Send quietly skips speech (`quiet_hours`).

## Failures

An area or group with no speaker, and a speaker that no longer exists, also leave one entry in Home Assistant's notification bell: "Heads Up: no speaker" or "Heads Up: speaker not found". It names the area, group or speaker and never the message, because every user sees the bell. A repeat replaces the entry, and it stays until someone dismisses it. A dry run in the panel creates none.

A speaker that no longer exists, a service that is missing or fails, and a missing engine give a `failed` delivery in the trace (`heads_up/hub_trace`) with the reasons `entity_missing`, `service_not_found`, `send_failed` and `no_tts_engine`. A failing service, a missing speaker and a missing engine each write a log warning, at most one per speaker per hour. The warning for a missing engine names the engines found. Skips (quiet hours, the pause, nothing to say) are written at debug level only; see [Troubleshooting](troubleshooting.md) to turn debug logging on. Test send in the panel shows each result with its reason.

## Limits

- No all-clear announcement and no volume handling.
- Rooms are Home Assistant areas and their assigned speakers; occupancy is not used.
- Not tested on a real speaker.
