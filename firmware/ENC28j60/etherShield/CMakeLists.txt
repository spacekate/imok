include(${ArduinoCode_SOURCE_DIR}/arduino_diecimila_crosscompile.cmake)

include_directories(${ArduinoCode_SOURCE_DIR}/libarduinocore)
LINK_DIRECTORIES(${ArduinoCode_SOURCE_DIR}/libarduinocore)

link_libraries(arduinocore)



add_library (etherShield
	enc28j60.c
	etherShield.cpp
	ip_arp_udp_tcp.c
)
