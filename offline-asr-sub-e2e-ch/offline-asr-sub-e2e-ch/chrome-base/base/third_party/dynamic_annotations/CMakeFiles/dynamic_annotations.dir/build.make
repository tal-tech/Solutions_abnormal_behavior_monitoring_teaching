# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.23

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Produce verbose output by default.
VERBOSE = 1

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/local/bin/cmake

# The command to remove a file.
RM = /usr/local/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/chenhongwei/workspace/offline-asr-sub-e2e-ch

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/chenhongwei/workspace/offline-asr-sub-e2e-ch

# Include any dependencies generated for this target.
include chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/compiler_depend.make

# Include the progress variables for this target.
include chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/progress.make

# Include the compile flags for this target's objects.
include chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/flags.make

chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.o: chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/flags.make
chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.o: chrome-base/base/third_party/dynamic_annotations/dynamic_annotations.c
chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.o: chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/chenhongwei/workspace/offline-asr-sub-e2e-ch/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building C object chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.o"
	cd /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.o -MF CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.o.d -o CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.o -c /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations/dynamic_annotations.c

chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.i"
	cd /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations/dynamic_annotations.c > CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.i

chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.s"
	cd /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations && /usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations/dynamic_annotations.c -o CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.s

# Object files for target dynamic_annotations
dynamic_annotations_OBJECTS = \
"CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.o"

# External object files for target dynamic_annotations
dynamic_annotations_EXTERNAL_OBJECTS =

debug/lib/debug/libdynamic_annotations.a: chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/dynamic_annotations.c.o
debug/lib/debug/libdynamic_annotations.a: chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/build.make
debug/lib/debug/libdynamic_annotations.a: chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/chenhongwei/workspace/offline-asr-sub-e2e-ch/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking C static library ../../../../debug/lib/debug/libdynamic_annotations.a"
	cd /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations && $(CMAKE_COMMAND) -P CMakeFiles/dynamic_annotations.dir/cmake_clean_target.cmake
	cd /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/dynamic_annotations.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/build: debug/lib/debug/libdynamic_annotations.a
.PHONY : chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/build

chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/clean:
	cd /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations && $(CMAKE_COMMAND) -P CMakeFiles/dynamic_annotations.dir/cmake_clean.cmake
.PHONY : chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/clean

chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/depend:
	cd /home/chenhongwei/workspace/offline-asr-sub-e2e-ch && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/chenhongwei/workspace/offline-asr-sub-e2e-ch /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations /home/chenhongwei/workspace/offline-asr-sub-e2e-ch /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations /home/chenhongwei/workspace/offline-asr-sub-e2e-ch/chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : chrome-base/base/third_party/dynamic_annotations/CMakeFiles/dynamic_annotations.dir/depend

