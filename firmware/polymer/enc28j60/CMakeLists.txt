include(${Polymer_SOURCE_DIR}/arduino_diecimila_crosscompile.cmake)

include_directories(${Polymer_SOURCE_DIR}/arduinocore)
LINK_DIRECTORIES(${Polymer_SOURCE_DIR}/arduinocore)

link_libraries(arduinocore)

add_library (enc28j60
	enc28j60.c
)
