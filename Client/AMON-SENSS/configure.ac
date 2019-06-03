#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([AMON-SENSS], 1.1, sunshine@isi.edu)
AC_CONFIG_SRCDIR([as.cc])
AC_CONFIG_HEADERS([config.h])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

# Checks for programs.
AC_PROG_CXX
AC_PROG_CC


# Checks for libraries.
AC_SEARCH_LIBS(pthread_create,pthread)
AC_SEARCH_LIBS([get_driver_instance], [mysqlcppconn], [], [
  AC_MSG_ERROR([unable to find the get_driver_instance() function])
])
AC_SEARCH_LIBS([pcap_open_offline], [pcap], [], [
  AC_MSG_ERROR([unable to find libpcap])
])

#AC_LIB_LINKFLAGS([mysqlcppconn])	
# Checks for header files.
AC_CHECK_HEADERS(cppconn/driver.h [arpa/inet.h fcntl.h locale.h netdb.h netinet/in.h stdint.h string.h sys/socket.h sys/time.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_CHECK_HEADER_STDBOOL
AC_TYPE_INT32_T
AC_TYPE_SIZE_T

# Checks for library functions.
AC_FUNC_MALLOC
AC_FUNC_STRTOD
AC_CHECK_FUNCS([memset sqrt strcasecmp strdup strstr strtol])

AC_CONFIG_FILES(Makefile)
AC_OUTPUT
