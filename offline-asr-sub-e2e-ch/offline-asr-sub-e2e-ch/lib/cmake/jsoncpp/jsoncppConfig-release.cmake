#----------------------------------------------------------------
# Generated CMake target import file for configuration "release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "jsoncpp_lib" for configuration "release"
set_property(TARGET jsoncpp_lib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(jsoncpp_lib PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libjsoncpp.so.1.9.2"
  IMPORTED_SONAME_RELEASE "libjsoncpp.so.22"
  )

list(APPEND _IMPORT_CHECK_TARGETS jsoncpp_lib )
list(APPEND _IMPORT_CHECK_FILES_FOR_jsoncpp_lib "${_IMPORT_PREFIX}/lib/libjsoncpp.so.1.9.2" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
