// Copyright 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Create a state machine for validating UTF-8. The algorithm in brief:
// 1. Convert the complete unicode range of code points, except for the
//    surrogate code points, to an ordered array of sequences of bytes in
//    UTF-8.
// 2. Convert individual bytes to ranges, starting from the right of each byte
//    sequence. For each range, ensure the bytes on the left and the ranges
//    on the right are the identical.
// 3. Convert the resulting list of ranges into a state machine, collapsing
//    identical states.
// 4. Convert the state machine to an array of bytes.
// 5. Output as a C++ file.
//
// To use:
//  $ ninja -C out/Release build_utf8_validator_tables
//  $ out/Release/build_utf8_validator_tables
//                                   --output=base/i18n/utf8_validator_tables.cc
//  $ git add base/i18n/utf8_validator_tables.cc
//
// Because the table is not expected to ever change, it is checked into the
// repository rather than being regenerated at build time.
//
// This code uses type uint8_t throughout to represent bytes, to avoid
// signed/unsigned char confusion.

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <algorithm>
#include <map>
#include <string>
#include <vector>

#include "base/command_line.h"
#include "base/files/file_path.h"
#include "base/files/file_util.h"
#include "base/logging.h"
#include "base/macros.h"
#include "base/numerics/safe_conversions.h"
#include "base/strings/stringprintf.h"
#include "third_party/icu/source/common/unicode/utf8.h"

namespace {

const char kHelpText[] =
    "Usage: build_utf8_validator_tables [ --help ] [ --output=<file> ]\n";

const char kProlog[] =
    "// Copyright 2013 The Chromium Authors. All rights reserved.\n"
    "// Use of this source code is governed by a BSD-style license that can "
    "be\n"
    "// found in the LICENSE file.\n"
    "\n"
    "// This file is auto-generated by build_utf8_validator_tables.\n"
    "// DO NOT EDIT.\n"
    "\n"
    "#include \"base/i18n/utf8_validator_tables.h\"\n"
    "\n"
    "namespace base {\n"
    "namespace internal {\n"
    "\n"
    "const uint8_t kUtf8ValidatorTables[] = {\n";

const char kEpilog[] =
    "};\n"
    "\n"
    "const size_t kUtf8ValidatorTablesSize = arraysize(kUtf8ValidatorTables);\n"
    "\n"
    "}  // namespace internal\n"
    "}  // namespace base\n";

// Ranges are inclusive at both ends--they represent [from, to]
class Range {
 public:
  // Ranges always start with just one byte.
  explicit Range(uint8_t value) : from_(value), to_(value) {}

  // Range objects are copyable and assignable to be used in STL
  // containers. Since they only contain non-pointer POD types, the default copy
  // constructor, assignment operator and destructor will work.

  // Add a byte to the range. We intentionally only support adding a byte at the
  // end, since that is the only operation the code needs.
  void AddByte(uint8_t to) {
    CHECK(to == to_ + 1);
    to_ = to;
  }

  uint8_t from() const { return from_; }
  uint8_t to() const { return to_; }

  bool operator<(const Range& rhs) const {
    return (from() < rhs.from() || (from() == rhs.from() && to() < rhs.to()));
  }

  bool operator==(const Range& rhs) const {
    return from() == rhs.from() && to() == rhs.to();
  }

 private:
  uint8_t from_;
  uint8_t to_;
};

// A vector of Ranges is like a simple regular expression--it corresponds to
// a set of strings of the same length that have bytes in each position in
// the appropriate range.
typedef std::vector<Range> StringSet;

// A UTF-8 "character" is represented by a sequence of bytes.
typedef std::vector<uint8_t> Character;

// In the second stage of the algorithm, we want to convert a large list of
// Characters into a small list of StringSets.
struct Pair {
  Character character;
  StringSet set;
};

typedef std::vector<Pair> PairVector;

// A class to print a table of numbers in the same style as clang-format.
class TablePrinter {
 public:
  explicit TablePrinter(FILE* stream)
      : stream_(stream), values_on_this_line_(0), current_offset_(0) {}

