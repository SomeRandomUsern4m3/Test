wallet_context = object
class Wallet(object):
    def __init__(self, starter_money):
        self.money = starter_money
    def add_money(self, amount):
        """To remove money just add a negative number"""
        self.money += amount
    def set_money(self, value):
        self.money = value
def create_wallet(amount):
    global wallet_context
    wallet_context = Wallet(amount)
def get_wallet_context():
    global wallet_context
    return wallet_context