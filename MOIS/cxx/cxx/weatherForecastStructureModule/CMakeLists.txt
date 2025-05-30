file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

set(INFERENCE_MODULE_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../scl-machine/problem-solver/cxx/inferenceModule")


include_directories(${CMAKE_CURRENT_LIST_DIR} ${SC_MEMORY_SRC} ${SC_KPM_SRC} ${INFERENCE_MODULE_DIR})

add_library (weatherForecastStructureModule SHARED ${SOURCES})


target_link_libraries(weatherForecastStructureModule sc-memory sc-agents-common inferenceModule) 


sc_codegen_ex(weatherForecastStructureModule ${CMAKE_CURRENT_LIST_DIR} ${CMAKE_CURRENT_LIST_DIR}/generated)