  void PrintValue(uint8_t value) {
    if (values_on_this_line_ == 0) {
      fputs("   ", stream_);
    } else if (values_on_this_line_ == kMaxValuesPerLine) {
      fprintf(stream_, "  // 0x%02x\n   ", current_offset_);
      values_on_this_line_ = 0;
    }
    fprintf(stream_, " 0x%02x,", static_cast<int>(value));
    ++values_on_this_line_;
    ++current_offset_;
  }

  void NewLine() {
    while (values_on_this_line_ < kMaxValuesPerLine) {
      fputs("      ", stream_);
      ++values_on_this_line_;
    }
    fprintf(stream_, "  // 0x%02x\n", current_offset_);
    values_on_this_line_ = 0;
  }

 private:
  // stdio stream. Not owned.
  FILE* stream_;

  // Number of values so far printed on this line.
  int values_on_this_line_;

  // Total values printed so far.
  int current_offset_;

  static const int kMaxValuesPerLine = 8;

  DISALLOW_COPY_AND_ASSIGN(TablePrinter);
};

// Start by filling a PairVector with characters. The resulting vector goes from
// "\x00" to "\xf4\x8f\xbf\xbf".
PairVector InitializeCharacters() {
  PairVector vector;
  for (int i = 0; i <= 0x10FFFF; ++i) {
    if (i >= 0xD800 && i < 0xE000) {
      // Surrogate codepoints are not permitted. Non-character code points are
      // explicitly permitted.
      continue;
    }
    uint8_t bytes[4];
    unsigned int offset = 0;
    UBool is_error = false;
    U8_APPEND(bytes, offset, arraysize(bytes), i, is_error);
    DCHECK(!is_error);
    DCHECK_GT(offset, 0u);
    DCHECK_LE(offset, arraysize(bytes));
    Pair pair = {Character(bytes, bytes + offset), StringSet()};
    vector.push_back(pair);
  }
  return vector;
}

// Construct a new Pair from |character| and the concatenation of |new_range|
// and |existing_set|, and append it to |pairs|.
void ConstructPairAndAppend(const Character& character,
                            const Range& new_range,
                            const StringSet& existing_set,
                            PairVector* pairs) {
  Pair new_pair = {character, StringSet(1, new_range)};
  new_pair.set.insert(
      new_pair.set.end(), existing_set.begin(), existing_set.end());
  pairs->push_back(new_pair);
}

// Each pass over the PairVector strips one byte off the right-hand-side of the
// characters and adds a range to the set on the right. For example, the first
// pass converts the range from "\xe0\xa0\x80" to "\xe0\xa0\xbf" to ("\xe0\xa0",
// [\x80-\xbf]), then the second pass converts the range from ("\xe0\xa0",
// [\x80-\xbf]) to ("\xe0\xbf", [\x80-\xbf]) to ("\xe0",
// [\xa0-\xbf][\x80-\xbf]).
void MoveRightMostCharToSet(PairVector* pairs) {
  PairVector new_pairs;
  PairVector::const_iterator it = pairs->begin();
  while (it != pairs->end() && it->character.empty()) {
    new_pairs.push_back(*it);
    ++it;
  }
  CHECK(it != pairs->end());
  Character unconverted_bytes(it->character.begin(), it->character.end() - 1);
  Range new_range(it->character.back());
  StringSet converted = it->set;
  ++it;
  while (it != pairs->end()) {
    const Pair& current_pair = *it++;
    if (current_pair.character.size() == unconverted_bytes.size() + 1 &&
        std::equal(unconverted_bytes.begin(),
                   unconverted_bytes.end(),
                   current_pair.character.begin()) &&
        converted == current_pair.set) {
      // The particular set of UTF-8 codepoints we are validating guarantees
      // that each byte range will be contiguous. This would not necessarily be
      // true for an arbitrary set of UTF-8 codepoints.
      DCHECK_EQ(new_range.to() + 1, current_pair.character.back());
      new_range.AddByte(current_pair.character.back());
      continue;
    }
    ConstructPairAndAppend(unconverted_bytes, new_range, converted, &new_pairs);
    unconverted_bytes = Character(current_pair.character.begin(),
                                  current_pair.character.end() - 1);
    new_range = Range(current_pair.character.back());
    converted = current_pair.set;
  }
  ConstructPairAndAppend(unconverted_bytes, new_range, converted, &new_pairs);
  new_pairs.swap(*pairs);
}

void MoveAllCharsToSets(PairVector* pairs) {
  // Since each pass of the function moves one character, and UTF-8 sequences
  // are at most 4 characters long, this simply runs the algorithm four times.
  for (int i = 0; i < 4; ++i) {
    MoveRightMostCharToSet(pairs);
  }
#if DCHECK_IS_ON()
  for (PairVector::const_iterator it = pairs->begin(); it != pairs->end();
       ++it) {
    DCHECK(it->character.empty());
  }
#endif
}

// Logs the generated string sets in regular-expression style, ie. [\x00-\x7f],
// [\xc2-\xdf][\x80-\xbf], etc. This can be a useful sanity-check that the
// algorithm is working. Use the command-line option
// --vmodule=build_utf8_validator_tables=1 to see this output.
void LogStringSets(const PairVector& pairs) {
  for (PairVector::const_iterator pair_it = pairs.begin();
       pair_it != pairs.end();
       ++pair_it) {
    std::string set_as_string;
    for (StringSet::const_iterator set_it = pair_it->set.begin();
         set_it != pair_it->set.end();
         ++set_it) {
      set_as_string += base::StringPrintf("[\\x%02x-\\x%02x]",
                                          static_cast<int>(set_it->from()),
                                          static_cast<int>(set_it->to()));
    }
    VLOG(1) << set_as_string;
  }
}

// A single state in the state machine is represented by a sorted vector of
// start bytes and target states. All input bytes in the range between the start
// byte and the next entry in the vector (or 0xFF) result in a transition to the
// target state.
struct StateRange {
  uint8_t from;
  uint8_t target_state;
};

typedef std::vector<StateRange> State;

// Generates a state where all bytes go to state 1 (invalid). This is also used
// as an initialiser for other states (since bytes from outside the desired
// range are invalid).
State GenerateInvalidState() {
  const StateRange range = {0, 1};
  return State(1, range);
}

// A map from a state (ie. a set of strings which will match from this state) to
// a number (which is an index into the array of states).
typedef std::map<StringSet, uint8_t> StateMap;

// Create a new state corresponding to |set|, add it |states| and |state_map|
// and return the index it was given in |states|.
uint8_t MakeState(const StringSet& set,
                  std::vector<State>* states,
                  StateMap* state_map) {
  DCHECK(!set.empty());
  const Range& range = set.front();
  const StringSet rest(set.begin() + 1, set.end());
  const StateMap::const_iterator where = state_map->find(rest);
  const uint8_t target_state = where == state_map->end()
                                   ? MakeState(rest, states, state_map)
                                   : where->second;
  DCHECK_LT(0, range.from());
  DCHECK_LT(range.to(), 0xFF);
  const StateRange new_state_initializer[] = {
      {0, 1},
      {range.from(), target_state},
      {static_cast<uint8_t>(range.to() + 1), 1}};
  states->push_back(
      State(new_state_initializer,
            new_state_initializer + arraysize(new_state_initializer)));
  const uint8_t new_state_number =
      base::checked_cast<uint8_t>(states->size() - 1);
  CHECK(state_map->insert(std::make_pair(set, new_state_number)).second);
  return new_state_number;
}

std::vector<State> GenerateStates(const PairVector& pairs) {
  // States 0 and 1 are the initial/valid state and invalid state, respectively.
  std::vector<State> states(2, GenerateInvalidState());
  StateMap state_map;
  state_map.insert(std::make_pair(StringSet(), 0));
  for (PairVector::const_iterator it = pairs.begin(); it != pairs.end(); ++it) {
    DCHECK(it->character.empty());
    DCHECK(!it->set.empty());
    const Range& range = it->set.front();
    const StringSet rest(it->set.begin() + 1, it->set.end());
    const StateMap::const_iterator where = state_map.find(rest);
    const uint8_t target_state = where == state_map.end()
                                     ? MakeState(rest, &states, &state_map)
                                     : where->second;
    if (states[0].back().from == range.from()) {
      DCHECK_EQ(1, states[0].back().target_state);
      states[0].back().target_state = target_state;
      DCHECK_LT(range.to(), 0xFF);
      const StateRange new_range = {static_cast<uint8_t>(range.to() + 1), 1};
      states[0].push_back(new_range);
    } else {
      DCHECK_LT(range.to(), 0xFF);
      const StateRange new_range_initializer[] = {
          {range.from(), target_state},
          {static_cast<uint8_t>(range.to() + 1), 1}};
      states[0]
          .insert(states[0].end(),
                  new_range_initializer,
                  new_range_initializer + arraysize(new_range_initializer));
    }
  }
  return states;
}

// Output the generated states as a C++ table. Two tricks are used to compact
// the table: each state in the table starts with a shift value which indicates
// how many bits we can discard from the right-hand-side of the byte before
// doing the table lookup. Secondly, only the state-transitions for bytes
// with the top-bit set are included in the table; bytes without the top-bit set
// are just ASCII and are handled directly by the code.
void PrintStates(const std::vector<State>& states, FILE* stream) {
  // First calculate the start-offset of each state. This allows the state
  // machine to jump directly to the correct offset, avoiding an extra
  // indirection. State 0 starts at offset 0.
  std::vector<uint8_t> state_offset(1, 0);
  std::vector<uint8_t> shifts;
  uint8_t pos = 0;

  for (std::vector<State>::const_iterator state_it = states.begin();
       state_it != states.end();
       ++state_it) {
    // We want to set |shift| to the (0-based) index of the least-significant
    // set bit in any of the ranges for this state, since this tells us how many
    // bits we can discard and still determine what range a byte lies in. Sadly
    // it appears that ffs() is not portable, so we do it clumsily.
    uint8_t shift = 7;
    for (State::const_iterator range_it = state_it->begin();
         range_it != state_it->end();
         ++range_it) {
      while (shift > 0 && range_it->from % (1 << shift) != 0) {
        --shift;
      }
    }
    shifts.push_back(shift);
    pos += 1 + (1 << (7 - shift));
    state_offset.push_back(pos);
  }

  DCHECK_EQ(129, state_offset[1]);

  fputs(kProlog, stream);
  TablePrinter table_printer(stream);

  for (uint8_t state_index = 0; state_index < states.size(); ++state_index) {
    const uint8_t shift = shifts[state_index];
    uint8_t next_range = 0;
    uint8_t target_state = 1;
    fprintf(stream,
            "    // State %d, offset 0x%02x\n",
            static_cast<int>(state_index),
            static_cast<int>(state_offset[state_index]));
    table_printer.PrintValue(shift);
    for (int i = 0; i < 0x100; i += (1 << shift)) {
      if (next_range < states[state_index].size() &&
          states[state_index][next_range].from == i) {
        target_state = states[state_index][next_range].target_state;
        ++next_range;
      }
      if (i >= 0x80) {
        table_printer.PrintValue(state_offset[target_state]);
      }
    }
    table_printer.NewLine();
  }

  fputs(kEpilog, stream);
}

}  // namespace

