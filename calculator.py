from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def calculator():
    operand1 = int(request.args.get('operand1'))
    operand2 = int(request.args.get('operand2'))
    operator = request.args.get('operator')

    if operator == '+':
        result = operand1 + operand2
    elif operator == '-':
        result = operand1 - operand2
    elif operator == '*':
        result = operand1 * operand2
    elif operator == '/':
        result = operand1 / operand2
    else:
        return 'Invalid operator'

    return f'The result is: {result}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
