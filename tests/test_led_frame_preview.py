import unittest

from midi_wled_bridge.qt_gui import (
    decode_led_frame_line,
    encode_led_frame_line,
    custom_mapping_layout,
    decode_layout_json,
    encode_layout_json,
    mapping_grid_layout,
    underlights_layout_positions,
    QApplication,
    MappingPreview,
    rotate_selected_positions,
)


class LedFramePreviewTests(unittest.TestCase):
    def test_led_frame_line_round_trips_exact_rgb_values(self) -> None:
        colors = [(0, 0, 0), (1, 31, 63), (255, 120, 4)]

        line = encode_led_frame_line(colors)

        self.assertEqual("LED_FRAME rgb=000000011f3fff7804", line)
        self.assertEqual(colors, decode_led_frame_line(line))

    def test_mapping_grid_layout_creates_one_square_per_led_and_wraps(self) -> None:
        layout = mapping_grid_layout(56, width=620, height=170)

        self.assertEqual(56, len(layout))
        self.assertGreater(len({tile.y for tile in layout}), 1)
        self.assertTrue(all(tile.size > 0 for tile in layout))
        self.assertTrue(all(tile.x + tile.size <= 620 for tile in layout))
        self.assertTrue(all(tile.y + tile.size <= 170 for tile in layout))

    def test_mapping_grid_layout_handles_empty_strip(self) -> None:
        self.assertEqual([], mapping_grid_layout(0, width=620, height=170))

    def test_underlights_layout_follows_bottom_right_top_left_arrow_order(self) -> None:
        positions = underlights_layout_positions(32)

        self.assertEqual(32, len(positions))
        self.assertTrue(all(positions[index][1] > 0.75 for index in range(8)))
        self.assertLess(positions[0][0], positions[7][0])
        self.assertTrue(all(positions[index][0] > 0.75 for index in range(8, 16)))
        self.assertGreater(positions[8][1], positions[15][1])
        self.assertTrue(all(positions[index][1] < 0.25 for index in range(16, 24)))
        self.assertGreater(positions[16][0], positions[23][0])
        self.assertTrue(all(positions[index][0] < 0.25 for index in range(24, 32)))
        self.assertLess(positions[24][1], positions[31][1])

    def test_custom_mapping_layout_places_square_tiles_at_normalized_positions(self) -> None:
        layout = custom_mapping_layout([(0.25, 0.25), (0.75, 0.75)], width=800, height=500)

        self.assertEqual(2, len(layout))
        self.assertAlmostEqual(200, layout[0].x + layout[0].size / 2)
        self.assertAlmostEqual(125, layout[0].y + layout[0].size / 2)
        self.assertAlmostEqual(600, layout[1].x + layout[1].size / 2)
        self.assertAlmostEqual(375, layout[1].y + layout[1].size / 2)

    def test_layout_json_round_trips_reusable_normalized_positions(self) -> None:
        positions = [(0.1, 0.2), (0.75, 0.9)]

        encoded = encode_layout_json(positions)

        self.assertEqual(positions, decode_layout_json(encoded))

    def test_rotates_selected_positions_around_selection_center(self) -> None:
        positions = [(0.25, 0.25), (0.75, 0.25), (0.9, 0.9)]

        rotated = rotate_selected_positions(positions, {0, 1}, 90)

        self.assertEqual([(0.5, 0.0), (0.5, 0.5), (0.9, 0.9)], rotated)

    def test_reset_layout_rebuilds_standard_underlights_positions(self) -> None:
        QApplication.instance() or QApplication([])
        preview = MappingPreview()
        preview.resize(620, 170)
        preview.set_led_count(4)
        preview.set_custom_positions([(0.2, 0.2), (0.3, 0.3), (0.4, 0.4), (0.5, 0.5)])

        preview.reset_layout()

        self.assertEqual(underlights_layout_positions(4), preview.custom_positions)


if __name__ == "__main__":
    unittest.main()
