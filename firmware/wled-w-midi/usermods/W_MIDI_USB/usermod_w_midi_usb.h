#pragma once

#include "wled.h"

#if defined(ARDUINO_ARCH_ESP32) && defined(CONFIG_IDF_TARGET_ESP32S3)
#include <USB.h>
#include "esp32-hal-tinyusb.h"
#endif

#include "w_midi_palette.h"

#ifndef USERMOD_ID_W_MIDI_USB
#define USERMOD_ID_W_MIDI_USB 0x57D1
#endif

#if defined(ARDUINO_ARCH_ESP32) && defined(CONFIG_IDF_TARGET_ESP32S3) && CONFIG_TINYUSB_ENABLED && CONFIG_TINYUSB_MIDI_ENABLED
static uint16_t wMidiUsbLoadDescriptor(uint8_t *dst, uint8_t *itf) {
  const uint8_t strIndex = tinyusb_add_string_descriptor("W-MIDI Underlight");
  const uint8_t epNum = tinyusb_get_free_duplex_endpoint();
  if (epNum == 0) return 0;

  uint8_t descriptor[TUD_MIDI_DESC_LEN] = {
      TUD_MIDI_DESCRIPTOR(*itf, strIndex, epNum, (uint8_t)(0x80 | epNum), 64)};
  *itf += 2;
  memcpy(dst, descriptor, TUD_MIDI_DESC_LEN);
  return TUD_MIDI_DESC_LEN;
}
#endif

class WMidiUsbUsermod : public Usermod {
 private:
  static constexpr const char *_name = "W_MIDI_USB";
  bool enabled = true;
  bool usbPriority = true;
  uint16_t ledCount = 32;
  uint8_t firstNote = 36;
  uint8_t midiChannel = 0;
  uint16_t usbTimeoutMs = 600;
  uint16_t currentLimitMa = 850;
  uint32_t lastUsbMidiMs = 0;
  bool usbActive = false;
  bool dirty = false;
  uint32_t pixels[32] = {0};

#if defined(ARDUINO_ARCH_ESP32) && defined(CONFIG_IDF_TARGET_ESP32S3)
  bool usbStarted = false;
#endif

  uint16_t clippedLedCount() const {
    return ledCount < 32 ? ledCount : 32;
  }

  bool channelMatches(uint8_t status) const {
    if (midiChannel == 0) return true;
    return ((status & 0x0F) + 1) == midiChannel;
  }

  int16_t noteToIndex(uint8_t note) const {
    if (note < firstNote) return -1;
    const uint16_t index = note - firstNote;
    return index < clippedLedCount() ? index : -1;
  }

  uint32_t colorForVelocity(uint8_t velocity) const {
    const uint8_t *rgb = W_MIDI_PALETTE[velocity & 0x7F];
    const uint32_t scaled = scaleForCurrent(rgb[0], rgb[1], rgb[2]);
    return scaled;
  }

  uint32_t scaleForCurrent(uint8_t red, uint8_t green, uint8_t blue) const {
    const uint16_t limit = currentLimitMa > 1 ? currentLimitMa : 1;
    const uint16_t maxAtFullWhite = clippedLedCount() * 60;
    if (maxAtFullWhite <= limit) {
      return RGBW32(red, green, blue, 0);
    }
    const uint32_t scale = (uint32_t)limit * 255U / maxAtFullWhite;
    return RGBW32((red * scale) / 255U, (green * scale) / 255U, (blue * scale) / 255U, 0);
  }

  void markUsbActive() {
    lastUsbMidiMs = millis();
    usbActive = true;
  }

  void handleNoteOn(uint8_t note, uint8_t velocity) {
    const int16_t index = noteToIndex(note);
    if (index < 0) return;
    pixels[index] = velocity == 0 ? 0 : colorForVelocity(velocity);
    dirty = true;
  }

  void handleNoteOff(uint8_t note) {
    const int16_t index = noteToIndex(note);
    if (index < 0) return;
    pixels[index] = 0;
    dirty = true;
  }

