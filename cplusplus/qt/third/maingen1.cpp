#include <QApplication>
#include <QMainWindow>
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QPushButton>
#include <QMessageBox>
#include "operations.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    // Initialize variables
    QString message = "This is a message 123";
    QString encoded = "";

    // Create the main window
    QMainWindow window;
    window.setWindowTitle("Hello World");
    window.resize(500, 400);

    // Create the menu bar
    QMenuBar *menuBar = window.menuBar();
    QMenu *fileMenu = menuBar->addMenu("&File");
    QAction *openAction = new QAction("&Open", &window);
    fileMenu->addAction(openAction);
    QObject::connect(openAction, &QAction::triggered, &Operation::open);

    QAction *closeAction = new QAction("&Close", &window);
    fileMenu->addAction(closeAction);
    QObject::connect(closeAction, &QAction::triggered, &Operation::close);

    QAction *encodeAction = new QAction("&Encode", &window);
    fileMenu->addAction(encodeAction);
    QObject::connect(encodeAction, &QAction::triggered, [&]() {
        encoded = Operation::encode(message);
    });

    QAction *decodeAction = new QAction("&Decode", &window);
    fileMenu->addAction(decodeAction);
    QObject::connect(decodeAction, &QAction::triggered, [&]() {
        Operation::decode(encoded);
    });

    QAction *exitAction = new QAction("&Exit", &window);
    exitAction->setShortcut(Qt::CTRL | Qt::Key_Q);
    fileMenu->addAction(exitAction);
    QObject::connect(exitAction, &QAction::triggered, &QApplication::quit);

    // Create the "Press me" button
    QPushButton *button = new QPushButton("Press me", &window);
    button->setGeometry(200, 150, 100, 30);

    // Connect the button's clicked signal to a lambda function
    QObject::connect(button, &QPushButton::clicked, [&]() {
        QMessageBox messageBox;
        messageBox.setText("The button has been pressed");
        messageBox.exec();
    });

    window.show();
    return app.exec();
}
