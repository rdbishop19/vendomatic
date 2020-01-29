from flask import Flask, request, jsonify

app = Flask(__name__)

# this is a first go at this without implementing SQLite or any other database
class VendoMatic:
    def __init__(self):
        self.coins = 0
        self.transaction_coins = 0
        self.inventory = [5, 5, 5]
        self.price_coin_quantity = 2
        self.max_items_vended = 1

# this is our trusty vending machine at Goodyear Tire
machine = VendoMatic()

## ACCEPT OR RETURN COINS FROM MACHINE
@app.route('/', methods = ["PUT", "DELETE"])
def handle_coins():
    if request.method == "PUT":
        
        data = request.get_json(force=True)
        resp = jsonify(data)
        machine.transaction_coins += int(data["coin"])
        resp.status_code = 204
        resp.headers['X-Coins'] = machine.transaction_coins

        return resp

    elif request.method == "DELETE":

        coins_returned = machine.transaction_coins
        machine.transaction_coins = 0
        resp = jsonify()
        resp.headers['X-Coins'] = coins_returned
        resp.status_code = 204

        return resp

## GETS INVENTORY FROM MACHINE
@app.route('/inventory', methods = ["GET"])
def get_inventory_array():

    data = machine.inventory
    resp = jsonify(data)
    resp.status_code = 200

    return resp

## SINGLE ITEM INVENTORY // TRANSACTION LOGIC
@app.route('/inventory/<int:inventory_id>', methods = ["GET", "PUT"])
def inventory(inventory_id):

    # Deciding to have the index start at 1 for the user's URL parameters
    index = inventory_id - 1

    # GET SINGLE ITEM INVENTORY
    if request.method == "GET":
        # only allows the user to check for properly indexed inventory items
        if inventory_id > 0 and inventory_id < len(machine.inventory) + 1:
            data = machine.inventory[index]
            resp = jsonify(data)
            resp.status_code = 200
        else:
            return not_found()

    # TRANSACTION LOGIC
    elif request.method == "PUT":
        # ENOUGH COINS FOR TRANSACTION
        if machine.transaction_coins >= machine.price_coin_quantity:
            # ITEM AVAILABLE - return extra transaction coins to user; deposit payment into machine
            if machine.inventory[index] > 0:

                returned_coins = machine.transaction_coins - machine.price_coin_quantity
                machine.coins += machine.price_coin_quantity 
                machine.transaction_coins = 0   # reset 
                machine.inventory[index] -= 1
                # 'quantity' needs to be a dynamic variable according to constraints
                data = {
                    "quantity": machine.max_items_vended,
                }
                resp = jsonify(data)
                resp.headers['X-Coins'] = returned_coins
                resp.headers['X-Inventory-Remaining'] = machine.inventory[index]
                resp.status_code = 200

            # ITEM OUT OF STOCK - return current number of transaction coins
            else:
                resp = jsonify()
                resp.headers['X-Coins'] = machine.transaction_coins
                resp.status_code = 404

        # PURCHASE ATTEMPT WITH ITEM AVAILABLE BUT INSUFFICIENT # OF COINS
        else:
            resp = jsonify()
            resp.status_code = 403
            resp.headers['X-Coins'] = machine.transaction_coins

    return resp

## PRINT CUSTOM 404 MESSAGE
@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

if __name__ == '__main__':
    app.run()