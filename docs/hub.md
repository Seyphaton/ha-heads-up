# Notification hub

Heads Up is one place that orchestrates where a message shows up, who is told, and when it is delivered or escalated. This page names the parts and shows what they do in a household.

## The words

- **Message:** what an automation sends. It has text, a severity and a lifecycle: it ends when someone closes it, a condition stops matching, a timeout passes or an action clears it. The dashboard banner is one view of a message.
- **Channel:** where a message appears: banner, push, popup, speech, mail or Persistent Notification (Home Assistant's bell). The banner is the base; the others are on the same level and each is named per call or by a policy.
- **Audience:** a named group of people that can change over time: Everyone, Admins, At home, Not home, Last to leave, First home, or your own. See [Audiences and recipients](audiences.md).
- **Recipient:** one target inside an audience: a person, a phone, a speaker.
- **Policy:** a rule for how messages behave, kept apart from the automation: escalate, remind, keep quiet at night, wait until someone is home, fall back to someone else, summarize, deliver at once. See [Policies](policies.md).
- **Acknowledgement:** someone saw the message. It stops escalations and reminders. The banner stays for the others.
- **Delivery:** one message, one recipient, one channel, with a result: sent, held, skipped or failed. The trace lists them.

## One call

```yaml
action: heads_up.notify
data:
  message: Water leak
  tts_message: Water in the utility room
  severity: critical
  channels: [banner, push, speak]
  to:
    push: {audience: Admins}
    speak: {recipients: [Ground floor speakers]}
```

The same message is on the dashboard, on the phones of the administrators and on the speakers. Closing it on one phone clears it there; clearing the message clears it everywhere. Without any policy that is all that happens.

## In a household

- A leak at 03:00: A critical message reaches every phone and the dashboard, quiet hours let it pass, and speakers say it. Ben acknowledges on his phone, so the escalation stops. The banner stays until the sensor is dry.
- A window left open in an empty house: The audience Last to leave gets a push. Nobody else is disturbed. The push is taken back when the window closes.
- The doorbell: A short message on the wall tablet and a spoken line. With a timeout of 60 seconds everything clears itself.
- The washing machine: A push to the person who started it. Quiet hours turn it into a banner at night. An Away policy sends it when they arrive.
- Nobody reacts to a critical message: After five minutes an escalation notifies a backup person and the speakers. A reminder repeats it. An acknowledgement stops both.
- A phone is replaced: Edit the person's recipient profile once. No automation changes.
- Why you did not get a message: Test send previews a call: who is reached now, and why anyone is skipped, held or dropped. The trace of a message shows what happened, for example "push to Anna skipped: quiet hours".

## Limits that protect the phones

A push over 5 per device per minute, or over 60 in total, is skipped and shows in the trace as `rate_limited`. An update with the same content as the last one is not sent again for 30 seconds (`duplicate`). Critical messages are never held back. All three are settings.

## After a restart

Timers keep their due times. A step that was due during the restart runs once if the message is still active and not acknowledged. Messages held for quiet hours, for Away or for a summary stay held. Pushes of messages that ended while Home Assistant was stopped are taken back. The notification bell of Home Assistant is emptied by a restart, so Heads Up puts the entries of active messages back.

## Where to configure

- Settings > Devices & services > Heads Up > Configure, and the panel's Settings page: the same entries. See [Panel](panel.md).
- Audiences, recipients, policies and channels: the panel, or the entries of the integration.
- Banners from entities without an automation: [Watch rules](rules.md).
