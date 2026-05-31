# WLED Discovery Design

## Goal

Add a GUI action that finds WLED devices on the local network and lets the user copy a discovered device IP into the existing WLED IP field.

## Design

The discovery logic lives in a small standalone module, `midi_wled_bridge.discovery`, so it can be tested without starting the Tk GUI. It scans likely local `/24` IPv4 networks, requests `http://<ip>/json/info`, and treats a JSON response as a WLED candidate when it contains WLED-like fields. The returned device record contains the display name and IP address.

The GUI adds a `Find WLED` button next to the existing IP address entry. Clicking it opens a compact search window, starts discovery in a background thread, and keeps Tk responsive. Results are shown as `name - ip`; selecting a result writes that IP into the existing field. Empty results and errors are shown in the window and logged.

## Error Handling

Connection failures, timeouts, invalid JSON, and non-WLED HTTP responses are ignored per host. If the overall scan fails, the GUI shows a friendly error in the search window and writes the detail to the log.

## Testing

Unit tests cover parsing WLED JSON, ignoring invalid responses, and sorting discovered devices. A GUI source-level test checks that the WLED finder control and background discovery hooks are present.
