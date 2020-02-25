import functools
from flask import Flask, request, jsonify
from thsauto import ThsAuto
import time
import sys
import threading

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

auto = ThsAuto()

lock = threading.Lock()
next_time = 0
interval = 0.5
def interval_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global interval
        global lock
        global next_time
        lock.acquire()
        now = time.time()
        if now < next_time:
            time.sleep(next_time - now)
        try:
            rt = func(*args, **kwargs)
        except Exception as e:
            rt = ({'code': 1, 'status': 'failed', 'msg': '{}'.format(e)}, 400)
        next_time = time.time() + interval
        lock.release()
        return rt
    return wrapper

@app.route('/thsauto/balance', methods = ['GET'])
@interval_call
def get_balance():
    result = auto.get_balance()
    return jsonify(result), 200

@app.route('/thsauto/position', methods = ['GET'])
@interval_call
def get_position():
    result = auto.get_position()
    return jsonify(result), 200

@app.route('/thsauto/orders/active', methods = ['GET'])
@interval_call
def get_active_orders():
    result = auto.get_active_orders()
    return jsonify(result), 200

@app.route('/thsauto/orders/filled', methods = ['GET'])
@interval_call
def get_filled_orders():
    result = auto.get_filled_orders()
    return jsonify(result), 200

@app.route('/thsauto/sell', methods = ['GET'])
@interval_call
def sell():
    stock = request.args['stock_no']
    amount = request.args['amount']
    price = request.args.get('price', None)
    if price is not None:
        price = float(price)
    result = auto.sell(stock_no=stock, amount=int(amount), price=price)
    return jsonify(result), 200

@app.route('/thsauto/buy', methods = ['GET'])
@interval_call
def buy():
    stock = request.args['stock_no']
    amount = request.args['amount']
    price = request.args.get('price', None)
    if price is not None:
        price = float(price)
    result = auto.buy(stock_no=stock, amount=int(amount), price=price)
    return jsonify(result), 200

@app.route('/thsauto/cancel', methods = ['GET'])
@interval_call
def cancel():
    entrust_no = request.args['entrust_no']
    result = auto.cancel(entrust_no=entrust_no)
    return jsonify(result), 200

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    app.run(host=host, port=port)