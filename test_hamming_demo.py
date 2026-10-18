import unittest

from hamming_demo import (
    calculate_syndrome,
    correct_single_bit,
    encode_hamming,
    extract_data,
)


class HammingCodeTests(unittest.TestCase):
    def test_encoded_word_has_valid_even_parity(self) -> None:
        codeword = encode_hamming("1011")

        self.assertEqual(len(codeword), 7)
        self.assertEqual(calculate_syndrome(codeword), (0, {1: 0, 2: 0, 4: 0}))
        self.assertEqual(extract_data(codeword), "1011")

    def test_each_single_bit_error_is_located_and_corrected(self) -> None:
        original = encode_hamming("1101")

        for position in range(1, 8):
            with self.subTest(position=position):
                changed = list(original)
                changed[position - 1] = "1" if changed[position - 1] == "0" else "0"
                received = "".join(changed)
                error_position, _ = calculate_syndrome(received)

                self.assertEqual(error_position, position)
                self.assertEqual(correct_single_bit(received, error_position), original)
                self.assertEqual(extract_data(correct_single_bit(received, error_position)), "1101")

    def test_invalid_bit_strings_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            encode_hamming("10x1")
        with self.assertRaises(ValueError):
            calculate_syndrome("101")


if __name__ == "__main__":
    unittest.main()
