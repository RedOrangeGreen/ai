#ifndef OPERATIONS_H
#define OPERATIONS_H

#include <QString>

class Operation {
public:
    static void open();
    static void close();
    static QString encode(const QString& input);
    static QString decode(const QString& input);

    static QString getKey();
    static void setKey(const QString& newKey);

private:
    static QString key;
};

#endif // OPERATIONS_H
