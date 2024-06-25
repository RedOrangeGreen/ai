QT += core gui widgets

TARGET = build/encapp
TEMPLATE = app

SOURCES += \
    main.cpp \
    operations.cpp

HEADERS += \
    operations.h

# Create the build directory if it doesn't exist
!exists($$OUT_PWD/build) {
    mkpath($$OUT_PWD/build)
}
