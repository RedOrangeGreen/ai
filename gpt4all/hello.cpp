#include <iostream> // Include directive for input/output stream.
#include <climits> 
using namespace std;  // Using statement to avoid typing 'std::' before cout and endl.

class Calculator {
public:
    int add(int a, int b) const {
        return (a + b);
    }
    
    int sub(int a, int b) const {
        if (b != 0) // To avoid division by zero error.
            return (a - b);
        else
            cout << "Error: Cannot subtract from zero." << endl;
        
        return INT_MIN; // Returning the minimum integer value as an indication of failure in this context.
    }
};

int main() {
    Calculator calc;  // Creating a 'Calculator' object named 'calc'.
    
    int resultAdd = calc.add(5, 3);   // Adding two numbers using the add method.
    cout << "Result of addition: " << resultAdd << endl;
    
    int resultSubtract = calc.sub(10, -2);  // Subtracting one number from another with a negative operand.
    cout << "Result of subtraction (with negation): " << resultSubtract << endl;
    
    return 0; // Return value indicating successful execution.
}
