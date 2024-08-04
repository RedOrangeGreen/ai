#include <iostream>

class Father {
public:
    virtual void speak() {
        std::cout << "I am a father." << std::endl;
    }
};

class Son : public Father {
public:
    void speak() override {
        std::cout << "I am a son." << std::endl;
    }
};

class Daughter : public Father {
public:
    void speak() override {
        std::cout << "I am a daughter." << std::endl;
    }
};

int main() {
    Son son;
    Daughter daughter;

    son.speak();
    daughter.speak();

    return 0;
}