int main(int argc, char* argv[]) {
  base::CommandLine::Init(argc, argv);
  logging::LoggingSettings settings;
  settings.logging_dest = logging::LOG_TO_SYSTEM_DEBUG_LOG;
  logging::InitLogging(settings);
  if (base::CommandLine::ForCurrentProcess()->HasSwitch("help")) {
    fwrite(kHelpText, 1, arraysize(kHelpText), stdout);
    exit(EXIT_SUCCESS);
  }
  base::FilePath filename =
      base::CommandLine::ForCurrentProcess()->GetSwitchValuePath("output");

  FILE* output = stdout;
  if (!filename.empty()) {
    output = base::OpenFile(filename, "wb");
    if (!output)
      PLOG(FATAL) << "Couldn't open '" << filename.AsUTF8Unsafe()
                  << "' for writing";
  }

  // Step 1: Enumerate the characters
  PairVector pairs = InitializeCharacters();
  // Step 2: Convert to sets.
  MoveAllCharsToSets(&pairs);
  if (VLOG_IS_ON(1)) {
    LogStringSets(pairs);
  }
  // Step 3: Generate states.
  std::vector<State> states = GenerateStates(pairs);
  // Step 4/5: Print output
  PrintStates(states, output);

  if (!filename.empty()) {
    if (!base::CloseFile(output))
      PLOG(FATAL) << "Couldn't finish writing '" << filename.AsUTF8Unsafe()
                  << "'";
  }

  return EXIT_SUCCESS;
}
