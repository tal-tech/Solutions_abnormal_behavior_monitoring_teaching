cmake_minimum_required(VERSION 3.10)

set(SERVICE_NAME cppservice_ch)

project(${SERVICE_NAME})

set (CPP_SERVICE_MAJOR_VERSION 0)
set (CPP_SERVICE_MINOR_VERSION 8)
set (CPP_SERVICE_PATCH_VERSION 1)
set (CPP_SERVICE_VERSION ${CPP_SERVICE_MAJOR_VERSION}.${CPP_SERVICE_MINOR_VERSION}.${CPP_SERVICE_PATCH_VERSION})

set(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}/package")

######################################################################
#全局编译标志
######################################################################

SET (CMAKE_EXE_LINKER_FLAGS
    "${CMAKE_EXE_LINKER_FLAGS} -Wl,-rpath,$ORIGIN/../lib" )

SET (CMAKE_SHARED_LINKER_FLAGS
    "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-rpath,$ORIGIN/../lib" )

set(CMAKE_SKIP_BUILD_RPATH TRUE)

set(BUILD_SHARED_LIBS ON)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -fPIC -fsanitize-address-use-after-scope")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=bounds-strict")

set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0")

set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -g")

######################################################################
#全局链接和包含
######################################################################
#[[
find_package(Boost REQUIRED)
if (Boost_FOUND)
   include_directories(${Boost_INCLUDE_DIRS})
endif()]]#
# include_directories(${CMAKE_SOURCE_DIR}/boost/boost_1_65_1/include)
# link_directories(${CMAKE_SOURCE_DIR}/boost/boost_1_65_1/lib)
#include_directories(${CMAKE_SOURCE_DIR}/proto)

#link_directories(${PROJECT_SOURCE_DIR}/kafka/cppkafka/lib)
#link_directories(${PROJECT_SOURCE_DIR}/ffmpeg/lib)
#link_directories(${PROJECT_SOURCE_DIR}/proto/libs)
#link_directories(alg/lib)
#link_directories(alg/third_party)
#link_directories(${PROJECT_SOURCE_DIR}/lib)
include_directories(${PROJECT_SOURCE_DIR}/include)
file(GLOB TAlASR_LIB ${PROJECT_SOURCE_DIR}/lib/lib*.*)
#################################################################L#####
#全局编译输出指定
######################################################################

IF(CMAKE_BUILD_TYPE MATCHES Debug)
set(CMAKE_VERBOSE_MAKEFILE ON)
ENDIF(CMAKE_BUILD_TYPE MATCHES Debug)

string(TOLOWER ${CMAKE_BUILD_TYPE} BUILD_TYPE)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/debug/lib/${BUILD_TYPE})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/debug/lib/${BUILD_TYPE})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/debug/bin/${BUILD_TYPE})


######################################################################
#子工程目录
######################################################################

#add_subdirectory(breakpad)
add_subdirectory(chrome-base)
#add_subdirectory(configer)
#add_subdirectory(curl-tool)
#add_subdirectory(hiredis)
#add_subdirectory(grpc)
#add_subdirectory(ffmpeg)
#add_subdirectory(jsoncpp)
#add_subdirectory(kafka)
#add_subdirectory(datawork-file-trans)
#add_subdirectory(mysql)
#add_subdirectory(service-common)
#add_subdirectory(service-custom)
#add_subdirectory(service-http-custom)
#add_subdirectory(service-websocket-custom)
#add_subdirectory(websocket)

######################################################################
#算法sdk编译对象
######################################################################



######################################################################
#http service编译对象
######################################################################

#file(GLOB ALG_LIBS ${PROJECT_SOURCE_DIR}/alg/lib/libtlvasr.so
#file(GLOB ALG_LIBS
#    ${PROJECT_SOURCE_DIR}/alg/third_party/*)

#add_executable(http_service
#    http-service-main.cpp
#    )
add_executable(main
    main.cpp)
#[[
if(Boost_FOUND)
   target_link_libraries(main ${Boost_LIBRARIES})
endif()
]]#
target_link_libraries(main
    base
    pthread
    ${TAlASR_LIB}
    #breakpad_client
    #hiredis
    #service-http-custom
    #boost_system
    #${ALG_LIBS}
    #tlvasr
    #mask_cuda_backend
    #protobuf
    )

######################################################################
#websocket service编译对象
######################################################################

#add_executable(ws_service
#    ws-service-main.cpp)
#
##add_dependencies(ws_service websocketpp)
#
#target_link_libraries(ws_service
#    breakpad_client
#    service-websocket-custom
#    ${Boost_LIBRARIES})

######################################################################
#程序发布设置
######################################################################

install(DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/ DESTINATION bin)
install(DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/ DESTINATION lib)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/kafka/cppkafka/lib/ DESTINATION lib)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/proto/libs/ DESTINATION lib)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/alg/resource/ DESTINATION bin/res)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/alg/lib/ DESTINATION lib)
install(DIRECTORY ${CMAKE_SOURCE_DIR}/alg/third_party/ DESTINATION lib)
install(DIRECTORY config/ DESTINATION bin/config)