  void handleMidiPacket(uint8_t status, uint8_t data1, uint8_t data2) {
    if (!channelMatches(status)) return;
    markUsbActive();
    switch (status & 0xF0) {
      case 0x90:
        if (data2 == 0) {
          handleNoteOff(data1);
        } else {
          handleNoteOn(data1, data2);
        }
        break;
      case 0x80:
        handleNoteOff(data1);
        break;
      default:
        break;
    }
  }

  void flushLeds() {
    const uint16_t count = clippedLedCount();
    for (uint16_t index = 0; index < count; index++) {
      strip.setPixelColor(index, pixels[index]);
    }
    strip.show();
    dirty = false;
  }

  void clearUsbState() {
    usbActive = false;
    dirty = false;
    for (uint16_t index = 0; index < 32; index++) {
      pixels[index] = 0;
    }
  }

 public:
  void setup() override {
#if defined(ARDUINO_ARCH_ESP32) && defined(CONFIG_IDF_TARGET_ESP32S3)
    if (enabled && !usbStarted) {
#if CONFIG_TINYUSB_ENABLED && CONFIG_TINYUSB_MIDI_ENABLED
      tinyusb_enable_interface(USB_INTERFACE_MIDI, TUD_MIDI_DESC_LEN, wMidiUsbLoadDescriptor);
      USB.productName("W-MIDI Underlight");
      USB.begin();
      usbStarted = true;
#endif
    }
#endif
  }

  void loop() override {
    if (!enabled) return;

#if defined(ARDUINO_ARCH_ESP32) && defined(CONFIG_IDF_TARGET_ESP32S3)
#if CONFIG_TINYUSB_ENABLED && CONFIG_TINYUSB_MIDI_ENABLED
    uint8_t packet[4];
    while (tud_midi_packet_read(packet)) {
      handleMidiPacket(packet[1], packet[2], packet[3]);
    }
#endif
#endif

    if (usbActive && millis() - lastUsbMidiMs > usbTimeoutMs) {
      clearUsbState();
      return;
    }

    if (usbPriority && usbActive && dirty) {
      flushLeds();
    }
  }

  void addToConfig(JsonObject &root) override {
    JsonObject top = root.createNestedObject(_name);
    top["enabled"] = enabled;
    top["ledCount"] = ledCount;
    top["firstNote"] = firstNote;
    top["midiChannel"] = midiChannel;
    top["usbTimeoutMs"] = usbTimeoutMs;
    top["currentLimitMa"] = currentLimitMa;
    top["usbPriority"] = usbPriority;
  }

  bool readFromConfig(JsonObject &root) override {
    JsonObject top = root[_name];
    if (top.isNull()) return false;
    if (!top["enabled"].isNull()) enabled = top["enabled"].as<bool>();
    if (!top["ledCount"].isNull()) ledCount = constrain(top["ledCount"].as<uint16_t>(), 1, 32);
    if (!top["firstNote"].isNull()) firstNote = constrain(top["firstNote"].as<uint8_t>(), 0, 127);
    if (!top["midiChannel"].isNull()) midiChannel = constrain(top["midiChannel"].as<uint8_t>(), 0, 16);
    if (!top["usbTimeoutMs"].isNull()) usbTimeoutMs = constrain(top["usbTimeoutMs"].as<uint16_t>(), 100, 5000);
    if (!top["currentLimitMa"].isNull()) currentLimitMa = constrain(top["currentLimitMa"].as<uint16_t>(), 100, 3000);
    if (!top["usbPriority"].isNull()) usbPriority = top["usbPriority"].as<bool>();
    return true;
  }

  void addToJsonInfo(JsonObject &root) override {
    JsonObject user = root["u"];
    if (user.isNull()) user = root.createNestedObject("u");
    JsonArray info = user.createNestedArray("W-MIDI USB");
    info.add(enabled ? "enabled" : "disabled");
    info.add(usbActive ? "USB MIDI active" : "idle");
  }

  uint16_t getId() override {
    return USERMOD_ID_W_MIDI_USB;
  }
};
