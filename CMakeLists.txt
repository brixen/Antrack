cmake_minimum_required(VERSION 2.8.4)

option(test "Build all tests." OFF) # Makes boolean 'test' available.
option(VOT2015 "Build VOT2015-friendly" OFF)
option(experiments "Build all experiments." OFF) # Makes boolean 'test' available.

option(python "Build python wrappers." OFF)

option(parallel "Build parallel dataset evaluation." OFF)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY bin)

set(PROJECT_NAME Robust_tracking_by_detection)
project(${PROJECT_NAME})

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
find_package(OpenCV REQUIRED )
find_package(Armadillo REQUIRED)
find_package (Threads REQUIRED)
find_package( Boost COMPONENTS program_options filesystem system)
find_library(GLOG_LIBRARY glog)


set(PYTHON_FILES
	src/python_wrappers/tracker_python.cpp
)


FILE(GLOB TEST_FILES
	src/Tests/*.cpp
	src/Tests/*.h
	src/Tests/main.cpp
	)

set(FILTER_PRETRAINING_MAIN
	src/main_filter_pretraining.cpp
)

set(PARALLEL_MAIN
  src/main_parallel.cpp
)

set(PROJECT_MAIN
	src/main.cpp
)

set(Experiment_01
	src/Experiments/Experiment_efficient_int_kernel.cpp
	src/Experiments/Experiment_efficient_int_kernel.h
)

set(Superpixels
   src/Superpixels/helper.h
   src/Superpixels/seeds2.h
   src/Superpixels/seeds2.cpp
   src/Superpixels/Plot.h
   src/Superpixels/Plot.cpp
   src/Superpixels/SuperPixels.h
   src/Superpixels/SuperPixels.cpp
   src/Superpixels/Objectness.h
   src/Superpixels/Objectness.cpp
   )


FILE(GLOB TRAX_FILES
	src/Datasets/vot2014_trax/*.h
	src/Datasets/vot2014_trax/*.c
	src/Datasets/vot2014_trax/main.cpp
)

FILE(GLOB SOURCE_FILES
	src/Datasets/*.cpp
	src/Datasets/*.h
	src/Features/*.cpp
	src/Features/*.h
	src/Kernels/*.cpp
	src/Kernels/*.h
	src/Filter/*.cpp
	src/Filter/*.h
	src/Tracker/*.cpp
	src/Tracker/*.h
)

################################
# Testing
################################
if (test)
  # This adds another subdirectory, which has 'project(gtest)'.
  add_subdirectory(lib/gtest-1.6.0)

  enable_testing()

  # Include the gtest library. gtest_SOURCE_DIR is available due to
  # 'project(gtest)' above.
  include_directories(${gtest_SOURCE_DIR}/include ${gtest_SOURCE_DIR}
    ${Boost_INCLUDE_DIR})

  ##############
  # Unit Tests
  ##############
  add_executable(RunUnitTests ${SOURCE_FILES} ${TEST_FILES} ${Superpixels})
  #add_executable(RunUnitTests ${SOURCE_FILES})
  # Standard linking to gtest stuff.
  target_link_libraries(RunUnitTests gtest gtest_main ${OpenCV_LIBS}
    ${ARMADILLO_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} ${Boost_LIBRARIES})

  # Extra linking for the project.
  #target_link_libraries(runUnitTests project1_lib)

  # This is so you can do 'make test' to see all your tests run, instead of
  # manually running the executable runUnitTests to see those specific tests.
  #add_test(NAME that-test-I-made COMMAND RunUnitTests)

  # You can also omit NAME and COMMAND. The second argument could be some other
  # test executable.
  #add_test(that-other-test-I-made RunUnitTests)
endif()


if (experiments)
	add_executable(experiment_01_fast_intersection_kernels ${SOURCE_FILES} ${Experiment_01})
	target_link_libraries(experiment_01_fast_intersection_kernels ${OpenCV_LIBS} ${ARMADILLO_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
endif()

if(VOT2015)
	set(VOT2015_DESTINATION "../matlab/build/bin/")
	find_package( Boost COMPONENTS program_options filesystem system  REQUIRED )

	include_directories( ${Boost_INCLUDE_DIR} )
	add_executable(struck_vot2014 ${Superpixels} ${SOURCE_FILES} ${TRAX_FILES})
    target_link_libraries(struck_vot2014 ${OpenCV_LIBS} ${ARMADILLO_LIBRARIES}
      ${CMAKE_THREAD_LIBS_INIT} ${Boost_LIBRARIES})

	set_target_properties(struck_vot2014 PROPERTIES
				RUNTIME_OUTPUT_DIRECTORY ${VOT2015_DESTINATION})
endif()





if(python)
	set(PYTHON_DESTINATION "../python/Tracker_wrapper/")
    find_package( Boost COMPONENTS python)
	find_package(PythonLibs)

	set(PYTHON_INCLUDE_DIRS /usr/local/Cellar/python/2.7.10_2/Frameworks/Python.framework/Versions/2.7/Headers)
	set(pyconfig /usr/local/Cellar/python/2.7.10_2/Frameworks/Python.framework/Versions/2.7/include/python2.7)
	set(PYTHON_LIBRARIES /usr/local/Cellar/python/2.7.10_2/Frameworks/Python.framework/Versions/2.7/lib/libpython2.7.dylib)


	include_directories (${Boost_INCLUDE_DIRS} ${pyconfig})

	PYTHON_ADD_MODULE(struck_tracker ${SOURCE_FILES} ${PYTHON_FILES} ${Superpixels})
target_link_libraries(struck_tracker
    boost_python
    ${PYTHON_LIBRARIES}
    ${Boost_LIBRARIES}
	${OpenCV_LIBS}
	${ARMADILLO_LIBRARIES}
	${CMAKE_THREAD_LIBS_INIT}

	)
	set_target_properties(struck_tracker PROPERTIES
				LIBRARY_OUTPUT_DIRECTORY ${PYTHON_DESTINATION})

	#FILE(COPY Antrack.so DESTINATION ${PYTHON_DESTINATION})
endif()



find_package( Boost COMPONENTS filesystem system REQUIRED )
add_executable(robust_struck_tracker_v1.0 ${Superpixels} ${SOURCE_FILES} ${PROJECT_MAIN})



include_directories(${OpenCV_INCLUDE_DIRS} )
include_directories(${ARMADILLO_INCLUDE_DIRS})
include_directories (${Boost_INCLUDE_DIRS})
target_link_libraries(robust_struck_tracker_v1.0 ${OpenCV_LIBS}
  ${ARMADILLO_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT}
    ${Boost_LIBRARIES} ${GLOG_LIBRARY} )


if (parallel)


	find_package( Boost COMPONENTS program_options filesystem system  REQUIRED )

	include_directories( ${Boost_INCLUDE_DIR} )

  	#add_executable(parallel_main ${Superpixels} ${SOURCE_FILES} ${PARALLEL_MAIN})
	#target_link_libraries(parallel_main ${Boost_LIBRARIES} ${OpenCV_LIBS} ${ARMADILLO_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})

	add_executable(struck_filter_experiments ${Superpixels} ${SOURCE_FILES} ${FILTER_PRETRAINING_MAIN})
	target_link_libraries(struck_filter_experiments ${Boost_LIBRARIES} ${OpenCV_LIBS} ${ARMADILLO_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
endif()
