include(${Polymer_SOURCE_DIR}/arduino_diecimila_crosscompile.cmake)

include_directories(${Polymer_SOURCE_DIR}/arduinocore)
LINK_DIRECTORIES(${Polymer_SOURCE_DIR}/arduinocore)

include_directories(${Polymer_SOURCE_DIR}/enc28j60)
LINK_DIRECTORIES(${Polymer_SOURCE_DIR}/enc28j60)

include_directories(${Polymer_SOURCE_DIR}/polymer)
LINK_DIRECTORIES(${Polymer_SOURCE_DIR}/polymer)

link_libraries(arduinocore)
link_libraries(enc28j60)
link_libraries(polymer)

add_executable(webclient webclient.cc)
