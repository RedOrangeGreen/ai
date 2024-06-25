#include "operations.h"
#include <QDesktopServices>
#include <QUrl>
#include <QMessageBox>

QString Operation::key = "Abcd1234";

void Operation::open() {
    QString videoUrl = "https://www.youtube.com/watch?v=rPJ7BOaVg90";
    QDesktopServices::openUrl(QUrl(videoUrl));
}

void Operation::close() {
    QMessageBox::information(nullptr, "Close", "Close operation");
}

QString Operation::encode(const QString& input) {
    QString result;
    for (int i = 0; i < input.length(); ++i) {
        result += QChar(input[i].unicode() ^ key[i % key.length()].unicode());
    }
    QMessageBox::information(nullptr, "Encode", "Encoded string: " + result);
    return result;
}

QString Operation::decode(const QString& input) {
    QString result;
    for (int i = 0; i < input.length(); ++i) {
        result += QChar(input[i].unicode() ^ key[i % key.length()].unicode());
    }
    QMessageBox::information(nullptr, "Decode", "Decoded string: " + result);
    return result;
}

QString Operation::getKey() {
    return key;
}

void Operation::setKey(const QString& newKey) {
    key = newKey;
}
