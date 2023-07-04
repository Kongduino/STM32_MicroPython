#include <stdio.h>
#include <stdint.h>
#define WIDTH (8 * sizeof(uint32_t))
#define TOPBIT (1 << (WIDTH - 1))
#define POLYNOMIAL 0x04C11DB7
#define INITIAL_REMAINDER 0xFFFFFFFF
#define FINAL_XOR_VALUE 0xFFFFFFFF
#define CHECK_VALUE 0xCBF43926
uint32_t crcTable[256];

int main(int argc, char** argv) {
  uint32_t remainder;
  int dividend;
  unsigned char bit;
  printf("WIDTH: %d\n\n", WIDTH);
  // Compute the remainder of each possible dividend.
  for (dividend = 0; dividend < 256; ++dividend) {
    // Start with the dividend followed by zeros.
    remainder = dividend << (WIDTH - 8);
    // Perform modulo-2 division, a bit at a time.
    for (bit = 8; bit > 0; --bit) {
      // Try to divide the current data bit.
      if (remainder & TOPBIT) remainder = (remainder << 1) ^ POLYNOMIAL;
      else remainder = (remainder << 1);
    }
    // Store the result into the table.
    crcTable[dividend] = remainder;
  }
  for (int i = 0; i < 256; i+=8) {
    for (int j = 0; j < 8; j++) printf("0x%08x, ", crcTable[i+j]);
    printf("%c", 10);
  }
  printf("%c", 10);
}
