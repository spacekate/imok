include(${ArduinoCode_SOURCE_DIR}/arduino_diecimila_crosscompile.cmake)

include_directories(${ArduinoCode_SOURCE_DIR}/libarduinocore)
LINK_DIRECTORIES(${ArduinoCode_SOURCE_DIR}/libarduinocore)

include_directories(${ArduinoCode_SOURCE_DIR}/etherShield)
LINK_DIRECTORIES(${ArduinoCode_SOURCE_DIR}/etherShield)

link_libraries(arduinocore)
link_libraries(etherShield)

add_executable(imok_enc28j60 imok_enc28j60.cc)
